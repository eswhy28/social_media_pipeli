#!/bin/bash
# Start server with PostgreSQL

# Export DATABASE_URL to override any defaults
export DATABASE_URL="postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline"

# Source virtual environment
source venv/bin/activate

# Start uvicorn
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000