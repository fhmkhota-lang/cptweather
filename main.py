import sys
from datetime import datetime, timezone
from weather import (
    get_weather, parse_weather, get_uv_index,
    get_forecast, check_rain_soon, get_weekend_forecast,
    check_fire_danger, get_week_ahead, get_all_beach_data
)
from tweet import compose_tweet, compose_weekend_tweet, compose_week_ahead_tweet, compose_beach_tweet, post_tweet


def is_friday_evening():
    now = datetime.now(tz=timezone.utc)
    return now.weekday() == 4  # Friday


def is_sunday_morning():
    now = datetime.now(tz=timezone.utc)
    return now.weekday() == 6  # Sunday


def main():
    # Expect one argument: "morning" or "evening"
    if len(sys.argv) < 2 or sys.argv[1] not in ("morning", "evening"):
        print("Usage: python main.py [morning|evening]")
        sys.exit(1)

    time_of_day = sys.argv[1]

    print(f"Fetching Cape Town weather for {time_of_day} post...")
    raw = get_weather()
    weather = parse_weather(raw)
    print(f"Weather: {weather['temp']}°C, {weather['description']}")
    print(f"Wind: {weather['wind_dir']} at {weather['wind_speed']} km/h — Cape Doctor: {weather['cape_doctor']}")
    print(f"Sunrise: {weather['sunrise']} | Sunset: {weather['sunset']}")

    # Fetch forecast data (used for rain alert + weekend forecast)
    print("Fetching forecast data...")
    forecast_data = get_forecast()

    # Rain alert
    rain_alert = check_rain_soon(forecast_data)
    print(f"Rain alert: {rain_alert}")

    # Fire danger
    fire_warning = check_fire_danger(weather)
    print(f"Fire danger: {fire_warning}")

    # UV index (morning only)
    uv = None
    if time_of_day == "morning":
        uv = get_uv_index()
        print(f"UV Index: {uv}")

    # Compose and post the main weather tweet
    tweet_text = compose_tweet(weather, time_of_day, uv, rain_alert, fire_warning)
    print(f"\nComposed tweet ({len(tweet_text)} chars):\n{tweet_text}\n")
    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted! Tweet ID: {tweet_id}")

    # Every morning, post a second beach conditions tweet
    if time_of_day == "morning":
        print("\nFetching beach conditions...")
        beaches = get_all_beach_data()
        if beaches:
            beach_text = compose_beach_tweet(beaches)
            print(f"Beach tweet ({len(beach_text)} chars):\n{beach_text}\n")
            beach_id = post_tweet(beach_text)
            print(f"✅ Beach conditions posted! Tweet ID: {beach_id}")

    # On Friday evening, also post the weekend forecast
    if time_of_day == "evening" and is_friday_evening():
        print("\nIt's Friday — posting weekend forecast...")
        weekend = get_weekend_forecast(forecast_data)
        if weekend:
            weekend_text = compose_weekend_tweet(weekend)
            print(f"Weekend tweet ({len(weekend_text)} chars):\n{weekend_text}\n")
            weekend_id = post_tweet(weekend_text)
            print(f"✅ Weekend forecast posted! Tweet ID: {weekend_id}")

    # On Sunday morning, post the week ahead
    if time_of_day == "morning" and is_sunday_morning():
        print("\nIt's Sunday — posting week ahead forecast...")
        week = get_week_ahead(forecast_data)
        if week:
            week_text = compose_week_ahead_tweet(week)
            print(f"Week ahead tweet ({len(week_text)} chars):\n{week_text}\n")
            week_id = post_tweet(week_text)
            print(f"✅ Week ahead posted! Tweet ID: {week_id}")


if __name__ == "__main__":
    main()
