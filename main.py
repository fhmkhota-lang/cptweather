import sys
from weather import get_weather, parse_weather
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

    tweet_text = compose_tweet(weather, time_of_day)
    print(f"\nComposed tweet ({len(tweet_text)} chars):\n{tweet_text}\n")

    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted! Tweet ID: {tweet_id}")


if __name__ == "__main__":
    main()
