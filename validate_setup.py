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

def check_api_key():
    """Check if API key is set and valid"""
    print("🔑 Checking API key...")
    
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        print("❌ ERROR: OWM_API_KEY environment variable not set")
        print("📖 Please see README.md for setup instructions")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...")
    
    # Test API key validity with a simple request
    print("🌐 Testing API key validity...")
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
                    print("✅ API key is valid and working")
                    return True
                else:
                    print("⚠️  API key works but returned no data")
                    return True
            else:
                print(f"❌ API request failed with status {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("❌ ERROR: Invalid API key")
            print("📖 Please check your OpenWeatherMap API key")
        elif e.code == 429:
            print("⚠️  API quota exceeded - but key appears valid")
            return True
        else:
            print(f"❌ HTTP error {e.code}: {e.reason}")
        return False
        
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def check_script():
    """Check if the weather script works"""
    print("\n🧪 Testing weather script...")
    
    import subprocess
    script_path = "forecast_skill/skills/get_weather.py"
    
    if not os.path.exists(script_path):
        print(f"❌ ERROR: {script_path} not found")
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
                    print(f"❌ Script error: {data.get('message', data['error'])}")
                    return False
                else:
                    print(f"✅ Script working! Got weather for {data.get('location', 'Unknown')}")
                    print(f"   Temperature: {data.get('temp_c', 'Unknown')}°C")
                    return True
            except json.JSONDecodeError:
                print("❌ Script returned invalid JSON")
                print(f"Output: {result.stdout}")
                return False
        else:
            print(f"❌ Script failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def main():
    print("🔧 OpenWeather Forecast Skill Setup Validation\n")
    
    success = True
    
    # Check API key
    if not check_api_key():
        success = False
    
    # Check script functionality
    if not check_script():
        success = False
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 All checks passed! Your skill is ready to use.")
        print("\nYou can now ask Claude weather questions like:")
        print("• 'What's the weather in Paris tomorrow?'")
        print("• 'Will it rain in Tokyo this weekend?'")
    else:
        print("❌ Setup incomplete. Please address the errors above.")
        print("📖 See README.md for detailed setup instructions.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())