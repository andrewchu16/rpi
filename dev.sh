#!/bin/zsh

# Make the script executable
chmod +x "$0"

# Set colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}  Starting Development Environment  ${NC}"
echo -e "${GREEN}====================================${NC}"

# Clean up any existing containers
echo -e "${BLUE}Stopping any existing containers...${NC}"
docker compose -f compose.dev.yaml down

# Start the development API container
echo -e "${BLUE}Building and starting API container...${NC}"
docker compose -f compose.dev.yaml up --build

echo -e "${YELLOW}To stop the container, run:${NC}"
echo -e "${YELLOW}docker compose -f compose.dev.yaml down${NC}"
