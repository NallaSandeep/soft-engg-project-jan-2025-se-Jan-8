# Check for existing Python processes
$existingProcesses = Get-Process python -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like '*wsgi.py*' }
if ($existingProcesses) {
    Write-Host "Warning: Found existing Python processes. Stopping them..."
    $existingProcesses | ForEach-Object {
        Write-Host "Stopping process $($_.Id)..."
        Stop-Process -Id $_.Id -Force
    }
    Start-Sleep -Seconds 2  # Wait for processes to stop
}

# Activate virtual environment if not already activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..."
    .\.venv\Scripts\Activate
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found. Please run setup.ps1 first."
    exit 1
}

# Global variable to track the main process
$script:mainProcess = $null

# Function to handle cleanup on exit
function Cleanup {
    param(
        [switch]$FromSignal
    )
    
    Write-Host "`nStopping Backend service..."
    
    # Stop the main process if it exists
    if ($script:mainProcess -and -not $script:mainProcess.HasExited) {
        Write-Host "Stopping main process..."
        taskkill /PID $script:mainProcess.Id /T /F | Out-Null
    }
    
    # Find and stop any remaining Python processes
    $remainingProcesses = Get-Process python -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like '*wsgi.py*' }
    if ($remainingProcesses) {
        Write-Host "Cleaning up remaining processes..."
        $remainingProcesses | ForEach-Object {
            Write-Host "Stopping process $($_.Id)..."
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    # If called from signal handler, we need to exit explicitly
    if ($FromSignal) {
        exit 0
    }
}

# Set up Ctrl+C handler
$job = Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action {
    Write-Host "Received shutdown signal..."
    Cleanup -FromSignal
}

Write-Host "Starting Backend service..."
Write-Host "API will be available at: http://localhost:5000"
Write-Host "Press Ctrl+C to stop the server"

try {
    # Start the process
    $env:PYTHONUNBUFFERED = "1"  # Ensure Python output is not buffered
    $script:mainProcess = Start-Process -FilePath "python" -ArgumentList "wsgi.py" -NoNewWindow -PassThru
    
    # Wait for the process to exit
    $script:mainProcess.WaitForExit()
    
    if ($script:mainProcess.ExitCode -ne 0) {
        Write-Host "Process terminated with error code: $($script:mainProcess.ExitCode)"
    }
} catch {
    Write-Host "Error running application: $_"
    exit 1
} finally {
    # Clean up the event handler
    Unregister-Event -SourceIdentifier $job.Name
    Remove-Job -Job $job -Force
    
    # Ensure cleanup happens
    Cleanup
} 