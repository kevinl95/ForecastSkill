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

### Single Location Forecast

When the user asks about weather for one location:

1. **Extract location and date** from the query
   - Location: City name (e.g., "Paris", "New York", "London, UK")
   - Date: YYYY-MM-DD format (default to today if not specified)

2. **Call the weather script**:
   ```bash
   python scripts/get_weather.py "<location>" "<date>"
   ```

3. **Parse the JSON response** and format naturally for the user

### Multi-Location Comparison

When the user asks to compare weather between locations:

**Trigger phrases:**
- "Compare weather in Paris vs London"
- "Paris or Berlin next week?"
- "Which city has better weather this week?"

1. **Extract locations and timeframe** from the query
   - Two locations to compare
   - Number of days (1-7, default to 7 for "week")

2. **Call the comparison script**:
   ```bash
   python scripts/get_weather.py compare "<location1>" "<location2>" <days>
   ```

3. **Present side-by-side comparison** with recommendations

## Error Handling

- **missing_api_key**: "The weather service isn't configured. Please edit config.json with your OpenWeatherMap API key before uploading this skill."
- **invalid_api_key**: "Invalid OpenWeatherMap API key. Please check your key in config.json."
- **location_not_found**: Ask for a more specific location (e.g., "Paris, France" instead of "Paris")
- **quota_exceeded**: "The weather service has reached its daily limit. Please try again later."

## Response Format

### Single Location Response
The script returns JSON with these fields:
- `location`: Resolved location name
- `date`: Date of forecast
- `temp_c`, `temp_f`: Temperature in Celsius and Fahrenheit
- `humidity`: Relative humidity percentage
- `wind_kph`: Wind speed in km/h
- `condition`: Weather description (e.g., "partly cloudy", "light rain")
- `precip_mm`: Precipitation in millimeters
- `sunrise_utc`, `sunset_utc`: Sun times in UTC ISO format

### Comparison Response
For multi-location comparisons, the script returns:
- `comparison_type`: "multi_day"
- `num_days`: Number of days compared
- `location1`/`location2`: Each containing:
  - `name`: Resolved location name
  - `forecasts`: Array of daily forecasts with temps, conditions, precipitation
- `recommendations`: Array of comparison insights and suggestions

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
2. Call script
3. Respond based on precipitation: "Yes, I'd recommend an umbrella - Tokyo is expecting light rain tomorrow with 8mm of precipitation."

**User:** "Compare weather in Paris vs London next week"
**Action:**
1. Extract: location1="Paris", location2="London", days=7
2. Call: `python scripts/get_weather.py compare "Paris" "London" 7`
3. Present comparison: "Comparing Paris and London for the next week: Paris will be warmer overall (averaging 18°C vs 14°C) but has more rainy days expected (4 vs 2). London has fewer rainy days expected, making it better for outdoor activities despite cooler temperatures."