#!/bin/bash

# Setup script for local development

echo "Setting up Social Media Monitoring API..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with your configuration"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p reports
mkdir -p alembic/versions

# Initialize database
echo "Database setup instructions:"
echo "1. Make sure PostgreSQL is running"
echo "2. Create database: createdb social_monitor"
echo "3. Run migrations: alembic upgrade head"
echo ""
echo "Redis setup instructions:"
echo "1. Make sure Redis is running on port 6379"
echo ""
echo "Setup complete! Run './start.sh' to start the API"

