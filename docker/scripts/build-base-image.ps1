# Build base ML image for faster deployments
param(
    [string]$Tag = "latest",
    [switch]$Push,
    [string]$Registry = "localhost:5000"  # Use local registry by default
)

# Ensure we're in the docker directory
Set-Location $PSScriptRoot/..

# Create base.Dockerfile if it doesn't exist
$baseDockerfile = @"
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    curl \
    git \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install heavy ML dependencies
RUN pip install --no-cache-dir \
    torch==2.0.0 \
    transformers==4.35.2 \
    sentence-transformers==2.2.2 \
    huggingface-hub==0.19.4

# Pre-download models
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Set environment variables
ENV PYTHONUNBUFFERED=1
"@

$baseDockerfile | Out-File -FilePath "base.Dockerfile" -Encoding utf8

# Build the base image
$imageName = "studyhub-base:$Tag"
Write-Host "Building base image: $imageName" -ForegroundColor Cyan
docker build -t $imageName -f base.Dockerfile .

if ($Push) {
    $remoteImage = "$Registry/$imageName"
    Write-Host "Pushing image to registry: $remoteImage" -ForegroundColor Cyan
    docker tag $imageName $remoteImage
    docker push $remoteImage
}

Write-Host "`nBase image built successfully!" -ForegroundColor Green
Write-Host "To use this image:"
Write-Host "1. Update your Dockerfile to use: FROM $imageName"
Write-Host "2. Remove ML dependencies from requirements.txt" 