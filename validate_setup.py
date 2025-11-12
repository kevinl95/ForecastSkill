#!/usr/bin/env python3
"""
Validation script to check if the OpenWeather Forecast Skill is properly configured.
Run this script to verify your API key and setup before using the skill.
"""

import os
import sys
import json
import urllib.request
import urllib.parse

#!/usr/bin/env python3
"""
Validation script to check if the OpenWeather Forecast Skill is properly configured.
Run this script to verify your config.json setup before uploading the skill to Claude.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

def check_config_file():
    """Check if config.json exists and has a valid API key"""
    print("Checking config.json...")
    
    config_path = "forecast_skill/config.json"
    if not os.path.exists(config_path):
        print(f"ERROR: {config_path} not found")
        print(" This file should contain your OpenWeatherMap API key")
        return False, None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("ERROR: config.json is not valid JSON")
        print(" Check for syntax errors in the file")
        return False, None
    
    api_key = config.get('api_key', '')
    
    if not api_key:
        print("ERROR: No 'api_key' field found in config.json")
        return False, None
    
    if api_key == 'PASTE_YOUR_API_KEY_HERE':
        print("ERROR: API key not configured")
        print(" Please edit config.json and replace the placeholder with your actual API key")
        return False, None
    
    print(f" Config file found with API key: {api_key[:8]}...")
    return True, api_key
    
def test_api_key(api_key):
    """Test if the API key works with a simple request"""
    print(" Testing API key validity...")
    try:
        params = urllib.parse.urlencode({
            "q": "London",
            "limit": 1,
            "appid": api_key
        })
        url = f"http://api.openweathermap.org/geo/1.0/direct?{params}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.getcode() == 200:
                data = json.load(response)
                if data:
                    print(" API key is valid and working")
                    return True
                else:
                    print("WARNING: API key works but returned no data")
                    return True
            else:
                print(f"ERROR: API request failed with status {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("ERROR: Invalid API key")
            print(" Please check your OpenWeatherMap API key")
        elif e.code == 429:
            print("WARNING: API quota exceeded - but key appears valid")
            return True
        else:
            print(f"ERROR: HTTP error {e.code}: {e.reason}")
        return False
        
    except Exception as e:
        print(f"ERROR: Network error: {e}")
        return False

def check_script():
    """Check if the weather script works"""
    print("\n Testing weather script...")
    
    import subprocess
    script_path = "forecast_skill/skills/get_weather.py"
    
    if not os.path.exists(script_path):
        print(f"ERROR: {script_path} not found")
        return False
    
    try:
        # Test with London, today's date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        result = subprocess.run([
            sys.executable, script_path, "London", today
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if "error" in data:
                    print(f"ERROR: Script error: {data.get('message', data['error'])}")
                    return False
                else:
                    print(f" Script working! Got weather for {data.get('location', 'Unknown')}")
                    print(f"   Temperature: {data.get('temp_c', 'Unknown')}°C")
                    return True
            except json.JSONDecodeError:
                print("ERROR: Script returned invalid JSON")
                print(f"Output: {result.stdout}")
                return False
        else:
            print(f"ERROR: Script failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: Script timed out")
        return False
    except Exception as e:
        print(f"ERROR: Error running script: {e}")
        return False

def main():
    print("OpenWeather Forecast Skill Setup Validation\n")
    
    success = True
    
    # Check config file
    config_valid, api_key = check_config_file()
    if not config_valid:
        success = False
    else:
        # Test API key
        if not test_api_key(api_key):
            success = False
        
        # Test script functionality
        if not check_script():
            success = False
    
    print(f"\n{'='*50}")
    if success:
        print("All checks passed! Your skill is ready to upload to Claude.")
        print("\nOnce uploaded, you can ask Claude weather questions like:")
        print("• 'What's the weather in Paris tomorrow?'")
        print("• 'Will it rain in Tokyo this weekend?'")
    else:
        print("Setup incomplete. Please address the errors above.")
        print("See SETUP.txt for detailed configuration instructions.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())