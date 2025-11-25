#!/bin/bash

# PostgreSQL Docker Deployment Script
# Automatically sets up PostgreSQL in Docker with your project configuration

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          PostgreSQL Docker Setup for Cloud Deploy          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration (matching your .env)
DB_NAME="social_media_pipeline"
DB_USER="sa"
DB_PASS="Mercury1_2"
DB_PORT="5432"
CONTAINER_NAME="social_media_postgres"
VOLUME_NAME="postgres_data"

# Step 1: Check Docker
echo -e "${YELLOW}[1/5] Checking Docker installation...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    
    # Detect OS
    if [ -f /etc/debian_version ]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    else
        echo -e "${RED}✗ Please install Docker manually: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker installed${NC}"
    echo -e "${YELLOW}⚠ You may need to log out and back in for Docker permissions${NC}"
else
    echo -e "${GREEN}✓ Docker is installed${NC}"
fi

# Check Docker is running
if ! docker ps &> /dev/null; then
    echo -e "${YELLOW}Starting Docker service...${NC}"
    sudo systemctl start docker || true
    sleep 2
fi

# Step 2: Check for existing container
echo ""
echo -e "${YELLOW}[2/5] Checking for existing PostgreSQL container...${NC}"

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠ Container '${CONTAINER_NAME}' already exists${NC}"
    echo -e "${YELLOW}Options:${NC}"
    echo "  1) Stop and remove (data will be preserved in volume)"
    echo "  2) Skip and use existing"
    echo "  3) Remove everything including data"
    read -p "Choose (1/2/3): " -r CHOICE
    
    case $CHOICE in
        1)
            echo -e "${YELLOW}Stopping and removing container...${NC}"
            docker stop ${CONTAINER_NAME} 2>/dev/null || true
            docker rm ${CONTAINER_NAME} 2>/dev/null || true
            echo -e "${GREEN}✓ Old container removed (data preserved)${NC}"
            ;;
        2)
            echo -e "${GREEN}✓ Using existing container${NC}"
            docker start ${CONTAINER_NAME} 2>/dev/null || true
            echo ""
            echo -e "${GREEN}PostgreSQL is ready!${NC}"
            echo ""
            echo "Connection: postgresql://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}"
            echo "Container: ${CONTAINER_NAME}"
            exit 0
            ;;
        3)
            echo -e "${RED}Removing container and data...${NC}"
            docker stop ${CONTAINER_NAME} 2>/dev/null || true
            docker rm ${CONTAINER_NAME} 2>/dev/null || true
            docker volume rm ${VOLUME_NAME} 2>/dev/null || true
            echo -e "${GREEN}✓ Everything removed${NC}"
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# Step 3: Pull PostgreSQL image
echo ""
echo -e "${YELLOW}[3/5] Pulling PostgreSQL 14 image...${NC}"
docker pull postgres:14
echo -e "${GREEN}✓ Image pulled${NC}"

# Step 4: Create volume and run container
echo ""
echo -e "${YELLOW}[4/5] Creating volume and starting PostgreSQL...${NC}"

# Create volume
docker volume create ${VOLUME_NAME} > /dev/null
echo -e "${GREEN}✓ Volume created: ${VOLUME_NAME}${NC}"

# Run PostgreSQL container
docker run -d \
  --name ${CONTAINER_NAME} \
  --restart unless-stopped \
  -e POSTGRES_DB=${DB_NAME} \
  -e POSTGRES_USER=${DB_USER} \
  -e POSTGRES_PASSWORD=${DB_PASS} \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -p ${DB_PORT}:5432 \
  -v ${VOLUME_NAME}:/var/lib/postgresql/data \
  postgres:14

echo -e "${GREEN}✓ Container started: ${CONTAINER_NAME}${NC}"

# Step 5: Wait and verify
echo ""
echo -e "${YELLOW}[5/5] Verifying PostgreSQL is ready...${NC}"
echo -e "${YELLOW}Waiting for PostgreSQL to initialize...${NC}"

MAX_TRIES=30
TRIES=0

while [ $TRIES -lt $MAX_TRIES ]; do
    if docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is ready!${NC}"
        break
    fi
    TRIES=$((TRIES+1))
    sleep 1
    echo -n "."
done

if [ $TRIES -eq $MAX_TRIES ]; then
    echo ""
    echo -e "${RED}✗ PostgreSQL failed to start. Check logs:${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Test connection
echo ""
echo -e "${YELLOW}Testing database connection...${NC}"
if docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Cannot connect to database${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              PostgreSQL Docker Setup Complete!             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Container:${NC} ${CONTAINER_NAME}"
echo -e "${GREEN}✓ Database:${NC} ${DB_NAME}"
echo -e "${GREEN}✓ User:${NC} ${DB_USER}"
echo -e "${GREEN}✓ Password:${NC} ${DB_PASS}"
echo -e "${GREEN}✓ Port:${NC} ${DB_PORT}"
echo -e "${GREEN}✓ Volume:${NC} ${VOLUME_NAME}"
echo ""
echo -e "${YELLOW}Connection String:${NC}"
echo "postgresql://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}"
echo ""
echo -e "${YELLOW}For AsyncPG (FastAPI):${NC}"
echo "postgresql+asyncpg://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:    ${GREEN}docker logs -f ${CONTAINER_NAME}${NC}"
echo "  Stop:         ${GREEN}docker stop ${CONTAINER_NAME}${NC}"
echo "  Start:        ${GREEN}docker start ${CONTAINER_NAME}${NC}"
echo "  Restart:      ${GREEN}docker restart ${CONTAINER_NAME}${NC}"
echo "  Connect:      ${GREEN}docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME}${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Your .env file should have:"
echo "     ${GREEN}DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASS}@localhost:${DB_PORT}/${DB_NAME}${NC}"
echo ""
echo "  2. Run the setup script:"
echo "     ${GREEN}./setup.sh${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
