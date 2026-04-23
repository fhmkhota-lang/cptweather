import os
import requests
from datetime import datetime, timezone

OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]

# Cape Town coordinates
LAT = -33.9249
LON = 18.4241
CITY = "Cape Town"


def get_weather() -> dict:
    """Fetch current weather for Cape Town from OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_forecast() -> dict:
    """Fetch 5-day forecast from OWM. Returns rain alert and weekend forecast data."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "cnt": 40,  # 5 days x 8 (3-hour intervals)
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def check_rain_soon(forecast_data: dict) -> str | None:
    """Check if rain is expected in the next 6 hours. Returns warning string or None."""
    if not forecast_data:
        return None
    now = datetime.now(tz=timezone.utc)
    for item in forecast_data.get("list", []):
        item_time = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        hours_ahead = (item_time - now).total_seconds() / 3600
        if 0 <= hours_ahead <= 6:
            condition_id = item["weather"][0]["id"]
            if condition_id < 700:  # Rain, drizzle or thunderstorm
                desc = item["weather"][0]["description"]
                hour_sast = (item_time.hour + 2) % 24
                return f"🌧️ Rain expected around {hour_sast:02d}:00 ({desc}) — grab a brolly!"
    return None


def get_weekend_forecast(forecast_data: dict) -> list | None:
    """Extract Sat/Sun/Mon daily summaries for the weekend forecast tweet."""
    if not forecast_data:
        return None

    from collections import defaultdict
    daily = defaultdict(list)

    for item in forecast_data.get("list", []):
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        date_key = dt.date()
        daily[date_key].append(item)

    today = datetime.now(tz=timezone.utc).date()
    days = sorted(daily.keys())

    results = []
    for day in days:
        if day <= today:
            continue
        items = daily[day]
        temps = [i["main"]["temp"] for i in items]
        conditions = [i["weather"][0]["id"] for i in items]
        descriptions = [i["weather"][0]["description"] for i in items]

        # Pick most severe condition of the day
        min_cond = min(conditions)
        idx = conditions.index(min_cond)
        desc = descriptions[idx].capitalize()

        if min_cond < 300:
            emoji = "⛈️"
        elif min_cond < 600:
            emoji = "🌧️"
        elif min_cond < 800:
            emoji = "🌫️"
        elif min_cond == 800:
            emoji = "☀️"
        else:
            emoji = "⛅"

        results.append({
            "date": day,
            "day_name": day.strftime("%A"),
            "min": round(min(temps)),
            "max": round(max(temps)),
            "desc": desc,
            "emoji": emoji,
        })

        if len(results) == 3:
            break

    return results if results else None


def check_fire_danger(weather: dict) -> str | None:
    """Return a fire danger warning if conditions are dangerous."""
    temp = weather["temp"]
    humidity = weather["humidity"]
    wind_speed = weather["wind_speed"]

    if temp >= 35 and humidity <= 30 and wind_speed >= 30:
        return "🔥 EXTREME fire danger — hot, dry & windy conditions. Be vigilant!"
    elif temp >= 30 and humidity <= 40 and wind_speed >= 20:
        return "🔥 High fire danger today — avoid open flames outdoors."
    return None


def get_uv_index() -> float:
    """Fetch current UV index from OWM One Call API."""
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": OPENWEATHER_API_KEY,
        "exclude": "minutely,hourly,daily,alerts",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("current", {}).get("uvi", None)
    except Exception:
        return None


def parse_weather(data: dict) -> dict:
    """Extract the fields we care about."""
    weather = data["weather"][0]
    main = data["main"]
    wind = data["wind"]
    sys = data.get("sys", {})

    # Map OWM condition codes to emojis
    condition_id = weather["id"]
    if condition_id < 300:
        emoji = "⛈️"   # Thunderstorm
    elif condition_id < 400:
        emoji = "🌦️"   # Drizzle
    elif condition_id < 600:
        emoji = "🌧️"   # Rain
    elif condition_id < 700:
        emoji = "❄️"   # Snow
    elif condition_id < 800:
        emoji = "🌫️"   # Atmosphere (fog/mist)
    elif condition_id == 800:
        emoji = "☀️"   # Clear
    elif condition_id == 801:
        emoji = "🌤️"   # Few clouds
    elif condition_id <= 803:
        emoji = "⛅"   # Scattered/broken clouds
    else:
        emoji = "☁️"   # Overcast

    # Wind direction from degrees
    deg = wind.get("deg", 0)
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    wind_dir = directions[round(deg / 45) % 8]

    wind_speed = round(wind.get("speed", 0) * 3.6)  # m/s → km/h

    # Cape Doctor warning (strong SE wind)
    cape_doctor = wind_dir in ("SE", "S", "SSE") and wind_speed >= 40

    # Clothing tip based on temperature
    temp = round(main["temp"])
    if temp >= 30:
        clothing_tip = "🩴 Very hot — shorts and sunscreen weather!"
    elif temp >= 25:
        clothing_tip = "😎 T-shirt weather — enjoy the warmth!"
    elif temp >= 20:
        clothing_tip = "👕 Light layers should do the trick."
    elif temp >= 15:
        clothing_tip = "🧥 Bring a light jacket just in case."
    elif temp >= 10:
        clothing_tip = "🧣 Jacket and scarf recommended today."
    else:
        clothing_tip = "🧤 Bundle up — it's cold out there!"

    # Sunrise / sunset (UTC timestamps → SAST = UTC+2)
    sunrise_utc = sys.get("sunrise")
    sunset_utc = sys.get("sunset")

    def fmt_time(ts):
        if ts is None:
            return None
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        sast_hour = (dt.hour + 2) % 24
        return f"{sast_hour:02d}:{dt.minute:02d}"

    return {
        "emoji": emoji,
        "description": weather["description"].capitalize(),
        "temp": temp,
        "feels_like": round(main["feels_like"]),
        "humidity": main["humidity"],
        "wind_speed": wind_speed,
        "wind_dir": wind_dir,
        "cape_doctor": cape_doctor,
        "clothing_tip": clothing_tip,
        "sunrise": fmt_time(sunrise_utc),
        "sunset": fmt_time(sunset_utc),
    }


def get_week_ahead(forecast_data: dict) -> list | None:
    """Extract Mon–Fri daily summaries for the Sunday week-ahead tweet."""
    if not forecast_data:
        return None

    from collections import defaultdict
    daily = defaultdict(list)

    for item in forecast_data.get("list", []):
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        daily[dt.date()].append(item)

    today = datetime.now(tz=timezone.utc).date()
    days = sorted(k for k in daily.keys() if k > today)[:5]

    results = []
    for day in days:
        items = daily[day]
        temps = [i["main"]["temp"] for i in items]
        conditions = [i["weather"][0]["id"] for i in items]
        descriptions = [i["weather"][0]["description"] for i in items]

        # Most severe condition of the day
        min_cond = min(conditions)
        idx = conditions.index(min_cond)
        desc = descriptions[idx].capitalize()

        if min_cond < 300:
            emoji = "⛈️"
        elif min_cond < 600:
            emoji = "🌧️"
        elif min_cond < 800:
            emoji = "🌫️"
        elif min_cond == 800:
            emoji = "☀️"
        else:
            emoji = "⛅"

        results.append({
            "day_name": day.strftime("%A"),
            "min": round(min(temps)),
            "max": round(max(temps)),
            "desc": desc,
            "emoji": emoji,
        })

    return results if results else None
