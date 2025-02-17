#!/bin/bash

# Health check script for StudyHub services
# Usage: ./health-check.sh [--notify]

set -e

# Configuration
SERVICES=(
    "frontend:3000"
    "backend:5000/api/health"
    "studyindexer:8000/health"
    "chromadb:8001/api/v1/heartbeat"
)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check individual service
check_service() {
    local service=$1
    local endpoint=$2
    
    echo -e "${YELLOW}Checking $service...${NC}"
    if curl -s "http://localhost:$endpoint" > /dev/null; then
        echo -e "${GREEN}$service is healthy${NC}"
        return 0
    else
        echo -e "${RED}$service is not responding${NC}"
        return 1
    fi
}

# Check Docker status
echo -e "${YELLOW}Checking Docker status...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running${NC}"
    exit 1
fi

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
docker compose ps

# Check Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}Redis is healthy${NC}"
else
    echo -e "${RED}Redis is not responding${NC}"
fi

# Check individual services
failed_services=()
for service in "${SERVICES[@]}"; do
    IFS=':' read -r name endpoint <<< "$service"
    if ! check_service "$name" "$endpoint"; then
        failed_services+=("$name")
    fi
done

# Print summary
echo -e "\n${YELLOW}Health Check Summary:${NC}"
if [ ${#failed_services[@]} -eq 0 ]; then
    echo -e "${GREEN}All services are healthy${NC}"
    exit 0
else
    echo -e "${RED}Failed services: ${failed_services[*]}${NC}"
    
    # If --notify flag is provided, you could add notification logic here
    if [ "$1" == "--notify" ]; then
        # Add your notification logic (e.g., email, Slack, etc.)
        echo "Notification would be sent here"
    fi
    
    exit 1
fi 