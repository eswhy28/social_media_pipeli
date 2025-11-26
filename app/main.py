from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, close_db
from app.redis_client import close_redis
from app.api import auth, reports, ai, webhooks, admin, ingestion, social_media


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")

    # Note: Database tables are managed by Alembic migrations
    # Run: alembic upgrade head
    # Or: python scripts/complete_setup.py
    logger.info("Database tables managed by Alembic (migrations)")

    # Optional: Test database connection
    try:
        from app.database import engine
        async with engine.connect() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.warning(f"Database connection test failed: {str(e)}")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_redis()
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Social Media Monitoring and Sentiment Analysis API - POC Version",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(ai.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(ingestion.router, prefix=f"{settings.API_V1_PREFIX}/ingestion", tags=["Ingestion"])
app.include_router(social_media.router, prefix=f"{settings.API_V1_PREFIX}/social-media", tags=["Social Media"])


# Legacy endpoint redirects/disabled endpoints
@app.get(f"{settings.API_V1_PREFIX}/data/sentiment/live")
async def legacy_sentiment_live_disabled():
    """
    Legacy sentiment live endpoint - Disabled

    This endpoint has been deprecated and disabled.
    Please use the new endpoint at:
    - GET /api/v1/social-media/data/scraped (with sentiment data included)
    - GET /api/v1/social-media/intelligence/report (comprehensive report)
    """
    from datetime import datetime
    return {
        "status": "disabled",
        "message": "This endpoint has been deprecated. Please use the new social-media endpoints.",
        "new_endpoints": {
            "scraped_data": f"{settings.API_V1_PREFIX}/social-media/data/scraped",
            "intelligence_report": f"{settings.API_V1_PREFIX}/social-media/intelligence/report",
            "sentiment_results": f"{settings.API_V1_PREFIX}/social-media/ai/sentiment-results"
        },
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
        "description": "Social Media Pipeline POC with Free-Tier Services"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "database": "SQLite",
        "cache": "Redis"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
