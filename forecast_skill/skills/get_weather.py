#!/usr/bin/env python3
"""
Weather forecast script using OpenWeatherMap API.
Usage: 
  get_weather.py <location> <YYYY-MM-DD>                    # Single day forecast
  get_weather.py compare <location1> <location2> <days>      # Multi-day comparison
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
import urllib.error


def load_api_key():
    """Load API key from config.json in the skill directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            api_key = config.get('api_key', '')
            
            if not api_key or api_key == 'PASTE_YOUR_API_KEY_HERE':
                return None
            return api_key.strip()
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def fetch_json(url, params):
    """Helper: GET request returning parsed JSON"""
    qs = urllib.parse.urlencode(params)
    full_url = f"{url}?{qs}"
    try:
        with urllib.request.urlopen(full_url, timeout=10) as resp:
            if resp.getcode() == 401:
                return {"error": "invalid_api_key", "message": "Invalid OpenWeatherMap API key."}
            elif resp.getcode() == 429:
                return {"error": "quota_exceeded", "message": "API quota exceeded. Please try again later."}
            elif resp.getcode() != 200:
                return {"error": "api_error", "message": f"API returned status {resp.getcode()}"}
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {"error": "invalid_api_key", "message": "Invalid OpenWeatherMap API key."}
        elif e.code == 429:
            return {"error": "quota_exceeded", "message": "API quota exceeded. Please try again later."}
        else:
            return {"error": "http_error", "message": f"HTTP error {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": "network_error", "message": f"Network error: {e.reason}"}
    except Exception as e:
        return {"error": "unknown_error", "message": str(e)}


def geocode(location, api_key):
    """Convert a place name to lat/lon via OWM geocoding"""
    data = fetch_json(
        "http://api.openweathermap.org/geo/1.0/direct",
        {"q": location, "limit": 1, "appid": api_key},
    )
    if "error" in data:
        print(json.dumps(data))
        sys.exit(1)
    if not data or len(data) == 0:
        print(json.dumps({
            "error": "location_not_found",
            "message": f"Location '{location}' not found. Try being more specific (e.g., 'Paris, France' instead of 'Paris')."
        }))
        sys.exit(1)
    entry = data[0]
    return entry["lat"], entry["lon"], entry.get("name", location)


def get_current_weather(lat, lon, api_key):
    """Fetch current weather data"""
    data = fetch_json(
        "https://api.openweathermap.org/data/2.5/weather",
        {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": api_key,
        },
    )
    if "error" in data:
        return data
    return data


def get_forecast(lat, lon, api_key):
    """Fetch 5-day weather forecast"""
    data = fetch_json(
        "https://api.openweathermap.org/data/2.5/forecast",
        {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": api_key,
        },
    )
    if "error" in data:
        return data
    return data


def pick_day(forecast, target_date):
    """Find the forecast for a specific date from 5-day forecast"""
    target = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    
    # Look through the forecast list for matching date
    for item in forecast.get("list", []):
        forecast_date = datetime.date.fromtimestamp(item["dt"])
        if forecast_date == target:
            return item
    
    # If no exact match found, return None (will use current weather)
    return None


def get_multi_day_forecast(forecast, num_days):
    """Get forecast for multiple days from 5-day forecast"""
    forecasts = []
    daily_summaries = {}
    
    # Group forecast items by date and find daily highs/lows
    for item in forecast.get("list", []):
        date = datetime.date.fromtimestamp(item["dt"])
        date_str = date.isoformat()
        
        if date_str not in daily_summaries:
            daily_summaries[date_str] = {
                "date": date_str,
                "date_formatted": date.strftime("%A, %B %d"),
                "temps": [],
                "conditions": [],
                "humidity_values": [],
                "wind_speeds": [],
                "precip_amounts": [],
                "precip_probs": []
            }
        
        # Collect data for daily summary
        daily_summaries[date_str]["temps"].append(item["main"]["temp"])
        daily_summaries[date_str]["conditions"].append(item["weather"][0])
        daily_summaries[date_str]["humidity_values"].append(item["main"]["humidity"])
        daily_summaries[date_str]["wind_speeds"].append(item["wind"]["speed"])
        daily_summaries[date_str]["precip_probs"].append(item.get("pop", 0))
        
        # Add precipitation if it exists
        rain = item.get("rain", {}).get("3h", 0)
        snow = item.get("snow", {}).get("3h", 0)
        daily_summaries[date_str]["precip_amounts"].append(rain + snow)
    
    # Convert to final format, taking only the requested number of days
    sorted_dates = sorted(daily_summaries.keys())[:num_days]
    
    for date_str in sorted_dates:
        day_data = daily_summaries[date_str]
        temps = day_data["temps"]
        
        # Find the most common weather condition for the day
        conditions = day_data["conditions"]
        condition_mains = [c["main"] for c in conditions]
        most_common_main = max(set(condition_mains), key=condition_mains.count)
        most_common_condition = next(c for c in conditions if c["main"] == most_common_main)
        
        forecasts.append({
            "date": day_data["date"],
            "date_formatted": day_data["date_formatted"],
            "temp_high_c": round(max(temps), 1),
            "temp_high_f": round(max(temps) * 9 / 5 + 32, 1),
            "temp_low_c": round(min(temps), 1),
            "temp_low_f": round(min(temps) * 9 / 5 + 32, 1),
            "condition": most_common_condition["description"],
            "condition_main": most_common_condition["main"],
            "humidity": round(sum(day_data["humidity_values"]) / len(day_data["humidity_values"])),
            "wind_kph": round(sum(day_data["wind_speeds"]) / len(day_data["wind_speeds"]) * 3.6, 1),
            "precip_mm": round(sum(day_data["precip_amounts"]), 1),
            "precip_probability": round(max(day_data["precip_probs"]) * 100),
            "uv_index": 0  # Not available in 5-day forecast
        })
    
    return forecasts


def analyze_comparison(location1_forecasts, location2_forecasts):
    """Analyze two location forecasts and provide recommendations"""
    recommendations = []
    
    # Compare average temperatures
    avg_temp1 = sum(d["temp_high_c"] for d in location1_forecasts if d["temp_high_c"]) / len(location1_forecasts)
    avg_temp2 = sum(d["temp_high_c"] for d in location2_forecasts if d["temp_high_c"]) / len(location2_forecasts)
    
    if avg_temp1 > avg_temp2 + 5:
        recommendations.append(f"{location1_forecasts[0]['location']} will be significantly warmer")
    elif avg_temp2 > avg_temp1 + 5:
        recommendations.append(f"{location2_forecasts[0]['location']} will be significantly warmer")
    
    # Compare rain probability
    rain_days1 = sum(1 for d in location1_forecasts if d["precip_probability"] > 50)
    rain_days2 = sum(1 for d in location2_forecasts if d["precip_probability"] > 50)
    
    if rain_days1 > rain_days2:
        recommendations.append(f"{location2_forecasts[0]['location']} has fewer rainy days expected")
    elif rain_days2 > rain_days1:
        recommendations.append(f"{location1_forecasts[0]['location']} has fewer rainy days expected")
    
    # Overall recommendation
    if not recommendations:
        recommendations.append("Both locations have similar weather patterns")
    
    return recommendations


def compare_locations(location1, location2, num_days, api_key):
    """Compare weather between two locations over multiple days"""
    try:
        # Get data for both locations
        lat1, lon1, resolved1 = geocode(location1, api_key)
        forecast1 = get_forecast(lat1, lon1, api_key)
        if "error" in forecast1:
            return forecast1
        forecasts1 = get_multi_day_forecast(forecast1, num_days)
        
        lat2, lon2, resolved2 = geocode(location2, api_key)
        forecast2 = get_forecast(lat2, lon2, api_key)
        if "error" in forecast2:
            return forecast2
        forecasts2 = get_multi_day_forecast(forecast2, num_days)
        
        # Add location names to forecast data
        for f in forecasts1:
            f["location"] = resolved1
        for f in forecasts2:
            f["location"] = resolved2
        
        # Analyze and compare
        recommendations = analyze_comparison(forecasts1, forecasts2)
        
        return {
            "comparison_type": "multi_day",
            "num_days": num_days,
            "location1": {
                "name": resolved1,
                "forecasts": forecasts1
            },
            "location2": {
                "name": resolved2,
                "forecasts": forecasts2
            },
            "recommendations": recommendations,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": "comparison_failed",
            "message": f"Failed to compare locations: {str(e)}"
        }


def main():
    # Load API key from config.json
    api_key = load_api_key()
    if not api_key:
        print(json.dumps({
            "error": "missing_api_key",
            "message": "API key not configured. Please edit config.json and add your OpenWeatherMap API key."
        }))
        sys.exit(1)

    # Check for comparison mode
    if len(sys.argv) >= 2 and sys.argv[1] == "compare":
        if len(sys.argv) < 5:
            print(json.dumps({
                "error": "invalid_usage",
                "message": "Usage: get_weather.py compare <location1> <location2> <days>"
            }))
            sys.exit(1)
        
        location1 = sys.argv[2]
        location2 = sys.argv[3]
        try:
            num_days = int(sys.argv[4])
            if num_days < 1 or num_days > 7:
                raise ValueError("Days must be between 1 and 7")
        except ValueError as e:
            print(json.dumps({
                "error": "invalid_days",
                "message": f"Invalid number of days: {e}"
            }))
            sys.exit(1)
        
        result = compare_locations(location1, location2, num_days, api_key)
        print(json.dumps(result))
        return

    # Standard single location forecast
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "invalid_usage",
            "message": "Usage: get_weather.py <location> <YYYY-MM-DD> OR get_weather.py compare <location1> <location2> <days>"
        }))
        sys.exit(1)

    location = sys.argv[1]
    target_date = sys.argv[2]

    # Validate date format
    try:
        datetime.datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({
            "error": "invalid_date",
            "message": "Date must be in YYYY-MM-DD format"
        }))
        sys.exit(1)

    lat, lon, resolved = geocode(location, api_key)
    
    # Check if target date is today - use current weather, otherwise use forecast
    today = datetime.date.today()
    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    
    if target_date_obj == today:
        # Use current weather for today
        weather_data = get_current_weather(lat, lon, api_key)
        if "error" in weather_data:
            print(json.dumps(weather_data))
            sys.exit(1)
        
        temp_c = weather_data["main"]["temp"]
        temp_f = round(temp_c * 9 / 5 + 32, 1)
        
        out = {
            "location": resolved,
            "date": target_date,
            "temp_c": temp_c,
            "temp_f": temp_f,
            "humidity": weather_data["main"]["humidity"],
            "wind_kph": round(weather_data["wind"]["speed"] * 3.6, 1),
            "condition": weather_data["weather"][0]["description"],
            "precip_mm": 0,  # Current weather doesn't include precipitation amount
            "sunrise_utc": datetime.datetime.utcfromtimestamp(weather_data["sys"]["sunrise"]).isoformat(),
            "sunset_utc": datetime.datetime.utcfromtimestamp(weather_data["sys"]["sunset"]).isoformat(),
        }
    else:
        # Use forecast for future dates
        forecast = get_forecast(lat, lon, api_key)
        if "error" in forecast:
            print(json.dumps(forecast))
            sys.exit(1)
        
        day = pick_day(forecast, target_date)
        if not day:
            print(json.dumps({
                "error": "date_not_available",
                "message": f"Forecast not available for {target_date}. 5-day forecast limit."
            }))
            sys.exit(1)
        
        temp_c = day["main"]["temp"]
        temp_f = round(temp_c * 9 / 5 + 32, 1)
        
        rain_3h = day.get("rain", {}).get("3h", 0)
        snow_3h = day.get("snow", {}).get("3h", 0)
        
        out = {
            "location": resolved,
            "date": target_date,
            "temp_c": temp_c,
            "temp_f": temp_f,
            "humidity": day["main"]["humidity"],
            "wind_kph": round(day["wind"]["speed"] * 3.6, 1),
            "condition": day["weather"][0]["description"],
            "precip_mm": rain_3h + snow_3h,
            "sunrise_utc": None,  # Not available in forecast data
            "sunset_utc": None,   # Not available in forecast data
        }

    print(json.dumps(out))


if __name__ == "__main__":
    main()