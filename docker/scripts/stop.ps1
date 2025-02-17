# Docker environment stop script for Windows
param(
    [switch]$RemoveVolumes,
    [switch]$RemoveOrphans
)

# Source common functions
. "$PSScriptRoot\utils\common.ps1"

# Check Docker status
Test-DockerStatus

# Initialize environment
Initialize-Environment

# Build the stop command
$command = "docker-compose down"
if ($RemoveVolumes) {
    $command += " -v"
}
if ($RemoveOrphans) {
    $command += " --remove-orphans"
}

# Stop services
Write-Host "Stopping services..." -ForegroundColor Cyan
Invoke-Expression $command

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to stop services. Please check the errors above."
    exit 1
}

Write-Host "`nServices stopped successfully!" -ForegroundColor Green
if ($RemoveVolumes) {
    Write-Host "All volumes have been removed." -ForegroundColor Yellow
} 