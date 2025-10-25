#!/bin/bash

# Social Media Pipeline - Quick Start Script
# This script builds, starts, and initializes the entire application

set -e

echo "=========================================="
echo "🚀 Social Media Pipeline - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build
echo ""

echo "🚀 Starting services..."
docker-compose up -d
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if API is healthy
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "   Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ API failed to start. Check logs with: docker-compose logs api"
    exit 1
fi

echo ""

# Check if database has data
echo "📊 Checking database..."
TWEET_COUNT=$(docker-compose exec -T api python -c "
import sqlite3
try:
    conn = sqlite3.connect('social_media.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM social_posts')
    count = cursor.fetchone()[0]
    print(count)
    conn.close()
except:
    print(0)
" 2>/dev/null || echo "0")

if [ "$TWEET_COUNT" -lt 100 ]; then
    echo "📝 Generating sample data (800 tweets)..."
    docker-compose exec -T api python generate_1000_tweets.py > /dev/null 2>&1 || true
    echo "✅ Sample data generated!"
else
    echo "✅ Database already contains $TWEET_COUNT tweets"
fi

echo ""
echo "=========================================="
echo "🎉 Application is ready!"
echo "=========================================="
echo ""
echo "📍 Access Points:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check:      http://localhost:8000/health"
echo "   • API Base URL:      http://localhost:8000"
echo ""
echo "🔐 Default Credentials:"
echo "   • Username: demo"
echo "   • Password: demo123"
echo ""
echo "📊 Available Endpoints:"
echo "   • GET  /api/v1/data/overview"
echo "   • GET  /api/v1/data/sentiment/live"
echo "   • GET  /api/v1/data/sentiment/series"
echo "   • GET  /api/v1/data/posts/recent"
echo "   • GET  /api/v1/data/posts/top"
echo "   • GET  /api/v1/data/posts/search?q=Nigeria"
echo "   • GET  /api/v1/data/hashtags/trending"
echo "   • GET  /api/v1/data/hashtags/{tag}"
echo "   • GET  /api/v1/data/influencers"
echo "   • GET  /api/v1/data/geographic/states"
echo "   • GET  /api/v1/data/anomalies"
echo "   • GET  /api/v1/data/connectors"
echo "   • GET  /api/v1/data/stats"
echo "   • POST /api/v1/auth/token"
echo ""
echo "📚 Full API documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Useful Commands:"
echo "   • View logs:        docker-compose logs -f"
echo "   • Stop services:    docker-compose down"
echo "   • Restart:          docker-compose restart"
echo "   • Status:           docker-compose ps"
echo ""
echo "=========================================="

