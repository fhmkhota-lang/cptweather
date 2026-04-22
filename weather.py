import os
import requests

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


def parse_weather(data: dict) -> dict:
    """Extract the fields we care about."""
    weather = data["weather"][0]
    main = data["main"]
    wind = data["wind"]

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

    return {
        "emoji": emoji,
        "description": weather["description"].capitalize(),
        "temp": round(main["temp"]),
        "feels_like": round(main["feels_like"]),
        "humidity": main["humidity"],
        "wind_speed": round(wind.get("speed", 0) * 3.6),  # m/s → km/h
        "wind_dir": wind_dir,
    }
