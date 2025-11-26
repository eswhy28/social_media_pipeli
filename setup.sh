#!/bin/bash

# Social Media Analytics Pipeline - Automated Setup Script
# This script sets up the entire application with PostgreSQL

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Social Media Analytics Pipeline - Setup Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Step 1: Check Python version
echo -e "${YELLOW}[1/11] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}✗ Python 3.10+ is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Step 2: Check PostgreSQL
echo ""
echo -e "${YELLOW}[2/11] Checking PostgreSQL...${NC}"

# Check if PostgreSQL is running in Docker
DOCKER_POSTGRES_RUNNING=false
DOCKER_CMD="docker"
POSTGRES_CONTAINER=""

if command -v docker &> /dev/null; then
    # Try without sudo first
    # Check for common PostgreSQL container names
    for container_name in "postgres" "social_media_postgres"; do
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container_name}$"; then
            echo -e "${GREEN}✓ PostgreSQL running in Docker (container: ${container_name})${NC}"
            DOCKER_POSTGRES_RUNNING=true
            DOCKER_CMD="docker"
            POSTGRES_CONTAINER="${container_name}"
            break
        fi
    done

    # Try with sudo if permission denied or not found yet
    if [ "$DOCKER_POSTGRES_RUNNING" = false ]; then
        for container_name in "postgres" "social_media_postgres"; do
            if sudo docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container_name}$"; then
                echo -e "${GREEN}✓ PostgreSQL running in Docker (container: ${container_name})${NC}"
                echo -e "${YELLOW}⚠ Using sudo for Docker commands${NC}"
                DOCKER_POSTGRES_RUNNING=true
                DOCKER_CMD="sudo docker"
                POSTGRES_CONTAINER="${container_name}"
                break
            fi
        done
    fi
fi

if [ "$DOCKER_POSTGRES_RUNNING" = true ]; then
    # Use appropriate docker command for all PostgreSQL operations
    PSQL_CMD="${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql"
    PG_DUMP_CMD="${DOCKER_CMD} exec ${POSTGRES_CONTAINER} pg_dump"
fi

# If not in Docker, check for local PostgreSQL
if [ "$DOCKER_POSTGRES_RUNNING" = false ]; then
    if command -v psql &> /dev/null; then
        PG_VERSION=$(psql --version | awk '{print $3}')
        echo -e "${GREEN}✓ PostgreSQL $PG_VERSION installed (local)${NC}"
        PSQL_CMD="psql"
        PG_DUMP_CMD="pg_dump"
    else
        echo -e "${RED}✗ PostgreSQL not found${NC}"
        echo ""
        echo "Please install PostgreSQL 14 or higher:"
        echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
        echo "  macOS: brew install postgresql@14"
        echo ""
        echo "OR run PostgreSQL in Docker:"
        echo "  ${GREEN}./deploy_postgres_docker.sh${NC}"
        echo ""
        echo "OR use the one-liner:"
        echo "  ${GREEN}sudo docker run -d --name social_media_postgres --restart unless-stopped \\${NC}"
        echo "    ${GREEN}-e POSTGRES_DB=social_media_pipeline -e POSTGRES_USER=sa \\${NC}"
        echo "    ${GREEN}-e POSTGRES_PASSWORD=Mercury1_2 -p 5432:5432 \\${NC}"
        echo "    ${GREEN}-v postgres_data:/var/lib/postgresql/data postgres:14${NC}"
        echo ""
        echo "If Docker is installed but you got a permission error:"
        echo "  ${YELLOW}sudo usermod -aG docker $USER${NC}"
        echo "  Then log out and back in, or run:"
        echo "  ${YELLOW}newgrp docker${NC}"
        exit 1
    fi
fi

# Step 3: Create virtual environment
echo ""
echo -e "${YELLOW}[3/11] Setting up Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Step 4: Install Python dependencies
echo ""
echo -e "${YELLOW}[4/11] Installing Python dependencies...${NC}"
echo -e "${YELLOW}This may take a few minutes on first run...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 5: Install SpaCy model
echo ""
echo -e "${YELLOW}[5/11] Installing SpaCy language model...${NC}"
echo -e "${YELLOW}Downloading language model (this may take a moment)...${NC}"
python -m spacy download en_core_web_sm
echo -e "${GREEN}✓ SpaCy model installed${NC}"

# Step 6: Configure environment
echo ""
echo -e "${YELLOW}[6/11] Configuring environment...${NC}"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from template${NC}"
    else
        echo -e "${YELLOW}⚠ No .env.example found, using defaults${NC}"
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
EOF
        echo -e "${GREEN}✓ Created default .env${NC}"
    fi
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

# Step 7: Setup database
echo ""
echo -e "${YELLOW}[7/11] Setting up database...${NC}"

# Extract database details from .env
DB_NAME="social_media_pipeline"
DB_USER="sa"
DB_PASS="Mercury1_2"
DB_HOST="localhost"
DB_PORT="5432"

# Check if database exists
if [ "$DOCKER_POSTGRES_RUNNING" = true ]; then
    # Using Docker PostgreSQL
    echo -e "${YELLOW}Checking if database exists...${NC}"
    
    # Check if database exists (query as postgres user inside container)
    DB_EXISTS=$(${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")

    if [ "$DB_EXISTS" = "1" ]; then
        echo -e "${GREEN}✓ Database '$DB_NAME' already exists${NC}"
    else
        echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
        
        # Create database and user in Docker (using postgres superuser)
        echo -e "${YELLOW}  - Creating database...${NC}"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -c "CREATE DATABASE $DB_NAME;" 2>&1 | grep -v "already exists" || true

        echo -e "${YELLOW}  - Creating user...${NC}"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>&1 | grep -v "already exists" || true

        echo -e "${YELLOW}  - Granting privileges...${NC}"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || echo "    (skipped)"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;" 2>/dev/null || echo "    (skipped)"

        # Grant schema permissions for PostgreSQL 15+
        echo -e "${YELLOW}  - Setting schema permissions...${NC}"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || echo "    (skipped)"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;" 2>/dev/null || echo "    (skipped)"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;" 2>/dev/null || echo "    (skipped)"

        echo -e "${GREEN}✓ Database setup completed${NC}"
    fi
    
    # Test database connection using Docker
    echo ""
    echo -e "${YELLOW}Testing database connection...${NC}"

    # First verify the database was created
    VERIFY_DB=$(${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")
    if [ "$VERIFY_DB" != "1" ]; then
        echo -e "${RED}✗ Database '$DB_NAME' was not created properly${NC}"
        echo -e "${YELLOW}Please check the Docker container logs:${NC}"
        echo -e "  ${GREEN}${DOCKER_CMD} logs ${POSTGRES_CONTAINER}${NC}"
        exit 1
    fi

    # Test connection as the application user
    if ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database connection successful${NC}"
    else
        echo -e "${YELLOW}⚠ Cannot connect as user '$DB_USER', attempting permission fix...${NC}"
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true
        ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U postgres -d $DB_NAME -c "GRANT ALL ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true

        if ${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Database connection successful after permission fix${NC}"
        else
            echo -e "${RED}✗ Still cannot connect to database${NC}"
            echo -e "${YELLOW}Debugging info:${NC}"
            echo -e "  Database: $DB_NAME"
            echo -e "  User: $DB_USER"
            echo -e "  Container: ${POSTGRES_CONTAINER}"
            echo ""
            echo -e "${YELLOW}Try manually:${NC}"
            echo -e "  ${GREEN}${DOCKER_CMD} exec -it ${POSTGRES_CONTAINER} psql -U postgres${NC}"
            exit 1
        fi
    fi
else
    # Using local PostgreSQL
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo -e "${GREEN}✓ Database '$DB_NAME' already exists${NC}"
    else
        echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
        
        # Create database and user
        sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
\q
EOF
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Database created successfully${NC}"
        else
            echo -e "${RED}✗ Failed to create database${NC}"
            echo ""
            echo "Please create the database manually:"
            echo "  sudo -u postgres psql"
            echo "  CREATE DATABASE $DB_NAME;"
            echo "  CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
            echo "  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
            echo "  \\q"
            exit 1
        fi
    fi
    
    # Test database connection
    echo -e "${YELLOW}Testing database connection...${NC}"
    if PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database connection successful${NC}"
    else
        echo -e "${RED}✗ Cannot connect to database${NC}"
        echo "Please check your PostgreSQL configuration"
        exit 1
    fi
fi

# Step 8: Initialize database tables
echo ""
echo -e "${YELLOW}[8/11] Initializing database tables...${NC}"

if [ -f "scripts/create_ai_tables.py" ]; then
    python scripts/create_ai_tables.py > /dev/null 2>&1
    echo -e "${GREEN}✓ Database tables created${NC}"
else
    echo -e "${YELLOW}⚠ Table creation script not found, skipping...${NC}"
fi

# Step 9: Import JSON data to PostgreSQL
echo ""
echo -e "${YELLOW}[9/11] Importing JSON data to PostgreSQL...${NC}"

if [ -d "data" ] && [ "$(ls -A data/*.json 2>/dev/null)" ]; then
    JSON_COUNT=$(find data -name "*.json" -type f | wc -l)
    echo -e "${YELLOW}Found $JSON_COUNT JSON file(s) in data directory${NC}"
    echo -e "${YELLOW}Importing data to PostgreSQL database...${NC}"
    
    if [ -f "scripts/import_data.py" ]; then
        python scripts/import_data.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Data imported successfully${NC}"
            DATA_IMPORTED=true
        else
            echo -e "${RED}✗ Data import failed${NC}"
            DATA_IMPORTED=false
        fi
    else
        echo -e "${RED}✗ Import script not found: scripts/import_data.py${NC}"
        DATA_IMPORTED=false
    fi
else
    echo -e "${YELLOW}⚠ No JSON files found in data directory${NC}"
    echo -e "${YELLOW}Skipping data import${NC}"
    DATA_IMPORTED=false
fi

# Step 10: Run AI Processing on imported data
if [ "$DATA_IMPORTED" = true ]; then
    echo ""
    echo -e "${YELLOW}[10/11] Running AI analysis on imported data...${NC}"
    echo -e "${YELLOW}This may take a few minutes depending on data size...${NC}"
    
    if [ -f "scripts/setup_intelligence_system.py" ]; then
        echo ""
        echo -e "${BLUE}═══ AI Processing Started ═══${NC}"
        python scripts/setup_intelligence_system.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ AI processing completed successfully${NC}"
        else
            echo -e "${YELLOW}⚠ AI processing completed with some warnings${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ AI processing script not found: scripts/setup_intelligence_system.py${NC}"
        echo -e "${YELLOW}You can run AI processing later with:${NC}"
        echo -e "${GREEN}python scripts/setup_intelligence_system.py${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}[10/11] Skipping AI processing (no data imported)${NC}"
fi

# Step 11: Verify setup
echo ""
echo -e "${YELLOW}[11/11] Verifying setup...${NC}"

# Check database for data using appropriate command
if [ "$DOCKER_POSTGRES_RUNNING" = true ]; then
    RECORD_COUNT=$(${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM apify_scraped_data;" 2>/dev/null | xargs)
else
    RECORD_COUNT=$(PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM apify_scraped_data;" 2>/dev/null | xargs)
fi

if [ -n "$RECORD_COUNT" ] && [ "$RECORD_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Database contains $RECORD_COUNT records${NC}"
    
    # Check for AI analysis
    if [ "$DOCKER_POSTGRES_RUNNING" = true ]; then
        SENTIMENT_COUNT=$(${DOCKER_CMD} exec ${POSTGRES_CONTAINER} psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM apify_sentiment_analysis;" 2>/dev/null | xargs)
    else
        SENTIMENT_COUNT=$(PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM apify_sentiment_analysis;" 2>/dev/null | xargs)
    fi
    
    if [ -n "$SENTIMENT_COUNT" ] && [ "$SENTIMENT_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ AI analysis complete: $SENTIMENT_COUNT sentiment records${NC}"
    else
        echo -e "${YELLOW}⚠ No AI analysis data found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Database is empty${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  Setup Complete!                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Python Environment:${NC} venv"
echo -e "${GREEN}✓ Database:${NC} PostgreSQL ($DB_NAME)"
echo -e "${GREEN}✓ Dependencies:${NC} Installed"
echo -e "${GREEN}✓ Tables:${NC} Created"

if [ "$DATA_IMPORTED" = true ]; then
    echo -e "${GREEN}✓ Data:${NC} $RECORD_COUNT records imported"
    if [ -n "$SENTIMENT_COUNT" ] && [ "$SENTIMENT_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ AI Analysis:${NC} $SENTIMENT_COUNT records processed"
    fi
else
    echo -e "${YELLOW}⚠ Data:${NC} No data imported"
fi

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "  1. Activate virtual environment:"
echo -e "     ${GREEN}source venv/bin/activate${NC}"
echo ""
echo -e "  2. Start the API server:"
echo -e "     ${GREEN}./start_server.sh${NC}"
echo -e "     or"
echo -e "     ${GREEN}uvicorn app.main:app --reload${NC}"
echo ""
echo -e "  3. Access API documentation:"
echo -e "     ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  4. Test the API:"
echo -e "     ${GREEN}curl http://localhost:8000/health${NC}"
echo ""

if [ -n "$RECORD_COUNT" ] && [ "$RECORD_COUNT" -gt 0 ]; then
    echo -e "  5. Test data endpoints:"
    echo -e "     ${GREEN}curl http://localhost:8000/api/v1/social-media/data/scraped?limit=10${NC}"
    echo -e "     ${GREEN}curl http://localhost:8000/api/v1/social-media/data/with-media?limit=10${NC}"
    echo ""
fi

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Optional: Start server now
echo -e "${YELLOW}Start the API server now? (y/N)${NC}"
read -r START_NOW
if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}Starting API server...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
