---
name: "OpenWeather Forecast Skill"
description: "Provides real-time current and forecast weather information anywhere in the world using OpenWeatherMap."
version: "1.0.0"
---

# OpenWeather Forecast Skill

When to use:
- Whenever the user asks about current, future, or comparative weather (temperature, rain, snow, UV, wind, sunrise, etc.).
- When the user references travel plans, outdoor events, or “should I” weather-dependent questions.
- Examples:
  - “Will it snow in Denver this weekend?”
  - “Is it a good day for a picnic in Central Park?”
  - “What’s the UV index in Sydney right now?”
  - “Compare the weather in Paris and Rome next week.”

Behavior:
1. Extract the relevant **locations** and **dates** from the user’s query.
2. Call `scripts/get_weather.py` with those parameters.
3. Return structured JSON with fields:
   - `location`
   - `date` (or range)
   - `temp_c`, `temp_f`
   - `humidity`, `wind_kph`
   - `condition` (clear, rain, snow, etc.)
   - `precip_mm`
   - `sunrise_utc`, `sunset_utc`
   - `forecast_summary`
4. Summarize naturally in the user’s language and style.

Error handling:
- If location or date missing: ask the user to clarify.
- If API unavailable: say “I wasn’t able to reach the weather service right now.”
