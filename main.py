import sys
from weather import get_weather, parse_weather, get_uv_index
from tweet import compose_tweet, post_tweet


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

    # Fetch UV index for morning posts
    uv = None
    if time_of_day == "morning":
        uv = get_uv_index()
        print(f"UV Index: {uv}")

    tweet_text = compose_tweet(weather, time_of_day, uv)
    print(f"\nComposed tweet ({len(tweet_text)} chars):\n{tweet_text}\n")

    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted! Tweet ID: {tweet_id}")


if __name__ == "__main__":
    main()
