# Prompt Templates for SkyFetch

## Overview
SkyFetch provides Claude with real-time weather data from the OpenWeatherMap API.
Claude should use this Skill when a user asks about **current or forecast weather** for a **specific location or activity**.

## Trigger Examples

Claude should consider invoking SkyFetch when the user asks questions like:
- “What’s the weather in Boulder this weekend?”
- “Should I ski at Loveland this weekend or next?”
- “Is it going to rain in San Francisco tomorrow?”
- “What’s the temperature right now in Paris?”
- “Is next week better for hiking in Moab?”

## Invocation Template

When using this Skill, extract:
- The location (city, region, or landmark)
- The date or time frame (if given)
- The activity or context (if relevant)

Then call the `get_weather` function defined in `weather.py`:

```json
{
  "function": "get_weather",
  "arguments": {
    "location": "{{location}}",
    "timeframe": "{{timeframe}}"
  }
}
```

## Response Guidance

Summarize the weather clearly in natural language.

Provide actionable insight if an activity is mentioned (e.g., “Next weekend looks colder with more snow, which may be better for skiing.”).

Include temperature range, precipitation, and general conditions.

If the Skill fails or live data isn’t available, reply gracefully:

“I wasn’t able to get the latest weather, but based on seasonal averages, Loveland usually has [summary] around this time.”

## Developer Notes

Uses urllib.request for fetching data.

API key is stored in environment variable OPENWEATHERMAP_API_KEY.

Expected outputs should be short JSON summaries that Claude can weave into natural replies.