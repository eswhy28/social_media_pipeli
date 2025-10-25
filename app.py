#!/usr/bin/env python3
"""
Hugging Face Spaces entry point for Social Media AI Pipeline
"""
import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from app.main import app
from app.database import init_db

async def setup():
    """Initialize database and setup for Hugging Face Spaces"""
    try:
        # Create data directory if it doesn't exist
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        raise

if __name__ == "__main__":
    # Run setup
    asyncio.run(setup())
    
    # Get port from environment (Hugging Face Spaces uses PORT)
    port = int(os.getenv("PORT", 7860))
    
    print(f"🚀 Starting Social Media AI Pipeline on port {port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )