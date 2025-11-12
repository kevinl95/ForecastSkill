---
name: "forecast-skill"
description: "Provides real-time weather forecasts using OpenWeatherMap API. Use when users ask about current or future weather conditions, temperature, precipitation, or weather-dependent planning for any location (e.g., 'What's the weather in Paris tomorrow?', 'Will it rain in Seattle this weekend?', 'Should I bring a jacket to Denver?')."
---

# Forecast Skill

Get real-time weather data and forecasts for any location worldwide using OpenWeatherMap.

## Prerequisites

This skill requires an OpenWeatherMap API key to be configured in `config.json` before uploading.

**Setup (done once before uploading the skill):**
1. Get a free API key at https://openweathermap.org/api
2. Edit `config.json` and replace `PASTE_YOUR_API_KEY_HERE` with your key
3. Upload the skill to Claude

See `SETUP.txt` for detailed instructions.

## Usage

When the user asks about weather:

1. **Extract location and date** from the query
   - Location: City name (e.g., "Paris", "New York", "London, UK")
   - Date: YYYY-MM-DD format (default to today if not specified)

2. **Call the weather script**:
   ```bash
   python scripts/get_weather.py "<location>" "<date>"
   ```

3. **Parse the JSON response** and format naturally for the user

## Error Handling

- **missing_api_key**: "The weather service isn't configured. Please edit config.json with your OpenWeatherMap API key before uploading this skill."
- **invalid_api_key**: "Invalid OpenWeatherMap API key. Please check your key in config.json."
- **location_not_found**: Ask for a more specific location (e.g., "Paris, France" instead of "Paris")
- **quota_exceeded**: "The weather service has reached its daily limit. Please try again later."

## Response Format

The script returns JSON with these fields:
- `location`: Resolved location name
- `date`: Date of forecast
- `temp_c`, `temp_f`: Temperature in Celsius and Fahrenheit
- `humidity`: Relative humidity percentage
- `wind_kph`: Wind speed in km/h
- `condition`: Weather description (e.g., "partly cloudy", "light rain")
- `precip_mm`: Precipitation in millimeters
- `sunrise_utc`, `sunset_utc`: Sun times in UTC ISO format

Present this information conversationally, highlighting the most relevant details for the user's query.

## Error Handling

The script may return errors in JSON format:

- `missing_api_key`: API key not provided - ask user for their key
- `invalid_api_key`: API key is invalid - ask user to verify their key
- `location_not_found`: Location not recognized - ask for clarification (e.g., "Paris, France" instead of "Paris")
- `quota_exceeded`: API daily limit reached - inform user to try later
- `invalid_date`: Date format incorrect - use YYYY-MM-DD format
- Network errors: Inform user the weather service is temporarily unavailable

## Examples

**User:** "What's the weather in Boulder this weekend?"
**Action:**
1. Extract: location="Boulder", dates=[Saturday, Sunday]
2. Get API key (if needed)
3. Call script twice (once for each day)
4. Summarize: "This weekend in Boulder: Saturday will be sunny and 72°F, perfect for outdoor activities. Sunday looks cooler at 65°F with a chance of afternoon showers."

**User:** "Should I bring an umbrella to Tokyo tomorrow?"
**Action:**
1. Extract: location="Tokyo", date=tomorrow
2. Get API key (if needed)
3. Call script
4. Respond based on precipitation: "Yes, I'd recommend an umbrella - Tokyo is expecting light rain tomorrow with 8mm of precipitation."