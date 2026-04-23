import os
import tweepy

TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_SECRET = os.environ["TWITTER_API_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = os.environ["TWITTER_ACCESS_SECRET"]


def uv_label(uv: float) -> str:
    """Return a human-readable UV label and advice."""
    if uv is None:
        return None
    if uv < 3:
        return f"🟢 UV Index: {uv:.0f} (Low)"
    elif uv < 6:
        return f"🟡 UV Index: {uv:.0f} (Moderate) — wear SPF"
    elif uv < 8:
        return f"🟠 UV Index: {uv:.0f} (High) — sunscreen essential"
    elif uv < 11:
        return f"🔴 UV Index: {uv:.0f} (Very High) — limit sun exposure"
    else:
        return f"🟣 UV Index: {uv:.0f} (Extreme) — avoid midday sun!"


def compose_tweet(weather: dict, time_of_day: str, uv: float = None,
                  rain_alert: str = None, fire_warning: str = None) -> str:
    """Build a tweet from parsed weather data."""
    w = weather

    if time_of_day == "morning":
        greeting = "Good morning, Cape Town!"
        sun_line = f"🌅 Sunrise: {w['sunrise']}\n" if w.get("sunrise") else ""
        uv_line = f"{uv_label(uv)}\n" if uv is not None else ""
    else:
        greeting = "Good evening, Cape Town!"
        sun_line = f"🌇 Sunset: {w['sunset']}\n" if w.get("sunset") else ""
        uv_line = ""

    wind_warning = "💨 The Cape Doctor is blowing — hold onto your hat!\n" if w["cape_doctor"] else ""
    rain_line = f"{rain_alert}\n" if rain_alert else ""
    fire_line = f"{fire_warning}\n" if fire_warning else ""

    tweet = (
        f"{w['emoji']} {greeting}\n\n"
        f"🌡️ {w['temp']}°C (feels like {w['feels_like']}°C)\n"
        f"🌬️ {w['wind_dir']} winds at {w['wind_speed']} km/h\n"
        f"💧 Humidity: {w['humidity']}%\n"
        f"☁️ {w['description']}\n"
        f"{sun_line}"
        f"{uv_line}"
        f"{wind_warning}"
        f"{rain_line}"
        f"{fire_line}\n"
        f"{w['clothing_tip']}\n\n"
        f"#CapeTown #WeatherZA #CTWeather"
    )

    # Trim optional lines if over 280 chars, least important first
    for optional in [fire_line, wind_warning, rain_line, uv_line]:
        if len(tweet) <= 280:
            break
        if optional:
            tweet = tweet.replace(optional, "")

    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    return tweet


def compose_weekend_tweet(forecast: list) -> str:
    """Build a Friday weekend forecast tweet from 3-day forecast data."""
    lines = ["🗓️ Weekend forecast for Cape Town:\n"]
    for day in forecast:
        lines.append(
            f"{day['emoji']} {day['day_name']}: {day['min']}–{day['max']}°C, {day['desc']}"
        )
    lines.append("\nPlan your weekend accordingly! 🤙")
    lines.append("\n#CapeTown #WeatherZA #CTWeekend")

    tweet = "\n".join(lines)
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    return tweet


def post_tweet(text: str) -> str:
    """Post a tweet via the X API v2 and return the tweet ID."""
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
    )
    response = client.create_tweet(text=text)
    return response.data["id"]
