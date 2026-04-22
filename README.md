# 🌤️ Cape Town Weather Bot

A zero-cost Twitter/X bot that posts Cape Town weather every morning at 06:00 and evening at 18:00 (SAST). Runs entirely on GitHub Actions — no server required.

---

## How it works

1. GitHub Actions triggers on a cron schedule (twice daily)
2. The script calls the OpenWeatherMap API for current Cape Town conditions
3. It formats a tweet and posts it via the X API

---

## Setup (one-time, ~30 minutes)

### 1. Get an OpenWeatherMap API key (free)

1. Sign up at https://openweathermap.org/api
2. Go to **API Keys** in your account dashboard
3. Copy your default key (or create a new one)

---

### 2. Get X (Twitter) API credentials

1. Go to https://developer.twitter.com and sign in
2. Create a new Project and App
3. Under **User authentication settings**, enable **OAuth 1.0a** with **Read and Write** permissions
4. Generate your keys — you need all four:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret

> ⚠️ Make sure the Access Token has **Read and Write** permission, not just Read.

---

### 3. Create a GitHub repository

1. Create a new repo (can be private)
2. Push all these files to it:

```
your-repo/
├── main.py
├── weather.py
├── tweet.py
├── requirements.txt
└── .github/
    └── workflows/
        └── schedule.yml
```

---

### 4. Add secrets to GitHub

In your repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|---|---|
| `OPENWEATHER_API_KEY` | Your OpenWeatherMap key |
| `TWITTER_API_KEY` | X API Key |
| `TWITTER_API_SECRET` | X API Secret |
| `TWITTER_ACCESS_TOKEN` | X Access Token |
| `TWITTER_ACCESS_SECRET` | X Access Token Secret |

---

### 5. Test it manually

1. Go to **Actions** tab in your GitHub repo
2. Click **Cape Town Weather Bot**
3. Click **Run workflow**
4. Choose `morning` or `evening` and run
5. Check your X profile — the tweet should appear within ~30 seconds

---

## Timing

| Post | Local time (SAST) | UTC cron |
|---|---|---|
| Morning | 06:00 | `0 4 * * *` |
| Evening | 18:00 | `0 16 * * *` |

> Cape Town observes UTC+2 year-round (no daylight saving time), so no cron adjustments needed seasonally.

---

## Cost

| Service | Free tier | Usage |
|---|---|---|
| OpenWeatherMap | 1,000 calls/day | 2 calls/day ✅ |
| X API | 500 tweets/month | ~62 tweets/month ✅ |
| GitHub Actions | 2,000 minutes/month | ~4 minutes/month ✅ |

**Total: R0/month**

---

## Example tweets

**Morning:**
```
☀️ Good morning, Cape Town!

🌡️ 22°C (feels like 21°C)
🌬️ SE winds at 14 km/h
💧 Humidity: 65%
☁️ Clear sky

Get out there and enjoy it. 🤙

#CapeTown #WeatherZA #CTWeather
```

**Evening:**
```
🌤️ Good evening, Cape Town!

🌡️ 18°C (feels like 17°C)
🌬️ S winds at 20 km/h
💧 Humidity: 72%
☁️ Partly cloudy

Perfect evening for a sundowner. 🥂

#CapeTown #WeatherZA #CTWeather
```
