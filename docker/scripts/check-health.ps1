# Health check script for StudyHub services
param(
    [switch]$LogToFile,
    [string]$LogPath = "health-check.log"
)

function Write-Log {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Status] $Message"
    Write-Host $logMessage
    
    if ($LogToFile) {
        Add-Content -Path $LogPath -Value $logMessage
    }
}

function Test-ServiceHealth {
    param(
        [string]$Service,
        [string]$Type,
        [string]$Endpoint
    )
    
    Write-Log "Checking $Service..."
    
    try {
        switch ($Type) {
            "redis" {
                $result = docker compose exec redis redis-cli ping
                if ($result -eq "PONG") {
                    Write-Log "$Service is healthy" "SUCCESS"
                    return $true
                }
            }
            "http" {
                $response = Invoke-WebRequest -Uri $Endpoint -UseBasicParsing -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    Write-Log "$Service is healthy (Status: $($response.StatusCode))" "SUCCESS"
                    return $true
                }
            }
            "celery" {
                $result = docker compose exec celery-worker celery -A app.core.celery_app inspect ping
                if ($result -match "pong") {
                    Write-Log "$Service is healthy" "SUCCESS"
                    return $true
                }
            }
        }
    }
    catch {
        Write-Log "$Service health check failed: $_" "ERROR"
        return $false
    }
    
    Write-Log "$Service is not healthy" "ERROR"
    return $false
}

function Get-ServiceStatus {
    Write-Log "Starting health check for all services..." "INFO"
    Write-Log "----------------------------------------" "INFO"
    
    # Check Docker status
    if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
        Write-Log "Docker Desktop is not running!" "ERROR"
        return
    }
    
    # Infrastructure Services
    $redis = Test-ServiceHealth -Service "Redis" -Type "redis"
    $chromadb = Test-ServiceHealth -Service "ChromaDB" -Type "http" -Endpoint "http://localhost:8001/api/v1/heartbeat"
    
    # Application Services
    $backend = Test-ServiceHealth -Service "Backend" -Type "http" -Endpoint "http://localhost:5000/api/health"
    $frontend = Test-ServiceHealth -Service "Frontend" -Type "http" -Endpoint "http://localhost:3000"
    $indexer = Test-ServiceHealth -Service "StudyIndexer" -Type "http" -Endpoint "http://localhost:8000/health"
    $celery = Test-ServiceHealth -Service "Celery Worker" -Type "celery"
    
    # Container Status
    Write-Log "----------------------------------------" "INFO"
    Write-Log "Container Status:" "INFO"
    $containers = docker compose ps --format "table {{.Name}}\t{{.Status}}"
    Write-Log $containers "INFO"
    
    # Summary
    Write-Log "----------------------------------------" "INFO"
    Write-Log "Health Check Summary:" "INFO"
    Write-Log "Redis: $(if ($redis) {'✅ Healthy'} else {'❌ Unhealthy'})" "INFO"
    Write-Log "ChromaDB: $(if ($chromadb) {'✅ Healthy'} else {'❌ Unhealthy'})" "INFO"
    Write-Log "Backend: $(if ($backend) {'✅ Healthy'} else {'❌ Unhealthy'})" "INFO"
    Write-Log "Frontend: $(if ($frontend) {'✅ Healthy'} else {'❌ Unhealthy'})" "INFO"
    Write-Log "StudyIndexer: $(if ($indexer) {'✅ Healthy'} else {'❌ Unhealthy'})" "INFO"
    Write-Log "Celery Worker: $(if ($celery) {'✅ Healthy'} else {'❌ Unhealthy'})" "INFO"
    Write-Log "----------------------------------------" "INFO"
}

# Execute health check
if ($LogToFile) {
    Write-Log "Health check results will be logged to: $LogPath" "INFO"
}

Get-ServiceStatus 