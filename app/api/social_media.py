"""
Social Media API Endpoints
Unified endpoints for all social media data sources
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.api.auth import get_current_user_optional
from app.models import User
from app.services.google_trends_service import get_google_trends_service
from app.services.tiktok_service import get_tiktok_service
from app.services.facebook_service import get_facebook_service
from app.services.apify_service import get_apify_service
from app.services.data_pipeline_service import get_data_pipeline_service
from app.schemas import BaseResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Request/Response Models
# ============================================

class GoogleTrendsRequest(BaseModel):
    """Request model for Google Trends"""
    keywords: Optional[List[str]] = Field(None, description="Keywords to analyze (max 5)")
    timeframe: str = Field(default="today 3-m", description="Time period (e.g., 'today 3-m', 'today 12-m')")
    include_related: bool = Field(default=True, description="Include related queries")
    include_regional: bool = Field(default=True, description="Include regional interest")


class TikTokHashtagRequest(BaseModel):
    """Request model for TikTok hashtag search"""
    hashtag: str = Field(..., description="Hashtag to search (without #)")
    count: int = Field(default=30, ge=10, le=100, description="Number of videos to fetch")


class FacebookPageRequest(BaseModel):
    """Request model for Facebook page scraping"""
    page_name: str = Field(..., description="Facebook page username/name")
    pages: int = Field(default=2, ge=1, le=5, description="Number of pages to scrape")


class ApifyScrapeRequest(BaseModel):
    """Request model for Apify scraping"""
    platform: str = Field(..., description="Platform to scrape (instagram, tiktok, twitter, facebook)")
    target: str = Field(..., description="Username, hashtag, or page URL to scrape")
    limit: int = Field(default=50, ge=10, le=100, description="Number of items to scrape")


# ============================================
# Google Trends Endpoints
# ============================================

@router.get("/trends/trending", response_model=BaseResponse)
async def get_trending_searches(
    region: str = Query(default="NG", description="Region code (NG for Nigeria)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get current trending searches in Nigeria from Google Trends

    Returns the most popular search terms in real-time
    """
    try:
        trends_service = get_google_trends_service()
        trending = await trends_service.get_trending_searches(region=region)

        # Store in database
        if trending:
            pipeline_service = get_data_pipeline_service(db)
            await pipeline_service.store_google_trends(trending)

        return BaseResponse(
            success=True,
            data={
                "trending_searches": trending,
                "region": region,
                "count": len(trending),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error fetching trending searches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends/analyze", response_model=BaseResponse)
async def analyze_keywords(
    request: GoogleTrendsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Analyze specific keywords using Google Trends

    Returns interest over time, related queries, and regional interest
    """
    try:
        trends_service = get_google_trends_service()

        # Get trending searches if no keywords provided
        if not request.keywords:
            trending = await trends_service.get_trending_searches("NG")
            request.keywords = [t['term'] for t in trending[:5]]

        # Get comprehensive analysis
        analysis = await trends_service.get_comprehensive_analysis(
            keywords=request.keywords,
            include_related=request.include_related,
            include_regional=request.include_regional
        )

        # Store in background
        background_tasks.add_task(
            _store_trends_data,
            db,
            analysis
        )

        return BaseResponse(
            success=True,
            data=analysis
        )

    except Exception as e:
        logger.error(f"Error analyzing keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/suggestions", response_model=BaseResponse)
async def get_keyword_suggestions(
    keyword: str = Query(..., description="Partial keyword"),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get keyword suggestions from Google Trends
    """
    try:
        trends_service = get_google_trends_service()
        suggestions = await trends_service.get_suggestions(keyword)

        return BaseResponse(
            success=True,
            data={
                "keyword": keyword,
                "suggestions": suggestions,
                "count": len(suggestions)
            }
        )

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TikTok Endpoints
# ============================================

@router.post("/tiktok/hashtag", response_model=BaseResponse)
async def scrape_tiktok_hashtag(
    request: TikTokHashtagRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Scrape TikTok videos by hashtag

    Fetches videos from specified hashtag with engagement metrics
    """
    try:
        tiktok_service = get_tiktok_service()

        videos = await tiktok_service.search_hashtag(
            hashtag=request.hashtag,
            count=request.count
        )

        # Store in database
        if videos:
            pipeline_service = get_data_pipeline_service(db)
            stored = await pipeline_service.store_tiktok_content(videos)

            return BaseResponse(
                success=True,
                data={
                    "videos": videos,
                    "total_videos": len(videos),
                    "stored_count": stored,
                    "hashtag": request.hashtag
                }
            )
        else:
            return BaseResponse(
                success=True,
                data={
                    "videos": [],
                    "total_videos": 0,
                    "message": "No videos found for this hashtag"
                }
            )

    except Exception as e:
        logger.error(f"Error scraping TikTok hashtag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiktok/monitor", response_model=BaseResponse)
async def monitor_nigerian_tiktok(
    max_videos: int = Query(default=20, ge=10, le=50),
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Monitor Nigerian TikTok content across popular hashtags

    Scrapes content from predefined Nigerian hashtags
    """
    try:
        tiktok_service = get_tiktok_service()

        result = await tiktok_service.monitor_nigerian_content(
            max_videos_per_hashtag=max_videos
        )

        # Store in background
        if result.get('videos'):
            background_tasks.add_task(
                _store_tiktok_data,
                db,
                result['videos']
            )

        return BaseResponse(
            success=True,
            data=result
        )

    except Exception as e:
        logger.error(f"Error monitoring TikTok: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiktok/analytics/{hashtag}", response_model=BaseResponse)
async def get_tiktok_hashtag_analytics(
    hashtag: str,
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get analytics for a specific TikTok hashtag
    """
    try:
        tiktok_service = get_tiktok_service()

        analytics = await tiktok_service.get_hashtag_analytics(
            hashtag=hashtag,
            days=days
        )

        return BaseResponse(
            success=True,
            data=analytics
        )

    except Exception as e:
        logger.error(f"Error getting TikTok analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Facebook Endpoints
# ============================================

@router.post("/facebook/page", response_model=BaseResponse)
async def scrape_facebook_page(
    request: FacebookPageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Scrape posts from a Facebook page

    Fetches public posts from specified page
    """
    try:
        facebook_service = get_facebook_service()

        posts = await facebook_service.scrape_page_posts(
            page_name=request.page_name,
            pages=request.pages
        )

        # Store in database
        if posts:
            pipeline_service = get_data_pipeline_service(db)
            stored = await pipeline_service.store_facebook_content(posts)

            return BaseResponse(
                success=True,
                data={
                    "posts": posts,
                    "total_posts": len(posts),
                    "stored_count": stored,
                    "page_name": request.page_name
                }
            )
        else:
            return BaseResponse(
                success=True,
                data={
                    "posts": [],
                    "total_posts": 0,
                    "message": "No posts found for this page"
                }
            )

    except Exception as e:
        logger.error(f"Error scraping Facebook page: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facebook/monitor", response_model=BaseResponse)
async def monitor_nigerian_facebook(
    pages_per_source: int = Query(default=2, ge=1, le=5),
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Monitor Nigerian Facebook pages

    Scrapes content from predefined Nigerian news and media pages
    """
    try:
        facebook_service = get_facebook_service()

        result = await facebook_service.monitor_nigerian_pages(
            pages_per_source=pages_per_source
        )

        # Store in background
        if result.get('posts'):
            background_tasks.add_task(
                _store_facebook_data,
                db,
                result['posts']
            )

        return BaseResponse(
            success=True,
            data=result
        )

    except Exception as e:
        logger.error(f"Error monitoring Facebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facebook/analytics/{page_name}", response_model=BaseResponse)
async def get_facebook_page_analytics(
    page_name: str,
    pages: int = Query(default=5, ge=1, le=10),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get analytics for a specific Facebook page
    """
    try:
        facebook_service = get_facebook_service()

        analytics = await facebook_service.get_page_analytics(
            page_name=page_name,
            pages=pages
        )

        return BaseResponse(
            success=True,
            data=analytics
        )

    except Exception as e:
        logger.error(f"Error getting Facebook analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Apify Endpoints
# ============================================

@router.post("/apify/scrape", response_model=BaseResponse)
async def scrape_with_apify(
    request: ApifyScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Scrape social media content using Apify

    Advanced scraping for Instagram, TikTok, Twitter, and Facebook
    """
    try:
        apify_service = get_apify_service()

        # Route to appropriate scraper based on platform
        if request.platform.lower() == "instagram":
            result = await apify_service.scrape_instagram_profile(
                username=request.target,
                results_limit=request.limit
            )
        elif request.platform.lower() == "tiktok":
            result = await apify_service.scrape_tiktok_hashtag(
                hashtag=request.target,
                results_limit=request.limit
            )
        elif request.platform.lower() == "facebook":
            result = await apify_service.scrape_facebook_page(
                page_url=request.target,
                posts_limit=request.limit
            )
        elif request.platform.lower() == "twitter":
            result = await apify_service.scrape_twitter_profile(
                username=request.target,
                tweets_limit=request.limit
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform: {request.platform}"
            )

        # Store in background
        if result.get('posts') or result.get('videos') or result.get('tweets'):
            background_tasks.add_task(
                _store_apify_data,
                db,
                request.platform,
                result
            )

        return BaseResponse(
            success=True,
            data=result
        )

    except Exception as e:
        logger.error(f"Error scraping with Apify: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apify/comprehensive", response_model=BaseResponse)
async def comprehensive_scraping(
    platforms: str = Query(default="instagram,tiktok,facebook", description="Comma-separated platforms"),
    items_per_platform: int = Query(default=50, ge=10, le=100),
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Comprehensive scraping across multiple platforms using Apify

    Scrapes Nigerian content from multiple social media platforms
    """
    try:
        apify_service = get_apify_service()

        platform_list = [p.strip() for p in platforms.split(',')]

        result = await apify_service.scrape_nigerian_social_media(
            platforms=platform_list,
            items_per_platform=items_per_platform
        )

        # Store in background
        background_tasks.add_task(
            _store_comprehensive_apify_data,
            db,
            result
        )

        return BaseResponse(
            success=True,
            data=result
        )

    except Exception as e:
        logger.error(f"Error in comprehensive scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Helper Functions
# ============================================

async def _store_trends_data(db: AsyncSession, analysis: Dict[str, Any]):
    """Background task to store trends data"""
    try:
        pipeline_service = get_data_pipeline_service(db)
        # Extract and store trending data
        if 'interest_over_time' in analysis:
            await pipeline_service.store_google_trends([analysis['interest_over_time']])
    except Exception as e:
        logger.error(f"Error storing trends data in background: {e}")


async def _store_tiktok_data(db: AsyncSession, videos: List[Dict[str, Any]]):
    """Background task to store TikTok data"""
    try:
        pipeline_service = get_data_pipeline_service(db)
        await pipeline_service.store_tiktok_content(videos)
    except Exception as e:
        logger.error(f"Error storing TikTok data in background: {e}")


async def _store_facebook_data(db: AsyncSession, posts: List[Dict[str, Any]]):
    """Background task to store Facebook data"""
    try:
        pipeline_service = get_data_pipeline_service(db)
        await pipeline_service.store_facebook_content(posts)
    except Exception as e:
        logger.error(f"Error storing Facebook data in background: {e}")


async def _store_apify_data(db: AsyncSession, platform: str, result: Dict[str, Any]):
    """Background task to store Apify data"""
    try:
        pipeline_service = get_data_pipeline_service(db)

        # Extract data based on platform
        if platform == "instagram":
            data = result.get('posts', [])
        elif platform == "tiktok":
            data = result.get('videos', [])
        elif platform == "facebook":
            data = result.get('posts', [])
        elif platform == "twitter":
            data = result.get('tweets', [])
        else:
            data = []

        if data:
            await pipeline_service.store_apify_data(platform, data)

    except Exception as e:
        logger.error(f"Error storing Apify data in background: {e}")


async def _store_comprehensive_apify_data(db: AsyncSession, result: Dict[str, Any]):
    """Background task to store comprehensive Apify data"""
    try:
        pipeline_service = get_data_pipeline_service(db)

        for platform, platform_data in result.get('platforms', {}).items():
            if platform_data and not platform_data.get('error'):
                # Extract appropriate data key
                if 'posts' in platform_data:
                    data = platform_data['posts']
                elif 'videos' in platform_data:
                    data = platform_data['videos']
                elif 'tweets' in platform_data:
                    data = platform_data['tweets']
                else:
                    continue

                await pipeline_service.store_apify_data(platform, data)

    except Exception as e:
        logger.error(f"Error storing comprehensive Apify data in background: {e}")
