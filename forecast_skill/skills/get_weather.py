#!/usr/bin/env python3
import os, sys, json, datetime, urllib.request, urllib.parse, urllib.error

OWM_KEY = os.getenv("OWM_API_KEY")
if not OWM_KEY:
    print(json.dumps({"error": "missing_api_key", "message": "OpenWeatherMap API key not found. Please set the OWM_API_KEY environment variable."}))
    sys.exit(1)

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

def geocode(location):
    """Convert a place name to lat/lon via OWM geocoding"""
    data = fetch_json(
        "http://api.openweathermap.org/geo/1.0/direct",
        {"q": location, "limit": 1, "appid": OWM_KEY},
    )
    if "error" in data:
        print(json.dumps(data))
        sys.exit(1)
    if not data or len(data) == 0:
        print(json.dumps({"error": "location_not_found", "message": f"Location '{location}' not found. Try being more specific (e.g., 'Paris, France' instead of 'Paris')."}))
        sys.exit(1)
    entry = data[0]
    return entry["lat"], entry["lon"], entry.get("name", location)

def get_forecast(lat, lon):
    """Fetch One Call weather forecast"""
    data = fetch_json(
        "https://api.openweathermap.org/data/2.5/onecall",
        {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,alerts",
            "units": "metric",
            "appid": OWM_KEY,
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
        print(json.dumps({"error": "invalid_usage", "message": "Usage: get_weather.py <location> <YYYY-MM-DD>"}))
        sys.exit(1)

    location = sys.argv[1]
    target_date = sys.argv[2]

    # Validate date format
    try:
        datetime.datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({"error": "invalid_date", "message": "Date must be in YYYY-MM-DD format"}))
        sys.exit(1)

    lat, lon, resolved = geocode(location)
    forecast = get_forecast(lat, lon)
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
        "sunrise_utc": datetime.datetime.utcfromtimestamp(day.get("sunrise", 0)).isoformat(),
        "sunset_utc": datetime.datetime.utcfromtimestamp(day.get("sunset", 0)).isoformat(),
    }

    print(json.dumps(out))

if __name__ == "__main__":
    main()
