"""
Social Media API Endpoints
Unified endpoints for all social media data sources
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, Integer
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.api.auth import get_current_user_optional
from app.models import User
from app.models.social_media_sources import ApifyScrapedData
from app.services.google_trends_service import get_google_trends_service
from app.services.tiktok_service import get_tiktok_service
from app.services.facebook_service import get_facebook_service
from app.services.apify_service import get_apify_service
from app.services.data_pipeline_service import get_data_pipeline_service
from app.services.hashtag_discovery_service import get_hashtag_discovery_service
from app.services.geocoding_service import get_geocoding_service
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
    platform: str = Field(..., description="Platform to scrape (twitter, facebook)")
    target: str = Field(..., description="Username, hashtag, or page URL to scrape")
    limit: int = Field(default=50, ge=10, le=100, description="Number of items to scrape")


# ============================================
# Google Trends Endpoints
# ============================================

@router.get("/trends/trending")
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

        return {"success": True, "data":{
                "trending_searches": trending,
                "region": region,
                "count": len(trending),
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error fetching trending searches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends/analyze")
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

        return {"success": True, "data":analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/suggestions")
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

        return {"success": True, "data":{
                "keyword": keyword,
                "suggestions": suggestions,
                "count": len(suggestions)
            }
        }

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TikTok Endpoints
# ============================================

@router.post("/tiktok/hashtag")
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

            return {"success": True, "data":{
                    "videos": videos,
                    "total_videos": len(videos),
                    "stored_count": stored,
                    "hashtag": request.hashtag
                }
            }
        else:
            return {"success": True, "data":{
                    "videos": [],
                    "total_videos": 0,
                    "message": "No videos found for this hashtag"
                }
            }

    except Exception as e:
        logger.error(f"Error scraping TikTok hashtag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiktok/monitor")
async def monitor_nigerian_tiktok(
    background_tasks: BackgroundTasks,
    max_videos: int = Query(default=20, ge=10, le=50),
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

        return {"success": True, "data":result
        }

    except Exception as e:
        logger.error(f"Error monitoring TikTok: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiktok/analytics/{hashtag}")
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

        return {"success": True, "data":analytics
        }

    except Exception as e:
        logger.error(f"Error getting TikTok analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Facebook Endpoints
# ============================================

@router.post("/facebook/page")
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

            return {"success": True, "data":{
                    "posts": posts,
                    "total_posts": len(posts),
                    "stored_count": stored,
                    "page_name": request.page_name
                }
            }
        else:
            return {"success": True, "data":{
                    "posts": [],
                    "total_posts": 0,
                    "message": "No posts found for this page"
                }
            }

    except Exception as e:
        logger.error(f"Error scraping Facebook page: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facebook/monitor")
async def monitor_nigerian_facebook(
    background_tasks: BackgroundTasks,
    pages_per_source: int = Query(default=2, ge=1, le=5),
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

        return {"success": True, "data":result
        }

    except Exception as e:
        logger.error(f"Error monitoring Facebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facebook/analytics/{page_name}")
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

        return {"success": True, "data":analytics
        }

    except Exception as e:
        logger.error(f"Error getting Facebook analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Apify Endpoints (Twitter & Facebook Only)
# ============================================

@router.post("/apify/scrape")
async def scrape_with_apify(
    request: ApifyScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Scrape social media content using Apify
    
    Supports Twitter and Facebook scraping using official Apify actors:
    - Twitter: apidojo/tweet-scraper (Tweet Scraper V2)
    - Facebook: apify/facebook-posts-scraper
    """
    try:
        apify_service = get_apify_service()

        # Route to appropriate scraper based on platform
        if request.platform.lower() == "facebook":
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
                detail=f"Unsupported platform: {request.platform}. Only 'twitter' and 'facebook' are supported."
            )

        # Store in background
        if result.get('posts') or result.get('tweets'):
            background_tasks.add_task(
                _store_apify_data,
                db,
                request.platform,
                result
            )

        return {"success": True, "data":result
        }

    except Exception as e:
        logger.error(f"Error scraping with Apify: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apify/comprehensive")
async def comprehensive_scraping(
    background_tasks: BackgroundTasks,
    platforms: str = Query(default="twitter,facebook", description="Comma-separated platforms (twitter, facebook)"),
    items_per_platform: int = Query(default=50, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Comprehensive scraping across Twitter and Facebook using Apify
    
    Scrapes Nigerian content from Twitter and Facebook platforms
    Only supports: twitter, facebook
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

        return {"success": True, "data":result
        }

    except Exception as e:
        logger.error(f"Error in comprehensive scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Hashtag Discovery Endpoints
# ============================================

@router.get("/hashtags/trending")
async def get_trending_hashtags(
    include_google_trends: bool = Query(default=True, description="Include Google Trends data"),
    include_collected: bool = Query(default=True, description="Include analysis of collected content"),
    limit: int = Query(default=50, ge=10, le=100, description="Maximum hashtags to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get currently trending Nigerian hashtags from all sources

    Discovers trending hashtags by combining:
    - Google Trends API (Nigeria)
    - Recently collected social media content
    - Core Nigerian hashtags

    Returns hashtags ranked by trend score (combination of frequency and engagement)
    """
    try:
        hashtag_service = get_hashtag_discovery_service(db)

        hashtags = await hashtag_service.discover_nigerian_hashtags(
            include_google_trends=include_google_trends,
            include_collected=include_collected,
            limit=limit
        )

        return {"success": True, "data":{
                "trending_hashtags": hashtags,
                "count": len(hashtags),
                "sources": {
                    "google_trends": include_google_trends,
                    "collected_content": include_collected
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting trending hashtags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtags/category/{category}")
async def get_hashtags_by_category(
    category: str,
    limit: int = Query(default=20, ge=5, le=50, description="Maximum hashtags to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get trending hashtags for a specific category

    Categories: politics, entertainment, sports, economy, tech, security, education

    Returns category-specific trending hashtags
    """
    try:
        hashtag_service = get_hashtag_discovery_service(db)

        hashtags = await hashtag_service.get_hashtags_by_category(
            category=category,
            limit=limit
        )

        return {"success": True, "data":{
                "category": category,
                "hashtags": hashtags,
                "count": len(hashtags),
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting hashtags for category {category}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtags/engagement/{hashtag}")
async def get_hashtag_engagement(
    hashtag: str,
    hours_back: int = Query(default=24, ge=1, le=8760, description="Hours of data to analyze (up to 1 year for downloaded data)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get engagement metrics for a specific hashtag

    Returns:
    - Total likes, comments, shares, views
    - Number of posts using this hashtag
    - Platforms where it's trending
    - Engagement rate
    """
    try:
        hashtag_service = get_hashtag_discovery_service(db)

        # Remove # if present
        clean_hashtag = hashtag.lstrip('#')

        metrics = await hashtag_service.get_engagement_metrics_for_hashtag(
            hashtag=clean_hashtag,
            hours_back=hours_back
        )

        return {"success": True, "data":{
                "hashtag": clean_hashtag,
                "time_period_hours": hours_back,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting engagement for #{hashtag}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtags/collected-trends")
async def get_collected_content_trends(
    hours_back: int = Query(default=24, ge=1, le=8760, description="Hours of data to analyze (up to 1 year for downloaded data)"),
    min_occurrences: int = Query(default=5, ge=1, le=50, description="Minimum occurrences"),
    limit: int = Query(default=50, ge=10, le=100, description="Maximum hashtags to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get trending hashtags from collected content with detailed engagement data

    Analyzes recently collected tweets, TikToks, and Facebook posts
    Returns hashtags with:
    - Occurrence count
    - Total engagement (likes + comments + shares)
    - Trend score
    - Last seen timestamp
    """
    try:
        hashtag_service = get_hashtag_discovery_service(db)

        trending_data = await hashtag_service.get_trending_from_collected_content(
            hours_back=hours_back,
            min_occurrences=min_occurrences,
            limit=limit
        )

        return {"success": True, "data":{
                "trending_hashtags": trending_data,
                "count": len(trending_data),
                "time_period_hours": hours_back,
                "min_occurrences": min_occurrences,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting collected content trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hashtags/update-cache")
async def update_hashtag_cache(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Manually trigger hashtag cache update

    Updates the trending hashtags cache with latest data from all sources
    """
    try:
        # Run cache update in background
        background_tasks.add_task(
            _update_hashtag_cache_task,
            db
        )

        return {"success": True, "data":{
                "message": "Hashtag cache update triggered",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error triggering hashtag cache update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Scraped Data Retrieval Endpoints
# ============================================

@router.get("/data/scraped")
async def get_scraped_data(
    platform: Optional[str] = Query(None, description="Filter by platform (twitter, facebook, etc.)"),
    limit: int = Query(default=50, ge=1, le=500, description="Number of records to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    hours_back: Optional[int] = Query(None, ge=1, le=8760, description="Filter by hours back (up to 1 year for downloaded data)"),
    has_media: Optional[bool] = Query(None, description="Filter posts with images/media"),
    hashtag: Optional[str] = Query(None, description="Filter by hashtag"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get scraped social media data with all insights
    
    Returns posts with:
    - Full content and metadata
    - Media URLs (images, videos)
    - Location with geographic coordinates
    - Engagement metrics
    - Hashtags and mentions
    - Author information
    """
    try:
        # Build query
        query = select(ApifyScrapedData)
        
        # Apply filters
        filters = []
        
        if platform:
            filters.append(ApifyScrapedData.platform == platform.lower())
        
        if hours_back:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            filters.append(ApifyScrapedData.posted_at >= cutoff_time)
        
        if has_media is not None:
            if has_media:
                filters.append(func.json_array_length(ApifyScrapedData.media_urls) > 0)
            else:
                filters.append(
                    or_(
                        ApifyScrapedData.media_urls == None,
                        func.json_array_length(ApifyScrapedData.media_urls) == 0
                    )
                )
        
        if hashtag:
            clean_tag = hashtag.lstrip('#').lower()
            filters.append(
                func.lower(func.cast(ApifyScrapedData.hashtags, str)).contains(clean_tag)
            )
        
        if location:
            filters.append(
                func.lower(ApifyScrapedData.location).contains(location.lower())
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by posted_at descending
        query = query.order_by(ApifyScrapedData.posted_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Enrich data with coordinates and format for frontend
        geocoding_service = get_geocoding_service()
        enriched_posts = []
        
        for post in posts:
            # Enrich location with coordinates
            location_data = geocoding_service.enrich_location_data(post.location)
            
            enriched_post = {
                "id": post.id,
                "platform": post.platform,
                "source_id": post.source_id,
                "author": {
                    "username": post.author,
                    "account_name": post.account_name,
                },
                "content": post.content,
                "content_type": post.content_type,
                "engagement": post.metrics_json or {},
                "hashtags": post.hashtags or [],
                "mentions": post.mentions or [],
                "media": {
                    "urls": post.media_urls or [],
                    "count": len(post.media_urls) if post.media_urls else 0,
                    "has_media": bool(post.media_urls and len(post.media_urls) > 0)
                },
                "location": location_data,
                "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                "collected_at": post.collected_at.isoformat() if post.collected_at else None,
                "url": f"https://twitter.com/{post.author}/status/{post.source_id}" if post.platform == "twitter" else None
            }
            
            enriched_posts.append(enriched_post)
        
        return {"success": True, "data":{
                "posts": enriched_posts,
                "count": len(enriched_posts),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "platform": platform,
                    "hours_back": hours_back,
                    "has_media": has_media,
                    "hashtag": hashtag,
                    "location": location
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching scraped data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/geo-analysis")
async def get_geo_analysis(
    hours_back: int = Query(default=24, ge=1, le=8760, description="Hours of data to analyze (up to 1 year for downloaded data)"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get geographic analysis of scraped data
    
    Returns:
    - Posts grouped by region/state
    - Each location with coordinates
    - Engagement metrics per location
    - Top hashtags per location
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Build query
        query = select(ApifyScrapedData).where(
            ApifyScrapedData.posted_at >= cutoff_time
        )
        
        if platform:
            query = query.where(ApifyScrapedData.platform == platform.lower())
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Group by location
        geocoding_service = get_geocoding_service()
        location_data = {}
        
        for post in posts:
            if not post.location:
                continue
            
            loc = post.location
            if loc not in location_data:
                enriched_loc = geocoding_service.enrich_location_data(loc)
                location_data[loc] = {
                    "location": enriched_loc,
                    "posts_count": 0,
                    "total_engagement": 0,
                    "hashtags": {},
                    "authors": set(),
                    "sample_posts": []
                }
            
            location_data[loc]["posts_count"] += 1
            location_data[loc]["authors"].add(post.author)
            
            # Add engagement
            if post.metrics_json:
                likes = post.metrics_json.get('likes', 0)
                retweets = post.metrics_json.get('retweets', 0)
                replies = post.metrics_json.get('replies', 0)
                location_data[loc]["total_engagement"] += likes + retweets + replies
            
            # Count hashtags
            if post.hashtags:
                for tag in post.hashtags:
                    location_data[loc]["hashtags"][tag] = location_data[loc]["hashtags"].get(tag, 0) + 1
            
            # Add sample post (max 3 per location)
            if len(location_data[loc]["sample_posts"]) < 3:
                location_data[loc]["sample_posts"].append({
                    "author": post.author,
                    "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                    "engagement": post.metrics_json,
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None
                })
        
        # Format output
        geo_analysis = []
        for loc, data in location_data.items():
            # Get top 5 hashtags for this location
            top_hashtags = sorted(
                data["hashtags"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            geo_analysis.append({
                "location": data["location"],
                "metrics": {
                    "posts_count": data["posts_count"],
                    "unique_authors": len(data["authors"]),
                    "total_engagement": data["total_engagement"],
                    "avg_engagement": data["total_engagement"] / data["posts_count"] if data["posts_count"] > 0 else 0
                },
                "top_hashtags": [{"tag": tag, "count": count} for tag, count in top_hashtags],
                "sample_posts": data["sample_posts"]
            })
        
        # Sort by posts count
        geo_analysis.sort(key=lambda x: x["metrics"]["posts_count"], reverse=True)
        
        return {"success": True, "data":{
                "geo_analysis": geo_analysis,
                "total_locations": len(geo_analysis),
                "time_period_hours": hours_back,
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error performing geo-analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/engagement-analysis")
async def get_engagement_analysis(
    hours_back: int = Query(default=24, ge=1, le=8760, description="Hours of data to analyze (up to 1 year for downloaded data)"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    group_by: str = Query(default="hour", description="Group by: hour, day, author, hashtag"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get engagement analysis of scraped data
    
    Returns aggregated engagement metrics grouped by time, author, or hashtag
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Build query
        query = select(ApifyScrapedData).where(
            ApifyScrapedData.posted_at >= cutoff_time
        )
        
        if platform:
            query = query.where(ApifyScrapedData.platform == platform.lower())
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Aggregate based on group_by parameter
        aggregated = {}
        
        for post in posts:
            if group_by == "hour":
                key = post.posted_at.strftime("%Y-%m-%d %H:00") if post.posted_at else "Unknown"
            elif group_by == "day":
                key = post.posted_at.strftime("%Y-%m-%d") if post.posted_at else "Unknown"
            elif group_by == "author":
                key = post.author or "Unknown"
            elif group_by == "hashtag":
                # We'll handle hashtags separately since one post can have multiple
                if post.hashtags:
                    for tag in post.hashtags:
                        if tag not in aggregated:
                            aggregated[tag] = {
                                "posts": [],
                                "total_likes": 0,
                                "total_retweets": 0,
                                "total_replies": 0,
                                "total_views": 0,
                                "posts_count": 0
                            }
                        
                        aggregated[tag]["posts"].append(post.source_id)
                        aggregated[tag]["posts_count"] += 1
                        
                        if post.metrics_json:
                            aggregated[tag]["total_likes"] += post.metrics_json.get('likes', 0)
                            aggregated[tag]["total_retweets"] += post.metrics_json.get('retweets', 0)
                            aggregated[tag]["total_replies"] += post.metrics_json.get('replies', 0)
                            aggregated[tag]["total_views"] += post.metrics_json.get('views', 0)
                continue
            else:
                key = "All"
            
            if key not in aggregated:
                aggregated[key] = {
                    "posts": [],
                    "total_likes": 0,
                    "total_retweets": 0,
                    "total_replies": 0,
                    "total_views": 0,
                    "posts_count": 0
                }
            
            aggregated[key]["posts"].append(post.source_id)
            aggregated[key]["posts_count"] += 1
            
            if post.metrics_json:
                aggregated[key]["total_likes"] += post.metrics_json.get('likes', 0)
                aggregated[key]["total_retweets"] += post.metrics_json.get('retweets', 0)
                aggregated[key]["total_replies"] += post.metrics_json.get('replies', 0)
                aggregated[key]["total_views"] += post.metrics_json.get('views', 0)
        
        # Format output
        analysis = []
        for key, metrics in aggregated.items():
            total_engagement = metrics["total_likes"] + metrics["total_retweets"] + metrics["total_replies"]
            avg_engagement = total_engagement / metrics["posts_count"] if metrics["posts_count"] > 0 else 0
            
            analysis.append({
                group_by: key,
                "metrics": {
                    "posts_count": metrics["posts_count"],
                    "total_likes": metrics["total_likes"],
                    "total_retweets": metrics["total_retweets"],
                    "total_replies": metrics["total_replies"],
                    "total_views": metrics["total_views"],
                    "total_engagement": total_engagement,
                    "avg_engagement": round(avg_engagement, 2)
                }
            })
        
        # Sort by total engagement
        analysis.sort(key=lambda x: x["metrics"]["total_engagement"], reverse=True)
        
        return {"success": True, "data":{
                "analysis": analysis,
                "group_by": group_by,
                "total_groups": len(analysis),
                "time_period_hours": hours_back,
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error performing engagement analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/with-media")
async def get_posts_with_media(
    media_type: Optional[str] = Query(None, description="Filter by media type: image, video, or all"),
    platform: Optional[str] = Query(None, description="Filter by platform (twitter, facebook, etc.)"),
    limit: int = Query(default=50, ge=1, le=500, description="Number of posts to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    hours_back: Optional[int] = Query(None, ge=1, le=8760, description="Filter by time range (up to 1 year)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get posts that contain media (images or videos)
    
    Optimized endpoint for frontend to easily retrieve posts with visual content.
    
    Returns:
    - Posts with media URLs (images/videos)
    - Media metadata (type, count)
    - Full post content and engagement
    - Author information
    - Direct URLs to media files
    """
    try:
        # Build query - only posts WITH media
        query = select(ApifyScrapedData).where(
            func.json_array_length(ApifyScrapedData.media_urls) > 0
        )
        
        # Apply additional filters
        filters = []
        
        if platform:
            filters.append(ApifyScrapedData.platform == platform.lower())
        
        if hours_back:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            filters.append(ApifyScrapedData.posted_at >= cutoff_time)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by posted_at descending
        query = query.order_by(ApifyScrapedData.posted_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Format response with enhanced media information
        enriched_posts = []
        
        for post in posts:
            media_urls = post.media_urls or []
            
            # Categorize media by type (basic detection)
            images = []
            videos = []
            
            for url in media_urls:
                if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    images.append(url)
                elif any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm', 'video']):
                    videos.append(url)
                else:
                    # If we can't determine, assume it's an image
                    images.append(url)
            
            # Apply media_type filter
            if media_type:
                if media_type.lower() == 'image' and not images:
                    continue
                if media_type.lower() == 'video' and not videos:
                    continue
            
            post_data = {
                "id": post.id,
                "source_id": post.source_id,
                "platform": post.platform,
                "author": {
                    "username": post.author,
                    "account_name": post.account_name,
                },
                "content": post.content,
                "content_type": post.content_type,
                "media": {
                    "all_urls": media_urls,
                    "images": images,
                    "videos": videos,
                    "total_count": len(media_urls),
                    "image_count": len(images),
                    "video_count": len(videos),
                    "has_images": len(images) > 0,
                    "has_videos": len(videos) > 0,
                    # Primary media (first item) for thumbnails
                    "primary_url": media_urls[0] if media_urls else None,
                    "primary_type": "image" if images else "video" if videos else "unknown"
                },
                "engagement": post.metrics_json or {},
                "hashtags": post.hashtags or [],
                "mentions": post.mentions or [],
                "location": post.location,
                "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                "url": f"https://twitter.com/{post.author}/status/{post.source_id}" if post.platform == "twitter" else None
            }
            
            enriched_posts.append(post_data)
        
        return {"success": True, "data": {
                "posts": enriched_posts,
                "count": len(enriched_posts),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "media_type": media_type,
                    "platform": platform,
                    "hours_back": hours_back
                },
                "summary": {
                    "total_media_items": sum(p["media"]["total_count"] for p in enriched_posts),
                    "total_images": sum(p["media"]["image_count"] for p in enriched_posts),
                    "total_videos": sum(p["media"]["video_count"] for p in enriched_posts)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching posts with media: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/stats")
async def get_data_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get overall statistics for scraped data
    
    Returns:
    - Total posts count
    - Posts by platform
    - Posts with media count
    - Date range of data
    - Top authors
    - Top hashtags
    """
    try:
        # Get total count
        total_result = await db.execute(select(func.count(ApifyScrapedData.id)))
        total_count = total_result.scalar()
        
        # Get platform distribution
        platform_result = await db.execute(
            select(
                ApifyScrapedData.platform,
                func.count(ApifyScrapedData.id).label('count')
            ).group_by(ApifyScrapedData.platform)
        )
        platforms = {row[0]: row[1] for row in platform_result.all()}
        
        # Get posts with media count
        media_result = await db.execute(
            select(func.count(ApifyScrapedData.id)).where(
                func.json_array_length(ApifyScrapedData.media_urls) > 0
            )
        )
        posts_with_media = media_result.scalar()
        
        # Get date range
        date_range_result = await db.execute(
            select(
                func.min(ApifyScrapedData.posted_at),
                func.max(ApifyScrapedData.posted_at)
            )
        )
        min_date, max_date = date_range_result.first()
        
        # Get all posts for detailed analysis
        all_posts_result = await db.execute(
            select(ApifyScrapedData).order_by(ApifyScrapedData.posted_at.desc()).limit(1000)
        )
        all_posts = all_posts_result.scalars().all()
        
        # Get top authors
        author_counts = {}
        hashtag_counts = {}
        
        for post in all_posts:
            # Count authors
            if post.author:
                author_counts[post.author] = author_counts.get(post.author, 0) + 1
            
            # Count hashtags
            if post.hashtags:
                for tag in post.hashtags:
                    hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {"success": True, "data":{
                "overall": {
                    "total_posts": total_count,
                    "posts_with_media": posts_with_media,
                    "media_percentage": round(posts_with_media / total_count * 100, 2) if total_count > 0 else 0
                },
                "platforms": platforms,
                "date_range": {
                    "earliest": min_date.isoformat() if min_date else None,
                    "latest": max_date.isoformat() if max_date else None
                },
                "top_authors": [{"author": author, "posts_count": count} for author, count in top_authors],
                "top_hashtags": [{"hashtag": tag, "count": count} for tag, count in top_hashtags],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AI Processing Endpoints (Smart Reprocessing Prevention)
# ============================================

@router.post("/ai/process-sentiment")
async def process_sentiment_analysis(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Max records to process"),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Process sentiment analysis for unprocessed scraped data
    
    Only processes data that hasn't been analyzed yet.
    Results are saved to avoid reprocessing.
    """
    try:
        from app.services.ai_processing_service import get_ai_processing_service
        
        ai_service = get_ai_processing_service(db)
        
        # Get count of unprocessed data
        unprocessed = await ai_service.get_unprocessed_data("sentiment", limit=10)
        unprocessed_count = len(unprocessed)
        
        if unprocessed_count == 0:
            return {"success": True, "data":{
                    "message": "No unprocessed data found. All data has been analyzed.",
                    "unprocessed_count": 0
                }
            }
        
        # Process sentiment
        result = await ai_service.process_sentiment_batch(limit=limit)
        
        return {"success": True, "data":{
                "message": f"Sentiment analysis completed for {result['processed']} records",
                "job_id": result['job_id'],
                "total_records": result['total_records'],
                "processed": result['processed'],
                "failed": result['failed'],
                "processing_time_seconds": result['processing_time_seconds'],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/process-locations")
async def process_location_extraction(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Max records to process"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Process location extraction for unprocessed scraped data
    
    Extracts locations from content and geocodes them.
    Only processes data that hasn't been analyzed yet.
    """
    try:
        from app.services.ai_processing_service import get_ai_processing_service
        
        ai_service = get_ai_processing_service(db)
        
        # Get count of unprocessed data
        unprocessed = await ai_service.get_unprocessed_data("location", limit=10)
        unprocessed_count = len(unprocessed)
        
        if unprocessed_count == 0:
            return {"success": True, "data":{
                    "message": "No unprocessed data found. All data has been analyzed.",
                    "unprocessed_count": 0
                }
            }
        
        # Process locations
        result = await ai_service.process_location_batch(limit=limit)
        
        return {"success": True, "data":{
                "message": f"Location extraction completed for {result['processed']} records",
                "job_id": result['job_id'],
                "total_records": result['total_records'],
                "processed": result['processed'],
                "failed": result['failed'],
                "locations_found": result['locations_found'],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/processing-stats")
async def get_ai_processing_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get AI processing statistics
    
    Shows how many records have been processed vs unprocessed
    """
    try:
        from app.services.ai_processing_service import get_ai_processing_service
        
        ai_service = get_ai_processing_service(db)
        stats = await ai_service.get_processing_statistics()
        
        return {"success": True, "data":{
                "statistics": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting processing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/sentiment-results")
async def get_sentiment_results(
    limit: int = Query(default=50, ge=1, le=500),
    sentiment_label: Optional[str] = Query(None, description="Filter by label: positive, negative, neutral"),
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get sentiment analysis results
    
    Returns sentiment analysis results with the original posts
    """
    try:
        from app.models.ai_analysis import ApifySentimentAnalysis
        from sqlalchemy import select
        
        # Build query
        query = select(ApifySentimentAnalysis).where(
            ApifySentimentAnalysis.confidence >= min_confidence
        )
        
        if sentiment_label:
            query = query.where(ApifySentimentAnalysis.label == sentiment_label.lower())
        
        query = query.order_by(ApifySentimentAnalysis.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        sentiment_records = result.scalars().all()
        
        # Enrich with post data
        enriched_results = []
        for record in sentiment_records:
            # Get the original post
            post_result = await db.execute(
                select(ApifyScrapedData).where(ApifyScrapedData.id == record.scraped_data_id)
            )
            post = post_result.scalar_one_or_none()
            
            if post:
                enriched_results.append({
                    "sentiment": {
                        "label": record.label,
                        "score": record.score,
                        "confidence": record.confidence,
                        "model": record.model_name
                    },
                    "post": {
                        "id": post.id,
                        "author": post.author,
                        "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                        "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                        "engagement": post.metrics_json
                    }
                })
        
        return {"success": True, "data":{
                "results": enriched_results,
                "count": len(enriched_results),
                "filters": {
                    "sentiment_label": sentiment_label,
                    "min_confidence": min_confidence
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting sentiment results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/location-results")
async def get_location_extraction_results(
    limit: int = Query(default=50, ge=1, le=500),
    location_type: Optional[str] = Query(None, description="Filter by type"),
    hours_back: Optional[int] = Query(None, ge=1, le=8760, description="Filter by time range (up to 1 year)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get location extraction results WITH FULL POST DATA
    
    Returns:
    - Extracted and geocoded locations
    - Complete original post content
    - Author information
    - Media URLs (images/videos)
   - Engagement metrics
    - Posted date and time
    """
    try:
        from app.models.ai_analysis import ApifyLocationExtraction
        from sqlalchemy import select
        
        # Build query with join to get post data
        query = select(ApifyLocationExtraction, ApifyScrapedData).join(
            ApifyScrapedData,
            ApifyLocationExtraction.scraped_data_id == ApifyScrapedData.id
        )
        
        if location_type:
            query = query.where(ApifyLocationExtraction.location_type == location_type.upper())
        
        if hours_back:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            query = query.where(ApifyScrapedData.posted_at >= cutoff_time)
        
        query = query.order_by(ApifyLocationExtraction.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        records = result.all()
        
        # Format results with full post data
        enriched_results = []
        for location_record, post in records:
            enriched_results.append({
                "location": {
                    "text": location_record.location_text,
                    "type": location_record.location_type,
                    "confidence": location_record.confidence,
                    "coordinates": location_record.coordinates,
                    "region": location_record.region,
                    "state_province": location_record.state_province,
                    "city": location_record.city,
                    "country": location_record.country
                },
                "post": {
                    "id": post.id,
                    "source_id": post.source_id,
                    "platform": post.platform,
                    "content": post.content,
                    "author": {
                        "username": post.author,
                        "account_name": post.account_name
                    },
                    "media": {
                        "urls": post.media_urls or [],
                        "count": len(post.media_urls) if post.media_urls else 0,
                        "has_media": bool(post.media_urls and len(post.media_urls) > 0)
                    },
                    "engagement": post.metrics_json or {},
                    "hashtags": post.hashtags or [],
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                    "url": f"https://twitter.com/{post.author}/status/{post.source_id}" if post.platform == "twitter" else None
                }
            })
        
        return {"success": True, "data":{
                "results": enriched_results,
                "count": len(enriched_results),
                "filters": {
                    "location_type": location_type,
                    "hours_back": hours_back
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting location results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Intelligence Report Endpoint (Comprehensive Analysis)
# ============================================

@router.get("/intelligence/report")
async def get_intelligence_report(
    limit: int = Query(default=50, ge=1, le=500),
    hours_back: int = Query(default=24, ge=1, le=8760, description="Time range in hours (up to 1 year for downloaded data)"),
    sentiment_filter: Optional[str] = Query(None, description="Filter by sentiment: positive, negative, neutral"),
    has_media: Optional[bool] = Query(None, description="Filter posts with/without media"),
    min_engagement: int = Query(default=0, description="Minimum total engagement"),
    include_ai_analysis: bool = Query(default=True, description="Include AI sentiment and location analysis"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    **INTELLIGENCE-GRADE REPORT**: Comprehensive social media monitoring endpoint
    
    Returns posts with:
    - Original post content and author
    - All media (images/videos) with direct URLs
    - AI sentiment analysis results
    - Location extraction with coordinates
    - Full engagement metrics
    - Hashtags and mentions
    - Temporal analysis
    
    Perfect for intelligence analysts and monitoring dashboards.
    """
    try:
        from app.models.ai_analysis import ApifySentimentAnalysis, ApifyLocationExtraction
        
        # Build base query - get all posts, time filtering can be added later with proper timezone handling
        query = select(ApifyScrapedData)
        
        # Apply filters
        if has_media is not None:
            if has_media:
                query = query.where(
                    and_(
                        ApifyScrapedData.media_urls.isnot(None),
                        func.json_array_length(ApifyScrapedData.media_urls) > 0
                    )
                )
            else:
                query = query.where(
                    or_(
                        ApifyScrapedData.media_urls.is_(None),
                        func.json_array_length(ApifyScrapedData.media_urls) == 0
                    )
                )
        
        # Engagement filter
        
        query = query.order_by(ApifyScrapedData.posted_at.desc()).limit(limit * 2)  # Get more to account for filtering
        
        result = await db.execute(query)
        all_posts = result.scalars().all()
        
        # Filter by engagement in Python (simpler and more reliable)
        posts = []
        for post in all_posts:
            if min_engagement > 0 and post.metrics_json:
                total_engagement = (
                    post.metrics_json.get('likes', 0) +
                    post.metrics_json.get('retweets', 0) +
                    post.metrics_json.get('replies', 0)
                )
                if total_engagement < min_engagement:
                    continue
            posts.append(post)
            if len(posts) >= limit:
                break
        
        # Enrich with AI analysis
        intelligence_reports = []
        
        for post in posts:
            # Base post data
            report = {
                "post_id": post.id,
                "platform": post.platform,
                "collected_at": post.collected_at.isoformat() if post.collected_at else None,
                
                # Author Information
                "author": {
                    "username": post.author,
                    "account_name": post.account_name,
                    "location": post.location
                },
                
                # Content
                "content": {
                    "text": post.content,
                    "language": post.raw_data.get('lang') if post.raw_data else 'unknown',
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                    "url": f"https://twitter.com/{post.author}/status/{post.source_id}" if post.source_id else None
                },
                
                # Media (Images/Videos)
                "media": {
                    "has_media": bool(post.media_urls and len(post.media_urls) > 0),
                    "count": len(post.media_urls) if post.media_urls else 0,
                    "urls": post.media_urls or [],
                    "type": "image" if post.media_urls else None  # Can be enhanced to detect video vs image
                },
                
                # Engagement Metrics
                "engagement": {
                    "likes": post.metrics_json.get('likes', 0) if post.metrics_json else 0,
                    "retweets": post.metrics_json.get('retweets', 0) if post.metrics_json else 0,
                    "replies": post.metrics_json.get('replies', 0) if post.metrics_json else 0,
                    "views": post.metrics_json.get('views', 0) if post.metrics_json else 0,
                    "quotes": post.metrics_json.get('quotes', 0) if post.metrics_json else 0,
                    "bookmarks": post.metrics_json.get('bookmarks', 0) if post.metrics_json else 0,
                    "total": (
                        post.metrics_json.get('likes', 0) +
                        post.metrics_json.get('retweets', 0) +
                        post.metrics_json.get('replies', 0)
                    ) if post.metrics_json else 0
                },
                
                # Context
                "context": {
                    "hashtags": post.hashtags or [],
                    "mentions": post.mentions or [],
                    "hashtag_count": len(post.hashtags) if post.hashtags else 0,
                    "mention_count": len(post.mentions) if post.mentions else 0
                }
            }
            
            # Add AI Analysis if requested
            if include_ai_analysis:
                # Get sentiment analysis
                sentiment_result = await db.execute(
                    select(ApifySentimentAnalysis).where(
                        ApifySentimentAnalysis.scraped_data_id == post.id
                    ).order_by(ApifySentimentAnalysis.created_at.desc()).limit(1)
                )
                sentiment = sentiment_result.scalar_one_or_none()
                
                if sentiment:
                    report["ai_analysis"] = {
                        "sentiment": {
                            "label": sentiment.label,
                            "score": sentiment.score,
                            "confidence": sentiment.confidence,
                            "polarity": sentiment.all_scores.get('polarity') if sentiment.all_scores else None,
                            "subjectivity": sentiment.all_scores.get('subjectivity') if sentiment.all_scores else None,
                            "model": sentiment.model_name,
                            "analyzed_at": sentiment.created_at.isoformat() if sentiment.created_at else None
                        }
                    }
                    
                    # Apply sentiment filter if specified
                    if sentiment_filter and sentiment.label != sentiment_filter.lower():
                        continue  # Skip this post if it doesn't match sentiment filter
                else:
                    report["ai_analysis"] = {"sentiment": None}
                
                # Get location extractions
                location_result = await db.execute(
                    select(ApifyLocationExtraction).where(
                        ApifyLocationExtraction.scraped_data_id == post.id
                    )
                )
                locations = location_result.scalars().all()
                
                if locations:
                    report["ai_analysis"]["locations"] = [
                        {
                            "text": loc.location_text,
                            "type": loc.location_type,
                            "confidence": loc.confidence,
                            "coordinates": loc.coordinates,
                            "country": loc.country,
                            "region": loc.region,
                            "city": loc.city
                        }
                        for loc in locations
                    ]
                else:
                    report["ai_analysis"]["locations"] = []
            
            intelligence_reports.append(report)
        
        # Filter out posts that didn't pass sentiment filter
        if sentiment_filter and include_ai_analysis:
            pass  # Already filtered in loop
        
        # Generate summary statistics
        summary = {
            "total_posts": len(intelligence_reports),
            "time_range_hours": hours_back,
            "filters_applied": {
                "sentiment": sentiment_filter,
                "has_media": has_media,
                "min_engagement": min_engagement
            },
            "posts_with_media": sum(1 for r in intelligence_reports if r["media"]["has_media"]),
            "total_engagement": sum(r["engagement"]["total"] for r in intelligence_reports),
            "average_engagement": round(
                sum(r["engagement"]["total"] for r in intelligence_reports) / len(intelligence_reports)
            ) if intelligence_reports else 0
        }
        
        if include_ai_analysis:
            sentiments = [r.get("ai_analysis", {}).get("sentiment", {}).get("label") 
                         for r in intelligence_reports 
                         if r.get("ai_analysis", {}).get("sentiment")]
            summary["sentiment_distribution"] = {
                "positive": sentiments.count("positive"),
                "negative": sentiments.count("negative"),
                "neutral": sentiments.count("neutral")
            }
        
        return {
            "success": True,
            "data": {
                "summary": summary,
                "reports": intelligence_reports,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating intelligence report: {e}")
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


async def _update_hashtag_cache_task(db: AsyncSession):
    """Background task to update hashtag cache"""
    try:
        hashtag_service = get_hashtag_discovery_service(db)
        cache = await hashtag_service.update_trending_cache()
        logger.info(f"Hashtag cache updated successfully: {len(cache.get('all', []))} total hashtags")
    except Exception as e:
        logger.error(f"Error updating hashtag cache in background: {e}")
