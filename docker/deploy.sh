#!/bin/bash

# Deployment script for StudyHub
# Usage: ./deploy.sh [--pull-only]

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/opt/studyhub"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Vultr Registry Configuration
REGISTRY_URL="blr.vultrcr.com/dockerbangalore"
REGISTRY_USER="e6beec2c-0ef9-4f1b-9261-c42f3ec4b207"
REGISTRY_PASSWORD="K3x7Jmh7JtBz5MAHXUNtZgcsWXCRwY5VY7te"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting StudyHub deployment...${NC}"

# Login to Vultr Registry
echo -e "${YELLOW}Logging into Vultr Container Registry...${NC}"
echo $REGISTRY_PASSWORD | docker login $REGISTRY_URL -u $REGISTRY_USER --password-stdin

# Create project directory if it doesn't exist
sudo mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone/pull repository
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone https://github.com/NallaSandeep/soft-engg-project-jan-2025-se-Jan-8.git .
else
    echo -e "${YELLOW}Pulling latest changes...${NC}"
    git pull origin project-dev
fi

# Exit if --pull-only flag is provided
if [ "$1" == "--pull-only" ]; then
    echo -e "${GREEN}Pull completed. Exiting without restart.${NC}"
    exit 0
fi

# Copy environment file if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Creating environment file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env file with proper values${NC}"
    exit 1
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create necessary directories with proper permissions
echo -e "${YELLOW}Setting up directories...${NC}"
sudo mkdir -p data/chroma data/uploads data/processed logs
sudo chown -R $USER:$USER data logs

# Build and tag images
echo -e "${YELLOW}Building and tagging images...${NC}"
docker compose build

# Tag images for Vultr registry
echo -e "${YELLOW}Tagging images for Vultr registry...${NC}"
docker tag studyhub-backend:latest $REGISTRY_URL/studyhub-backend:latest
docker tag studyhub-frontend:latest $REGISTRY_URL/studyhub-frontend:latest
docker tag studyhub-indexer:latest $REGISTRY_URL/studyhub-indexer:latest

# Push images to registry
echo -e "${YELLOW}Pushing images to Vultr registry...${NC}"
docker push $REGISTRY_URL/studyhub-backend:latest
docker push $REGISTRY_URL/studyhub-frontend:latest
docker push $REGISTRY_URL/studyhub-indexer:latest

# Pull latest images
echo -e "${YELLOW}Pulling latest Docker images...${NC}"
docker compose pull

# Stop and remove existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker compose down

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"
docker compose ps

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "Services are available at:"
echo -e "Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo -e "Backend API: http://$(hostname -I | awk '{print $1}'):5000"
echo -e "StudyIndexer API: http://$(hostname -I | awk '{print $1}'):8000"

# Logout from registry
docker logout $REGISTRY_URL 