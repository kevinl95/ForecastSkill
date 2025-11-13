# Build script to create a ready-to-upload forecast skill bundle
# Usage: .\build.ps1 [api_key] [output_name]

param(
    [string]$ApiKey = "",
    [string]$OutputName = "forecast-skill.zip"
)

# Function to read API key securely
function Read-ApiKey {
    Write-Host "OpenWeatherMap API Key Setup" -ForegroundColor Cyan
    Write-Host "   Get a free key at: https://openweathermap.org/api" -ForegroundColor Gray
    Write-Host ""
    
    do {
        $apiKey = Read-Host "Enter your OpenWeatherMap API key"
        
        if ([string]::IsNullOrWhiteSpace($apiKey)) {
            Write-Host "ERROR: API key cannot be empty. Please try again." -ForegroundColor Red
            continue
        }
        
        if ($apiKey -eq "PASTE_YOUR_API_KEY_HERE") {
            Write-Host "ERROR: Please enter your actual API key, not the placeholder." -ForegroundColor Red
            continue
        }
        
        # Basic validation - OpenWeatherMap keys are typically 32 hex characters
        if ($apiKey -notmatch "^[a-fA-F0-9]{32}$") {
            Write-Host "WARNING: API key doesn't match expected format (32 hex characters)." -ForegroundColor Yellow
            $confirm = Read-Host "Continue anyway? [y/N]"
            if ($confirm -notmatch "^[Yy]$") {
                continue
            }
        }
        
        break
    } while ($true)
    
    return $apiKey
}

Write-Host "Building Forecast Skill bundle with integrated API key..." -ForegroundColor Green

# Get API key if not provided
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    $ApiKey = Read-ApiKey
}

# Clean previous build
if (Test-Path $OutputName) {
    Remove-Item $OutputName -Force
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}

# Create temp directory and copy skill files
New-Item -ItemType Directory -Path "build" -Force | Out-Null
Copy-Item -Path "forecast_skill\*" -Destination "build\" -Recurse -Force

Write-Host "Injecting API key into config.json..." -ForegroundColor Yellow

# Inject API key into config.json
$configPath = "build\config.json"
$configContent = Get-Content $configPath -Raw
$configContent = $configContent -replace "PASTE_YOUR_API_KEY_HERE", $ApiKey
Set-Content -Path $configPath -Value $configContent -NoNewline

# Verify the replacement worked
$verifyContent = Get-Content $configPath -Raw
if ($verifyContent -match "PASTE_YOUR_API_KEY_HERE") {
    Write-Host "ERROR: API key injection failed" -ForegroundColor Red
    Get-Content $configPath
    exit 1
}

Write-Host "API key configured in config.json" -ForegroundColor Green

# Show what will be in the bundle (from build directory - top level)
Write-Host ""
Write-Host "Bundle contents (files will be at top level when extracted):" -ForegroundColor Cyan
Get-ChildItem -Path "build" -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring((Resolve-Path "build").Path.Length + 1)
    Write-Host "  $relativePath"
} | Sort-Object

# Create zip with files at top level
Write-Host ""
Write-Host "Creating zip archive..." -ForegroundColor Yellow

# Use .NET compression to create zip with files at top level
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipPath = Resolve-Path "." | Join-Path -ChildPath $OutputName
$sourcePath = Resolve-Path "build"

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

$zip = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    Get-ChildItem -Path $sourcePath -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($sourcePath.Path.Length + 1)
        # Replace backslashes with forward slashes for zip compatibility
        $entryName = $relativePath -replace "\\", "/"
        $entry = $zip.CreateEntry($entryName)
        $entryStream = $entry.Open()
        try {
            $fileStream = [System.IO.File]::OpenRead($_.FullName)
            try {
                $fileStream.CopyTo($entryStream)
            }
            finally {
                $fileStream.Close()
            }
        }
        finally {
            $entryStream.Close()
        }
    }
}
finally {
    $zip.Dispose()
}

# Validate bundle
Write-Host ""
Write-Host "Created: $OutputName" -ForegroundColor Green
Write-Host "Bundle structure (top-level files):" -ForegroundColor Cyan

# List zip contents
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $zip.Entries | ForEach-Object {
        $size = if ($_.Length -gt 1024) { "{0:N1} KB" -f ($_.Length / 1024) } else { "$($_.Length) B" }
        Write-Host "  $($_.FullName) ($size)"
    }
}
finally {
    $zip.Dispose()
}

# Verify key files exist and API key is configured
Write-Host ""
Write-Host "Validating bundle..." -ForegroundColor Yellow

$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $configEntry = $zip.Entries | Where-Object { $_.FullName -eq "config.json" }
    if ($configEntry) {
        $stream = $configEntry.Open()
        try {
            $reader = New-Object System.IO.StreamReader($stream)
            $configContent = $reader.ReadToEnd()
            
            if ($configContent -match [regex]::Escape($ApiKey)) {
                Write-Host "API key properly configured in bundle" -ForegroundColor Green
            } else {
                Write-Host "ERROR: API key not found in bundled config.json" -ForegroundColor Red
                exit 1
            }
            
            if ($configContent -match "PASTE_YOUR_API_KEY_HERE") {
                Write-Host "ERROR: Placeholder still present in config.json" -ForegroundColor Red
                exit 1
            }
        }
        finally {
            $stream.Close()
        }
    } else {
        Write-Host "ERROR: config.json not found in bundle" -ForegroundColor Red
        exit 1
    }
}
finally {
    $zip.Dispose()
}

Write-Host "Archive integrity check passed" -ForegroundColor Green

Write-Host ""
Write-Host "Build complete! Ready-to-upload skill bundle created." -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ""
Write-Host "User instructions:" -ForegroundColor Cyan
Write-Host "  1. Download $OutputName" -ForegroundColor White
Write-Host "  2. Extract the zip file" -ForegroundColor White
Write-Host "  3. Upload all the extracted files to Claude (they'll be at the top level)" -ForegroundColor White
Write-Host ""
Write-Host "Security note: This bundle contains your API key." -ForegroundColor Yellow
Write-Host "   Only share with trusted users or for your own use." -ForegroundColor Yellow

# Cleanup
Remove-Item "build" -Recurse -Force

Write-Host ""
Write-Host "Build process completed successfully!" -ForegroundColor Green