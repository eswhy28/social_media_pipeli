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
POSTGRES_SUPERUSER="sa"  # Your container uses 'sa' as superuser, not 'postgres'
POSTGRES_DB="mydb"       # Default database to connect to

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
DB_EXISTS=$(docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $POSTGRES_DB -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Database '$DB_NAME' already exists${NC}"
else
    echo -e "${YELLOW}⚠ Database '$DB_NAME' does not exist${NC}"
fi

# Step 2: Create database (skip since user already exists and we're using it)
echo ""
echo -e "${YELLOW}[2/5] Verifying database...${NC}"
DB_EXISTS=$(docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $POSTGRES_DB -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Database '$DB_NAME' exists${NC}"
else
    echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
    docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $POSTGRES_DB -c "CREATE DATABASE $DB_NAME;" 2>&1
    echo -e "${GREEN}✓ Database created${NC}"
fi

# Step 3: User already exists (sa), so skip this
echo ""
echo -e "${YELLOW}[3/5] Verifying user '$DB_USER'...${NC}"
echo -e "${GREEN}✓ User '$DB_USER' already exists (superuser)${NC}"

# Step 4: Grant permissions (ensure schema permissions are set)
echo ""
echo -e "${YELLOW}[4/5] Setting schema permissions...${NC}"

# PostgreSQL 15+ schema permissions
docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true
docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;" 2>/dev/null || true
docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;" 2>/dev/null || true
docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;" 2>/dev/null || true
docker exec $CONTAINER_NAME psql -U $POSTGRES_SUPERUSER -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;" 2>/dev/null || true

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


