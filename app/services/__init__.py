# Service exports for easy imports
from app.services.ai_service import get_ai_service
from app.services.data_service import get_data_service
from app.services.enhanced_ai_service import get_enhanced_ai_service

# Phase 2: New social media data source services
from app.services.google_trends_service import get_google_trends_service
from app.services.tiktok_service import get_tiktok_service
from app.services.facebook_service import get_facebook_service
from app.services.apify_service import get_apify_service

__all__ = [
    "get_ai_service",
    "get_data_service",
    "get_enhanced_ai_service",
    "get_google_trends_service",
    "get_tiktok_service",
    "get_facebook_service",
    "get_apify_service",
]
