from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.api.auth import get_current_user_optional
from app.models import User
from app.services.data_service import DataService
from app.schemas import BaseResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class FetchTweetsRequest(BaseModel):
    """Request model for fetching tweets"""
    query: str = Field(..., description="Search query (keywords, hashtags, mentions)")
    max_results: int = Field(default=100, ge=10, le=100, description="Number of tweets to fetch (10-100, default 100 for max value)")
    days_back: int = Field(default=7, ge=1, le=30, description="How many days back to search")
    focus_on_engagement: bool = Field(default=True, description="Prioritize highly engaged tweets")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Nigeria FIFA World Cup OR #SuperEagles",
                "max_results": 100,
                "days_back": 7,
                "focus_on_engagement": True
            }
        }


class FetchTweetsResponse(BaseModel):
    """Response model for fetch tweets"""
    success: bool
    data: dict


@router.post("/fetch-tweets", response_model=FetchTweetsResponse)
async def fetch_and_analyze_tweets(
    request: FetchTweetsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Fetch tweets based on search query, perform sentiment analysis, and save to database.
    
    This endpoint:
    1. Fetches tweets from Twitter API based on query
    2. Focuses on most recent and highly engaged tweets
    3. Performs sentiment analysis on each tweet
    4. Extracts hashtags and keywords
    5. Saves everything to database
    6. Returns summary of fetched data
    
    Note: Twitter free tier allows 100 tweets per month
    """
    try:
        data_service = DataService(db)
        
        # Calculate start time
        start_time = datetime.utcnow() - timedelta(days=request.days_back)
        
        logger.info(f"Fetching tweets for query: '{request.query}' by user: {current_user.username}")
        
        # Fetch tweets from Twitter API
        tweets = await data_service.fetch_recent_tweets(
            query=request.query,
            max_results=request.max_results,
            start_time=start_time
        )
        
        if not tweets:
            return FetchTweetsResponse(
                success=True,
                data={
                    "tweets_fetched": 0,
                    "tweets_stored": 0,
                    "message": "No tweets found for the query. Try adjusting your search terms or date range."
                }
            )
        
        # Sort by engagement if requested
        if request.focus_on_engagement:
            tweets = sorted(
                tweets,
                key=lambda x: x.get('metrics', {}).get('likes', 0) + 
                             x.get('metrics', {}).get('retweets', 0) * 2 +  # Weight retweets higher
                             x.get('metrics', {}).get('replies', 0),
                reverse=True
            )
        
        # Store tweets and perform sentiment analysis
        stored_count = await data_service.store_posts(tweets)
        
        # Get analytics summary
        analytics = await data_service.get_fetch_summary(request.query, start_time)
        
        logger.info(f"Successfully fetched {len(tweets)} tweets, stored {stored_count} new tweets")
        
        return FetchTweetsResponse(
            success=True,
            data={
                "tweets_fetched": len(tweets),
                "tweets_stored": stored_count,
                "duplicates_skipped": len(tweets) - stored_count,
                "query": request.query,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "analytics": analytics,
                "top_engaged_tweet": tweets[0] if tweets else None,
                "message": f"Successfully fetched and analyzed {len(tweets)} tweets. {stored_count} new tweets saved to database."
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching tweets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tweets: {str(e)}"
        )


@router.get("/fetch-stats")
async def get_fetch_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get statistics about fetched tweets and database status.
    
    Returns:
    - Total tweets in database
    - Tweets by sentiment
    - Most recent fetch time
    - Top hashtags
    - Engagement metrics
    """
    try:
        data_service = DataService(db)
        stats = await data_service.get_database_stats()
        
        return BaseResponse(
            success=True,
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting fetch stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post("/analyze-existing")
async def analyze_existing_tweets(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Re-analyze existing tweets in database (useful if sentiment analysis was updated).
    """
    try:
        data_service = DataService(db)
        
        # Run re-analysis in background
        background_tasks.add_task(data_service.reanalyze_all_tweets)
        
        return BaseResponse(
            success=True,
            data={
                "message": "Re-analysis started in background. This may take a few minutes."
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting re-analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start re-analysis: {str(e)}"
        )
