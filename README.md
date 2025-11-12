# ForecastSkill

A Claude Skill that provides real-time weather forecasts using the OpenWeatherMap API.

## Quick Start

### For Claude Users

1. **Get an OpenWeatherMap API key** (free):
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account (1,000 calls/day included)
   - Generate an API key

2. **Configure the skill**:
   - Open `forecast_skill/config.json`
   - Replace `"PASTE_YOUR_API_KEY_HERE"` with your actual API key
   - Save the file

3. **Upload to Claude**:
   - Upload the entire `forecast_skill` folder to Claude
   - Start asking weather questions!

**Example:**
```json
{"api_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"}
```

See `forecast_skill/SETUP.txt` for detailed instructions.

## Usage

Ask Claude weather questions and the skill automatically activates:
- "What's the weather like in Paris tomorrow?"
- "Will it rain in Seattle this weekend?"
- "Should I bring a jacket to Denver next week?"
- "Compare the weather in London and Berlin next Monday"

## For Developers

### Local Testing
```bash
cd forecast_skill/skills
python get_weather.py "London" "2025-11-12"
```

### File Structure
```
forecast_skill/
├── SKILL.md              # Instructions for Claude
├── config.json           # User configures API key here
├── SETUP.txt             # Setup instructions
├── skills/
│   └── get_weather.py    # Weather script
└── resources/
    └── prompt_templates.md
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