#!/bin/bash
# Build script to create a ready-to-upload forecast skill bundle
# Usage: ./build.sh [api_key] [output_name]

set -e

API_KEY="$1"
OUTPUT_NAME="${2:-forecast-skill.zip}"

# Function to read API key securely
read_api_key() {
    echo "OpenWeatherMap API Key Setup"
    echo "   Get a free key at: https://openweathermap.org/api"
    echo ""
    
    while true; do
        echo -n "Enter your OpenWeatherMap API key: "
        read -r api_key
        
        if [[ -z "$api_key" ]]; then
            echo "ERROR: API key cannot be empty. Please try again."
            continue
        fi
        
        if [[ "$api_key" == "PASTE_YOUR_API_KEY_HERE" ]]; then
            echo "ERROR: Please enter your actual API key, not the placeholder."
            continue
        fi
        
        # Basic validation - OpenWeatherMap keys are typically 32 hex characters
        if [[ ! "$api_key" =~ ^[a-fA-F0-9]{32}$ ]]; then
            echo "WARNING: API key doesn't match expected format (32 hex characters)."
            echo -n "Continue anyway? [y/N]: "
            read -r confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                continue
            fi
        fi
        
        break
    done
    
    echo "$api_key"
}

echo "Building Forecast Skill bundle with integrated API key..."

# Get API key if not provided
if [[ -z "$API_KEY" ]]; then
    API_KEY=$(read_api_key)
fi

# Clean previous build
rm -f "$OUTPUT_NAME"
rm -rf build/

# Create temp directory and copy skill files
mkdir -p build
cp -r forecast_skill/* build/

echo "Injecting API key into config.json..."

# Inject API key into config.json
sed -i "s/PASTE_YOUR_API_KEY_HERE/$API_KEY/g" build/config.json

# Verify the replacement worked
if grep -q "PASTE_YOUR_API_KEY_HERE" build/config.json; then
    echo "ERROR: API key injection failed"
    cat build/config.json
    exit 1
fi

echo "API key configured in config.json"

# Show what will be in the bundle (from build directory - top level)
echo ""
echo "Bundle contents (files will be at top level when extracted):"
find build -type f | sed 's|^build/||' | sort

# Create zip with files at top level
cd build
zip -r "../$OUTPUT_NAME" .
cd ..

# Validate bundle
echo ""
echo "Created: $OUTPUT_NAME"
echo "Bundle structure (top-level files):"
unzip -l "$OUTPUT_NAME"

# Verify key files exist and API key is configured
echo ""
echo "Validating bundle..."
unzip -t "$OUTPUT_NAME" > /dev/null
echo "Archive integrity check passed"

if unzip -p "$OUTPUT_NAME" config.json | grep -q "$API_KEY"; then
    echo "API key properly configured in bundle"
else
    echo "ERROR: API key not found in bundled config.json"
    exit 1
fi

if unzip -p "$OUTPUT_NAME" config.json | grep -q "PASTE_YOUR_API_KEY_HERE"; then
    echo "ERROR: Placeholder still present in config.json"
    exit 1
fi

echo ""
echo "Build complete! Ready-to-upload skill bundle created."
echo ""
echo "User instructions:"
echo "  1. Download $OUTPUT_NAME"
echo "  2. Extract the zip file"
echo "  3. Upload all the extracted files to Claude (they'll be at the top level)"
echo ""
echo "Security note: This bundle contains your API key."
echo "   Only share with trusted users or for your own use."

# Cleanup
rm -rf build/