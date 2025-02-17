# Project Reorganization Script

# Create backup
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd')"
Write-Host "Creating backup in $backupDir..."
New-Item -ItemType Directory -Path $backupDir -Force

# Backup current files
Copy-Item "data" "$backupDir/data" -Recurse -Force
Copy-Item "logs" "$backupDir/logs" -Recurse -Force
Copy-Item "README.md" "$backupDir/README.md" -Force
Copy-Item "README.txt" "$backupDir/README.txt" -Force
Copy-Item "setup.py" "$backupDir/setup.py" -Force
Copy-Item "start.ps1" "$backupDir/start.ps1" -Force

# Create new directory structure
Write-Host "Creating new directory structure..."
$directories = @(
    "studyhub/backend",
    "studyhub/frontend",
    "studyindexer/data",
    "studyindexer/logs",
    "studyai"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}

# Move studyindexer files
Write-Host "Moving StudyIndexer files..."
# Move data directory
if (Test-Path "data") {
    if (-not (Test-Path "studyindexer/data")) {
        Move-Item "data/*" "studyindexer/data/" -Force
    } else {
        Write-Host "Merging data directories..."
        Copy-Item "data/*" "studyindexer/data/" -Recurse -Force
    }
    Remove-Item "data" -Recurse -Force
}

# Move logs directory
if (Test-Path "logs") {
    if (-not (Test-Path "studyindexer/logs")) {
        Move-Item "logs/*" "studyindexer/logs/" -Force
    } else {
        Write-Host "Merging logs directories..."
        Copy-Item "logs/*" "studyindexer/logs/" -Recurse -Force
    }
    Remove-Item "logs" -Recurse -Force
}

# Move setup files
if (Test-Path "setup.py") {
    Move-Item "setup.py" "studyindexer/" -Force
}
if (Test-Path "start.ps1") {
    Move-Item "start.ps1" "studyindexer/" -Force
}
if (Test-Path "README.md") {
    Move-Item "README.md" "studyindexer/" -Force
}
if (Test-Path "README.txt") {
    Remove-Item "README.txt" -Force  # Remove duplicate README
}

# Create StudyAI placeholder
Write-Host "Creating StudyAI placeholder..."
Set-Content "studyai/README.md" @"
# StudyAI Service

Future AI service component for StudyHub platform.

## Planned Features
- AI-powered study assistance
- Content recommendations
- Learning path optimization
- Personalized tutoring

## Status
This module is planned for future development.
"@

Write-Host "Project reorganization completed!"
Write-Host "Backup created in: $backupDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review the new structure"
Write-Host "2. Run setup scripts for each component:"
Write-Host "   - studyhub/backend/setup.ps1"
Write-Host "   - studyhub/frontend/setup.ps1"
Write-Host "   - studyindexer/setup.ps1" 