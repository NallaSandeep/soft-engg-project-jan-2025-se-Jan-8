# Common PowerShell functions for Docker scripts

function Test-DockerStatus {
    try {
        $docker = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
        if (-not $docker) {
            Write-Error "Docker Desktop is not running. Please start Docker Desktop and try again."
            exit 1
        }
    }
    catch {
        Write-Error "Error checking Docker status: $_"
        exit 1
    }
}

function Initialize-Environment {
    # Ensure we're in the docker directory
    $dockerDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Set-Location $dockerDir

    # Create .env file if it doesn't exist
    if (-not (Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host "Created .env file from template. Please update with your settings." -ForegroundColor Yellow
    }

    # Enable BuildKit
    $env:DOCKER_BUILDKIT = 1
    $env:COMPOSE_DOCKER_CLI_BUILD = 1

    # Ensure data persistence directories exist
    $dataDirectories = @(
        "../studyindexer/data/chroma",
        "../studyindexer/data/uploads",
        "../studyindexer/data/processed",
        "../studyindexer/logs",
        "../studyhub/backend/instance",
        "../studyhub/backend/logs"
    )

    foreach ($dir in $dataDirectories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created directory: $dir" -ForegroundColor Yellow
        }
    }
}

# Service dependency map
$script:serviceDependencies = @{
    'redis' = @()
    'chromadb' = @()
    'studyindexer' = @('redis', 'chromadb')
    'celery-worker' = @('redis', 'studyindexer')
    'backend' = @('studyindexer')
    'frontend' = @('backend')
}

function Test-ServiceHealth {
    param (
        [string]$Service,
        [int]$TimeoutSeconds = 30
    )

    Write-Host "Checking health of $Service..." -ForegroundColor Cyan
    $startTime = Get-Date

    # Check dependencies first
    foreach ($dependency in $script:serviceDependencies[$Service]) {
        if (-not (Test-ServiceHealth -Service $dependency -TimeoutSeconds $TimeoutSeconds)) {
            Write-Error "Dependency $dependency is not healthy for $Service"
            return $false
        }
    }

    while ((Get-Date).Subtract($startTime).TotalSeconds -lt $TimeoutSeconds) {
        $status = docker-compose ps $Service --format "{{.Status}}"
        
        # Service-specific health checks
        switch ($Service) {
            'redis' {
                $redisHealth = docker-compose exec -T redis redis-cli ping
                if ($redisHealth -eq 'PONG') {
                    return $true
                }
            }
            'chromadb' {
                $chromaHealth = docker-compose exec -T chromadb curl -s http://localhost:8000/api/v1/heartbeat
                if ($chromaHealth -match 'ok') {
                    return $true
                }
            }
            'studyindexer' {
                $indexerHealth = docker-compose exec -T studyindexer curl -s http://localhost:8000/health
                if ($indexerHealth -match 'healthy') {
                    return $true
                }
            }
            'backend' {
                # Check if database is initialized
                $dbExists = docker-compose exec -T backend test -f /app/instance/studyhub.db
                if ($LASTEXITCODE -eq 0) {
                    $backendHealth = docker-compose exec -T backend curl -s http://localhost:5000/api/health
                    if ($backendHealth -match 'ok') {
                        return $true
                    }
                } else {
                    Write-Host "Database not initialized. Running init_db.py..." -ForegroundColor Yellow
                    docker-compose exec -T backend python scripts/init_db.py
                }
            }
            default {
                if ($status -match 'healthy|running') {
                    return $true
                }
            }
        }

        Start-Sleep -Seconds 2
    }

    Write-Error "Service $Service failed to become healthy within $TimeoutSeconds seconds"
    return $false
}

function Wait-ForHealthyServices {
    param (
        [string[]]$Services = @("redis", "chromadb", "studyindexer", "celery-worker", "backend", "frontend")
    )

    Write-Host "Waiting for services to be healthy..." -ForegroundColor Cyan
    
    foreach ($service in $Services) {
        if (-not (Test-ServiceHealth -Service $service -TimeoutSeconds 60)) {
            Write-Error "Service $service failed health check"
            return $false
        }
        Write-Host "Service $service is healthy" -ForegroundColor Green
    }

    return $true
}

function Show-ServiceInformation {
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
    
    # Show data persistence locations
    Write-Host "`nData Persistence Locations:"
    Write-Host "- ChromaDB: ../studyindexer/data/chroma" -ForegroundColor Gray
    Write-Host "- Uploads: ../studyindexer/data/uploads" -ForegroundColor Gray
    Write-Host "- Backend DB: ../studyhub/backend/instance/studyhub.db" -ForegroundColor Gray
} 