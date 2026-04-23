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
