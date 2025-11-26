#!/bin/bash

# Manual Database Setup Script
# Use this if the automatic setup fails

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Manual Database Setup for Social Media Pipeline${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Configuration
DB_NAME="social_media_pipeline"
DB_USER="sa"
DB_PASS="Mercury1_2"

# Detect Docker container
CONTAINER_NAME=""
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^postgres$"; then
    CONTAINER_NAME="postgres"
elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^social_media_postgres$"; then
    CONTAINER_NAME="social_media_postgres"
else
    echo -e "${RED}✗ No PostgreSQL Docker container found${NC}"
    echo ""
    echo "Please start a PostgreSQL container first:"
    echo "  docker run -d --name postgres -p 5432:5432 \\"
    echo "    -e POSTGRES_PASSWORD=postgres \\"
    echo "    postgres:16"
    exit 1
fi

echo -e "${GREEN}✓ Found PostgreSQL container: $CONTAINER_NAME${NC}"
echo ""

# Step 1: Check if database exists
echo -e "${YELLOW}[1/5] Checking existing database...${NC}"
DB_EXISTS=$(docker exec $CONTAINER_NAME psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Database '$DB_NAME' already exists${NC}"
else
    echo -e "${YELLOW}⚠ Database '$DB_NAME' does not exist${NC}"
fi

# Step 2: Create database
echo ""
echo -e "${YELLOW}[2/5] Creating database...${NC}"
docker exec $CONTAINER_NAME psql -U postgres -c "CREATE DATABASE $DB_NAME;" 2>&1 | grep -v "already exists" || echo -e "${GREEN}✓ Database created (or already exists)${NC}"

# Step 3: Create user
echo ""
echo -e "${YELLOW}[3/5] Creating user '$DB_USER'...${NC}"
docker exec $CONTAINER_NAME psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>&1 | grep -v "already exists" || echo -e "${GREEN}✓ User created (or already exists)${NC}"

# Step 4: Grant permissions
echo ""
echo -e "${YELLOW}[4/5] Granting permissions...${NC}"

docker exec $CONTAINER_NAME psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
docker exec $CONTAINER_NAME psql -U postgres -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

# PostgreSQL 15+ schema permissions
docker exec $CONTAINER_NAME psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
docker exec $CONTAINER_NAME psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
docker exec $CONTAINER_NAME psql -U postgres -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
docker exec $CONTAINER_NAME psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
docker exec $CONTAINER_NAME psql -U postgres -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

echo -e "${GREEN}✓ Permissions granted${NC}"

# Step 5: Test connection
echo ""
echo -e "${YELLOW}[5/5] Testing database connection...${NC}"

if docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connection successful!${NC}"

    # Show database info
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Database Setup Complete!${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "Database Name: ${GREEN}$DB_NAME${NC}"
    echo -e "Database User: ${GREEN}$DB_USER${NC}"
    echo -e "Database Pass: ${GREEN}$DB_PASS${NC}"
    echo -e "Container:     ${GREEN}$CONTAINER_NAME${NC}"
    echo ""
    echo -e "Connection string:"
    echo -e "  ${GREEN}postgresql://sa:Mercury1_2@localhost:5432/social_media_pipeline${NC}"
    echo ""
    echo -e "Test connection from host:"
    echo -e "  ${GREEN}docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME${NC}"
    echo ""
else
    echo -e "${RED}✗ Connection failed${NC}"
    echo ""
    echo "Debug commands:"
    echo "  docker exec -it $CONTAINER_NAME psql -U postgres"
    echo "  docker logs $CONTAINER_NAME"
    exit 1
fi


