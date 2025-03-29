#!/bin/bash

# Exit on error
set -e

echo "Setting up StudyIndexerNew in WSL..."

# Update package lists and install required dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential python3-dev

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install core build dependencies first
echo "Installing build dependencies..."
pip install --upgrade pip
pip install setuptools wheel

# Install from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install ChromaDB client separately if needed
echo "Ensuring ChromaDB is properly installed..."
pip install chromadb==0.4.22

# Install the package in development mode
echo "Installing StudyIndexerNew in development mode..."
pip install -e .

# Create required directories
echo "Creating required directories..."
mkdir -p data/chroma logs

echo "Setup complete! You can now run the application with:"
echo "python manage_services.py start" 