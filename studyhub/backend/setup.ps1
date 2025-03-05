# StudyHub Backend Setup Script

# Check for existing Python processes
$existingProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*wsgi.py*' }
if ($existingProcess) {
    Write-Host "Warning: Found existing backend process. Stopping it..."
    Stop-Process -Id $existingProcess.Id -Force
    Start-Sleep -Seconds 2  # Wait for process to fully stop
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\.venv\Scripts\Activate

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
$dependencies = @(
    "Flask==3.1.0",
    "flask-cors==5.0.0",
    "flask-jwt-extended==4.7.1",
    "flask-migrate==4.1.0",
    "flask-sqlalchemy==3.1.1",
    "sqlalchemy==2.0.37",
    "werkzeug==3.1.3",
    "alembic==1.14.1",
    "python-dotenv==1.0.1",
    "bcrypt==4.0.1",
    "psycopg2-binary==2.9.10",
    "pillow==10.0.0",
    "python-magic==0.4.27",
    "redis==5.0.1",
    "celery==5.3.6",
    "gunicorn==21.2.0",
    "requests==2.31.0",
    "pytest",
    "pytest-flask",
    "black",
    "flake8"
)

$errorCount = 0
foreach ($dep in $dependencies) {
    Write-Host "Installing $dep..."
    pip install $dep
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Failed to install $dep"
        $errorCount++
    }
}

if ($errorCount -gt 0) {
    Write-Host "`nWarning: $errorCount dependencies failed to install. Check the messages above."
}

# Create necessary directories
Write-Host "Creating required directories..."
$directories = @(
    "instance",    # Flask instance directory
    "logs",        # Application logs
    "uploads",     # File uploads
    "migrations"   # Database migrations
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from example..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "Warning: .env.example not found. Please create .env file manually."
    }
}

# Initialize database only if Flask is installed successfully
$flaskCheck = pip list | Select-String "Flask"
if ($flaskCheck) {
    Write-Host "Initializing database..."
    python scripts/init_db.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Database initialization failed. Please check the error message above."
    }
} else {
    Write-Host "Error: Flask installation failed. Please check the error messages above."
    exit 1
}

Write-Host "`nSetup completed successfully!"
Write-Host "You can now run '.\start.ps1' to start the server." 