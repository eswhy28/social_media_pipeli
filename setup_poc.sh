#!/bin/bash

# Social Media Pipeline POC - Setup Script
# This script sets up the development environment for the POC

set -e  # Exit on error

echo "=========================================="
echo "Social Media Pipeline POC - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

if ! python3 -c 'import sys; assert sys.version_info >= (3,9)' 2>/dev/null; then
    echo "Error: Python 3.9 or higher is required"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Download TextBlob corpora
echo ""
echo "Downloading TextBlob language data..."
python -m textblob.download_corpora

# Check if Redis is running
echo ""
echo "Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "⚠ Warning: Redis is not running"
    echo "  Please start Redis with: redis-server"
    echo "  Or with Docker: docker run -d -p 6379:6379 redis:alpine"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠ IMPORTANT: Edit .env and add your Twitter API credentials!"
else
    echo "✓ .env file already exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 << EOF
import asyncio
import sys
sys.path.insert(0, '.')
from app.database import init_db

async def main():
    try:
        await init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

asyncio.run(main())
EOF

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data
echo "✓ Directories created"

echo ""
echo "=========================================="
echo "Setup Complete! ✓"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Twitter API Bearer Token"
echo "2. Start Redis (if not running): redis-server"
echo "3. Start the application:"
echo "   a. Terminal 1: uvicorn app.main:app --reload"
echo "   b. Terminal 2: celery -A app.celery_app worker --loglevel=info"
echo "   c. Terminal 3: celery -A app.celery_app beat --loglevel=info"
echo ""
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For detailed instructions, see README_POC.md"
echo ""

