# ForecastSkill

A Claude Skill that provides real-time weather forecasts using the OpenWeatherMap API.

## Quick Start

1. Clone this repository
2. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
3. Run the build script and enter your API key when prompted: `./build.sh`
4. Upload the generated zip to Claude.

### Build Script Options

```bash
./build.sh                          # Interactive: prompts for API key
./build.sh your_api_key_here        # Non-interactive: uses provided key
./build.sh your_key custom-name.zip # Custom output filename
```

The build script will:
- Inject your API key into config.json
- Create a zip with files at the top level (no subfolders)
- Validate the bundle structure
- Ready for immediate upload to Claude

## Usage

Ask Claude weather questions and the skill automatically activates:

**Single Location Weather:**
- "What's the weather like in Paris tomorrow?"
- "Will it rain in Seattle this weekend?"
- "Should I bring a jacket to Denver next week?"

**Multi-Location Comparison:** 
- "Compare weather in Paris vs London next week"
- "Which city has better weather this week, Berlin or Amsterdam?"
- "Paris or Rome for a 5-day trip?"

### Local Testing
```bash
cd forecast_skill/skills
python get_weather.py "London" "2025-11-12"
```

## Troubleshooting

**"missing_api_key" error**: 
- Edit `config.json` and add your OpenWeatherMap API key
- Make sure you replaced the placeholder text

**"invalid_api_key" error**: 
- Verify your API key at https://openweathermap.org/api
- Check for extra spaces or quotes in config.json

**"location_not_found" error**: 
- Try a more specific location name
- Use format like "Paris, France" instead of just "Paris"