# StudyHub Frontend Setup Script

# Check Node.js installation
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js is required but not installed."
    Write-Host "Please install Node.js from https://nodejs.org/"
    exit 1
}

# Check npm installation
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: npm is required but not installed."
    Write-Host "Please install Node.js which includes npm."
    exit 1
}

# Check package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "Error: package.json not found in current directory"
    Write-Host "Please ensure you're in the correct directory with the React project"
    exit 1
}

# Check existing processes
$existingProcess = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*react-scripts start*' }
if ($existingProcess) {
    Write-Host "Warning: Found existing frontend process. Stopping it..."
    Stop-Process -Id $existingProcess.Id -Force
    Start-Sleep -Seconds 2
}

# Create necessary directories
Write-Host "Creating required directories..."
$directories = @(
    "public",      # Public assets
    "src",         # Source code
    "build",       # Production build
    "logs"         # Application logs
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}

# Install dependencies with better error handling
Write-Host "Installing npm dependencies..."
$npmOutput = npm install 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: npm install failed with the following output:"
    Write-Host $npmOutput
    exit 1
}

# Create environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from example..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "Warning: .env.example not found. Please create .env file manually."
    }
}

# Build the project with error handling
Write-Host "Building the project..."
$buildOutput = npm run build 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Build failed with the following output:"
    Write-Host $buildOutput
    exit 1
}

Write-Host "`nFrontend setup completed successfully!"
Write-Host "You can now run 'npm start' to start the development server."
Write-Host "Or 'npm run build' to create a production build." 