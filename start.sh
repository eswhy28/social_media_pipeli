#!/bin/bash

# Start script for Social Media Monitoring API

echo "Starting Social Media Monitoring API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container..."

    # Wait for PostgreSQL
    echo "Waiting for PostgreSQL..."
    while ! nc -z postgres 5432; do
        sleep 0.1
    done
    echo "PostgreSQL started"

    # Wait for Redis
    echo "Waiting for Redis..."
    while ! nc -z redis 6379; do
        sleep 0.1
    done
    echo "Redis started"
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting API server..."
uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload

