import os
import tweepy

TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_SECRET = os.environ["TWITTER_API_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = os.environ["TWITTER_ACCESS_SECRET"]


def compose_tweet(weather: dict, time_of_day: str) -> str:
    """
    Build a tweet from parsed weather data.
    time_of_day: "morning" or "evening"
    """
    w = weather

    if time_of_day == "morning":
        greeting = "Good morning, Cape Town!"
        closing_options = [
            "Stay hydrated and drive safe. 🚗",
            "Have a wonderful day ahead. 🌈",
            "Get out there and enjoy it. 🤙",
        ]
        # Pick closing based on temp to add a little variety
        if w["temp"] >= 28:
            closing = "Stay cool and drink plenty of water. 💧"
        elif w["temp"] <= 12:
            closing = "Grab a jacket before you head out. 🧥"
        else:
            closing = closing_options[w["temp"] % len(closing_options)]
    else:
        greeting = "Good evening, Cape Town!"
        if w["temp"] >= 25:
            closing = "Perfect evening for a sundowner. 🥂"
        elif w["temp"] <= 12:
            closing = "Cosy night ahead — stay warm. 🔥"
        else:
            closing = "Hope your day was a good one. 🌅"

    tweet = (
        f"{w['emoji']} {greeting}\n\n"
        f"🌡️ {w['temp']}°C (feels like {w['feels_like']}°C)\n"
        f"🌬️ {w['wind_dir']} winds at {w['wind_speed']} km/h\n"
        f"💧 Humidity: {w['humidity']}%\n"
        f"☁️ {w['description']}\n\n"
        f"{closing}\n\n"
        f"#CapeTown #WeatherZA #CTWeather"
    )

    # X has a 280 char limit — truncate gracefully if ever needed
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
