# Docker environment start script for Windows
param(
    [switch]$SkipBuild,
    [switch]$DetachedMode
)

# Source common functions
. "$PSScriptRoot\utils\common.ps1"

# Check Docker status
Test-DockerStatus

# Environment setup
Initialize-Environment

# Build services if not skipped
if (-not $SkipBuild) {
    Write-Host "Building services..." -ForegroundColor Cyan
    & "$PSScriptRoot\build.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed. Please check the errors above."
        exit 1
    }
}

# Start services
Write-Host "Starting services..." -ForegroundColor Cyan
$command = "docker-compose up"
if ($DetachedMode) {
    $command += " -d"
}

Invoke-Expression $command

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start services. Please check the errors above."
    exit 1
}

if ($DetachedMode) {
    # Wait for services to be healthy
    Wait-ForHealthyServices

    # Display service information
    Show-ServiceInformation
} 