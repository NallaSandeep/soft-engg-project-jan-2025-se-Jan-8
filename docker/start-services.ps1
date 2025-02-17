# start-services.ps1
Write-Host "Building and starting StudyHub services..." -ForegroundColor Cyan

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $docker = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
        if ($docker) {
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

# Check if Docker is running
if (-not (Test-DockerRunning)) {
    Write-Host "Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from template. Please update with your settings." -ForegroundColor Yellow
}

# Build services
Write-Host "Building Docker images..." -ForegroundColor Cyan
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Please check the errors above." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "Starting services..." -ForegroundColor Cyan
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start services. Please check the errors above." -ForegroundColor Red
    exit 1
}

# Wait for services to be healthy
Write-Host "Waiting for services to be healthy..." -ForegroundColor Cyan
$services = @("redis", "chromadb", "studyindexer", "backend", "frontend")
$maxAttempts = 30
$currentAttempt = 0

while ($currentAttempt -lt $maxAttempts) {
    $allHealthy = $true
    foreach ($service in $services) {
        $status = docker-compose ps $service --format "{{.Status}}"
        if (-not ($status -match "healthy") -and -not ($status -match "running")) {
            $allHealthy = $false
            break
        }
    }
    
    if ($allHealthy) {
        break
    }
    
    $currentAttempt++
    Write-Host "Waiting for services to be healthy... Attempt $currentAttempt of $maxAttempts" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

if ($currentAttempt -eq $maxAttempts) {
    Write-Host "Some services failed to become healthy. Please check docker-compose logs for details." -ForegroundColor Red
    exit 1
}

# Display service URLs and information
Write-Host "`nStudyHub services are ready!" -ForegroundColor Green
Write-Host "`nService URLs:"
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "StudyIndexer API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "ChromaDB: http://localhost:8001" -ForegroundColor Cyan

Write-Host "`nUseful commands:"
Write-Host "- View logs: docker-compose logs -f" -ForegroundColor Gray
Write-Host "- Stop services: docker-compose down" -ForegroundColor Gray
Write-Host "- Restart services: docker-compose restart" -ForegroundColor Gray