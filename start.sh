#!/bin/bash
# Simple script to start the server

echo "🚀 Starting Social Media Analytics Pipeline..."
echo "📚 API Documentation will be at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
