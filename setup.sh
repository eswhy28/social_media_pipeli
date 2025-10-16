#!/bin/bash

# Social Media Pipeline - Automated Setup Script
# This script sets up the entire application automatically

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}  SOCIAL MEDIA PIPELINE - AUTOMATED SETUP${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

# Check if script is run from project directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Step 1: Check Python version
print_step "Step 1/8: Checking Python version..."
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 9 ]; then
            PYTHON_CMD=$cmd
            print_success "Found Python $VERSION"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python 3.9 or higher is required"
    print_info "Install Python 3.9+: https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Check Redis
print_step "Step 2/8: Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis is running"
    else
        print_info "Redis is installed but not running"
        print_info "Starting Redis..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis 2>/dev/null || redis-server --daemonize yes
        else
            redis-server --daemonize yes
        fi
        sleep 2
        if redis-cli ping &> /dev/null; then
            print_success "Redis started successfully"
        else
            print_error "Could not start Redis. Please start it manually: redis-server"
        fi
    fi
else
    print_info "Redis not found. Installing via Docker..."
    if command -v docker &> /dev/null; then
        docker run -d -p 6379:6379 --name redis-social-media redis:alpine
        print_success "Redis started in Docker"
    else
        print_error "Redis not found. Please install Redis:"
        print_info "Ubuntu/Debian: sudo apt-get install redis-server"
        print_info "macOS: brew install redis"
        print_info "Docker: docker run -d -p 6379:6379 redis:alpine"
    fi
fi

# Step 3: Create virtual environment
print_step "Step 3/8: Creating virtual environment..."
if [ -d "venv" ]; then
    print_info "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
print_success "Virtual environment created"

# Step 4: Activate virtual environment and upgrade pip
print_step "Step 4/8: Activating virtual environment..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_success "Virtual environment activated"

# Step 5: Install dependencies
print_step "Step 5/8: Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "All dependencies installed successfully"
else
    print_error "Failed to install some dependencies. Check requirements.txt"
    exit 1
fi

# Step 6: Download TextBlob corpora
print_step "Step 6/8: Downloading NLP data..."
python -m textblob.download_corpora > /dev/null 2>&1
print_success "NLP corpora downloaded"

# Step 7: Initialize database
print_step "Step 7/8: Initializing database..."
python3 << 'PYEOF'
import asyncio
import sys

async def init_db():
    try:
        # Import all models
        from app.models import (
            User, SocialPost, SentimentTimeSeries, TrendingTopic,
            AnomalyDetection, APIRateLimit, Hashtag, Keyword,
            Influencer, Anomaly, GeographicData, AlertRule,
            DataConnector, Report
        )
        from app.database import Base, engine

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Verify
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]

        await engine.dispose()
        print(f"Database initialized with {len(tables)} tables")
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

success = asyncio.run(init_db())
sys.exit(0 if success else 1)
PYEOF

if [ $? -eq 0 ]; then
    print_success "Database initialized with all tables"
else
    print_error "Database initialization failed"
    exit 1
fi

# Step 8: Create .env file if it doesn't exist
print_step "Step 8/8: Creating environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
    else
        # Create a basic .env file
        cat > .env << 'ENVEOF'
# App Settings
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Twitter API - Get from: https://developer.twitter.com/en/portal/dashboard
TWITTER_BEARER_TOKEN=

# Database (SQLite - local)
DATABASE_URL=sqlite+aiosqlite:///./social_media.db

# Redis (local)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security - Change in production!
SECRET_KEY=change-this-to-a-random-secret-key-in-production-$(openssl rand -hex 32)

# CORS Origins
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
ENVEOF
        print_success "Created default .env file"
    fi

    print_info ""
    print_info "⚠️  IMPORTANT: Add your Twitter API Bearer Token to .env file"
    print_info "   Edit .env and set: TWITTER_BEARER_TOKEN=your_token_here"
    print_info "   Get token from: https://developer.twitter.com/en/portal/dashboard"
else
    print_success ".env file already exists"
fi

# Create logs directory
mkdir -p logs

# Final verification
print_step "Running system verification..."
python3 << 'PYEOF'
import asyncio
import sys

async def verify():
    issues = []

    # Check imports
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import celery
        import redis
        import tweepy
        import textblob
    except ImportError as e:
        issues.append(f"Missing dependency: {e}")

    # Check database
    try:
        from app.database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
    except Exception as e:
        issues.append(f"Database issue: {e}")

    # Check Redis
    try:
        from app.redis_client import get_redis
        redis = await get_redis()
        await redis.ping()
    except Exception as e:
        issues.append(f"Redis issue: {e}")

    if issues:
        print("ERRORS:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return False
    return True

success = asyncio.run(verify())
sys.exit(0 if success else 1)
PYEOF

if [ $? -eq 0 ]; then
    print_success "System verification passed"
else
    print_error "System verification found some issues"
fi

echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}  ✅ SETUP COMPLETE!${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
echo "   1. Add your Twitter API token to .env file:"
echo "      ${BLUE}nano .env${NC}  (or use your preferred editor)"
echo ""
echo "   2. Start the application:"
echo "      ${BLUE}./start.sh${NC}"
echo ""
echo "   3. Access the API documentation:"
echo "      ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "   4. Login with demo credentials:"
echo "      Username: ${GREEN}demo${NC}"
echo "      Password: ${GREEN}demo123${NC}"
echo ""
echo -e "${YELLOW}📚 Useful Commands:${NC}"
echo "   - Start: ${BLUE}./start.sh${NC}"
echo "   - Stop:  ${BLUE}./stop.sh${NC}"
echo "   - Test:  ${BLUE}./test.sh${NC}"
echo ""
echo -e "${GREEN}Happy monitoring! 🚀${NC}"
echo ""

