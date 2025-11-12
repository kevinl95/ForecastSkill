# ForecastSkill

A Claude Skill that provides real-time weather forecasts using the OpenWeatherMap API.

## How This Works

This skill is designed to work with Claude through Anthropic's platform. When properly configured, Claude can automatically call this skill to provide weather information in response to your questions.

## Setup for Skill Developers/Self-Hosted Usage

If you're running this skill locally or integrating it into your own system:

### 1. Get an OpenWeatherMap API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api) and sign up for a free account
2. Navigate to the API keys section in your account dashboard
3. Generate a new API key (free tier allows 1,000 calls/day)

### 2. Configure the API Key

The skill expects the API key to be available as an environment variable `OWM_API_KEY`.

**For local development/testing:**
```bash
export OWM_API_KEY="your_api_key_here"
python forecast_skill/skills/get_weather.py "New York" "2025-11-12"
```

**Note for Claude Web Users:** If you're using Claude through the web interface, the skill configuration and API key management is handled by Anthropic's infrastructure. You don't need to set environment variables yourself.

## Usage

This skill automatically activates when you ask Claude weather-related questions:
- "What's the weather like in Paris tomorrow?"
- "Will it rain in Seattle this weekend?"
- "Should I bring a jacket to Denver next week?"

## For Developers

If you're working on this skill or integrating it into your own systems, you can test it locally by setting the environment variable and running the script directly.

## Troubleshooting

**For developers/self-hosted users:**
- **"missing_api_key" error**: Set the OWM_API_KEY environment variable
- **"location_not_found" error**: Try a more specific location name
- **API timeout errors**: Check your internet connection

**For Claude web users:**
If the skill isn't working, the issue is likely on Anthropic's side - API configuration, skill deployment, or service availability.