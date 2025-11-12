#!/usr/bin/env python3
"""
Weather forecast script using OpenWeatherMap API.
Usage: get_weather.py <location> <YYYY-MM-DD>
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


def get_forecast(lat, lon, api_key):
    """Fetch One Call weather forecast"""
    data = fetch_json(
        "https://api.openweathermap.org/data/2.5/onecall",
        {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,alerts",
            "units": "metric",
            "appid": api_key,
        },
    )
    if "error" in data:
        print(json.dumps(data))
        sys.exit(1)
    return data


def pick_day(forecast, target_date):
    """Find the forecast for a specific date or fallback to current"""
    target = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    for d in forecast.get("daily", []):
        dt = datetime.date.fromtimestamp(d["dt"])
        if dt == target:
            return d
    return forecast.get("current", {})


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "invalid_usage",
            "message": "Usage: get_weather.py <location> <YYYY-MM-DD>"
        }))
        sys.exit(1)

    location = sys.argv[1]
    target_date = sys.argv[2]

    # Load API key from config.json
    api_key = load_api_key()
    if not api_key:
        print(json.dumps({
            "error": "missing_api_key",
            "message": "API key not configured. Please edit config.json and add your OpenWeatherMap API key."
        }))
        sys.exit(1)

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
    forecast = get_forecast(lat, lon, api_key)
    day = pick_day(forecast, target_date)

    temp_c = day["temp"]["day"] if isinstance(day.get("temp"), dict) else day.get("temp", None)
    temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None

    out = {
        "location": resolved,
        "date": target_date,
        "temp_c": temp_c,
        "temp_f": temp_f,
        "humidity": day.get("humidity"),
        "wind_kph": round(day.get("wind_speed", 0) * 3.6, 1),
        "condition": day.get("weather", [{}])[0].get("description"),
        "precip_mm": day.get("rain", 0),
        "sunrise_utc": datetime.datetime.utcfromtimestamp(day.get("sunrise", 0)).isoformat() if day.get("sunrise") else None,
        "sunset_utc": datetime.datetime.utcfromtimestamp(day.get("sunset", 0)).isoformat() if day.get("sunset") else None,
    }

    print(json.dumps(out))


if __name__ == "__main__":
    main()