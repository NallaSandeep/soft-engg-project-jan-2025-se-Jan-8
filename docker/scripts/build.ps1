# Docker environment build script for Windows
param(
    [string[]]$Services,
    [switch]$NoPull,
    [switch]$NoCache
)

# Source common functions
. "$PSScriptRoot\utils\common.ps1"

# Check Docker status
Test-DockerStatus

# Initialize environment
Initialize-Environment

# Build the build command
$command = "docker-compose build"
if (-not $NoPull) {
    $command += " --pull"
}
if ($NoCache) {
    $command += " --no-cache"
}
if ($Services) {
    $command += " " + ($Services -join " ")
}

# Build services
Write-Host "Building services..." -ForegroundColor Cyan
Write-Host "Using command: $command" -ForegroundColor Gray
Invoke-Expression $command

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed. Please check the errors above."
    exit 1
}

Write-Host "`nBuild completed successfully!" -ForegroundColor Green 