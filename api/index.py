"""
Vercel Serverless Function Entry Point for Social Media AI Pipeline
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from mangum import Mangum

# Import the existing app configuration
from app.api import auth, data, reports, ai, webhooks, admin, ingestion

# Create FastAPI app for Vercel
app = FastAPI(
    title="Social Media AI Pipeline API",
    version="2.0.0",
    description="Enterprise-grade social media analysis platform with advanced AI capabilities",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for public API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# API prefix
API_V1_PREFIX = "/api/v1"

# Include routers
app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(data.router, prefix=f"{API_V1_PREFIX}/data", tags=["Data"])
app.include_router(reports.router, prefix=f"{API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(ai.router, prefix=f"{API_V1_PREFIX}/ai", tags=["AI"])
app.include_router(webhooks.router, prefix=f"{API_V1_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(ingestion.router, prefix=f"{API_V1_PREFIX}/ingestion", tags=["Ingestion"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Social Media AI Pipeline",
        "version": "2.0.0",
        "status": "healthy",
        "docs": "/docs",
        "description": "Enterprise-grade social media analysis platform",
        "endpoints": {
            "ai_analysis": f"{API_V1_PREFIX}/ai/analyze/comprehensive",
            "sentiment": f"{API_V1_PREFIX}/ai/analyze/sentiment",
            "locations": f"{API_V1_PREFIX}/ai/analyze/locations",
            "posts": f"{API_V1_PREFIX}/data/posts",
            "analytics": f"{API_V1_PREFIX}/data/analytics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "production",
        "version": "2.0.0",
        "platform": "Vercel",
        "database": "SQLite",
        "cache": "Redis"
    }


@app.get("/api")
async def api_info():
    """API documentation endpoint"""
    return {
        "message": "Social Media AI Pipeline API",
        "version": "2.0.0",
        "documentation": "/docs",
        "endpoints": [
            {"path": "/api/v1/ai/analyze/sentiment", "method": "POST", "description": "Analyze text sentiment"},
            {"path": "/api/v1/ai/analyze/locations", "method": "POST", "description": "Extract locations from text"},
            {"path": "/api/v1/ai/analyze/comprehensive", "method": "POST", "description": "Complete text analysis"},
            {"path": "/api/v1/data/posts", "method": "GET", "description": "Get social media posts"},
            {"path": "/api/v1/data/analytics", "method": "GET", "description": "Get analytics data"},
            {"path": "/api/v1/auth/login", "method": "POST", "description": "User login"},
            {"path": "/api/v1/auth/register", "method": "POST", "description": "User registration"}
        ],
        "access": "Public - No authentication required for testing"
    }


# Mangum handler for Vercel
handler = Mangum(app)