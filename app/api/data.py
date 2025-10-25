from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User
from app.services.data_service import DataService
from pydantic import BaseModel

router = APIRouter()


class BaseResponse(BaseModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("/overview")
async def get_overview(
    range: str = Query("Last 7 Days", description="Date range for analytics"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview dashboard data with sentiment analysis

    Returns:
    - total_posts: Number of posts in the date range
    - total_engagement: Total likes + retweets + replies
    - unique_users: Number of unique users/handles
    - sentiment: Breakdown of positive/negative/neutral posts
    """
    try:
        data_service = DataService(db)
        overview_data = await data_service.get_overview(range, start_date, end_date)

        return BaseResponse(success=True, data=overview_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/live")
async def get_live_sentiment(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time sentiment gauge value"""
    try:
        data_service = DataService(db)

        # Get recent sentiment data
        overview = await data_service.get_overview("Last 7 Days")

        # Calculate sentiment score (-100 to +100)
        sentiment = overview.get("sentiment", {})
        total = sentiment.get("positive", 0) + sentiment.get("negative", 0) + sentiment.get("neutral", 0)

        if total == 0:
            sentiment_score = 0
        else:
            positive_ratio = sentiment.get("positive", 0) / total
            negative_ratio = sentiment.get("negative", 0) / total
            sentiment_score = round((positive_ratio - negative_ratio) * 100, 1)

        data = {
            "sentiment_score": sentiment_score,
            "distribution": sentiment,
            "total_posts": total
        }

        return BaseResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/recent")
async def get_recent_posts(
    limit: int = Query(10, ge=1, le=100),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment: positive, negative, neutral"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent posts with sentiment analysis"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select, desc

        query = select(SocialPost).order_by(desc(SocialPost.posted_at)).limit(limit)

        if sentiment:
            query = query.where(SocialPost.sentiment == sentiment)

        result = await db.execute(query)
        posts = result.scalars().all()

        posts_data = [
            {
                "id": post.id,
                "handle": post.handle,
                "text": post.text,
                "platform": post.platform,
                "likes": post.likes,
                "retweets": post.retweets,
                "replies": post.replies,
                "engagement_total": post.engagement_total,
                "sentiment": post.sentiment,
                "sentiment_score": post.sentiment_score,
                "hashtags": post.hashtags,
                "posted_at": post.posted_at.isoformat(),
                "location": post.location
            }
            for post in posts
        ]

        return BaseResponse(success=True, data={"posts": posts_data, "count": len(posts_data)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtags/trending")
async def get_trending_hashtags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trending hashtags from posts"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select, func
        from datetime import datetime, timedelta

        # Get posts from last 7 days
        start_date = datetime.utcnow() - timedelta(days=7)

        result = await db.execute(
            select(SocialPost.hashtags).where(
                SocialPost.posted_at >= start_date
            )
        )
        posts = result.scalars().all()

        # Count hashtags
        hashtag_counts = {}
        for post_hashtags in posts:
            if post_hashtags:
                for tag in post_hashtags:
                    hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1

        # Sort and limit
        trending = [
            {"tag": tag, "count": count}
            for tag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]

        return BaseResponse(success=True, data={"hashtags": trending, "count": len(trending)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall statistics"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select, func

        # Total posts
        total_result = await db.execute(select(func.count(SocialPost.id)))
        total_posts = total_result.scalar()

        # Sentiment breakdown
        sentiment_result = await db.execute(
            select(
                SocialPost.sentiment,
                func.count(SocialPost.id).label('count')
            ).group_by(SocialPost.sentiment)
        )
        sentiment_data = {row.sentiment: row.count for row in sentiment_result}

        # Total engagement
        engagement_result = await db.execute(
            select(func.sum(SocialPost.engagement_total))
        )
        total_engagement = engagement_result.scalar() or 0

        # Unique users
        users_result = await db.execute(
            select(func.count(func.distinct(SocialPost.handle)))
        )
        unique_users = users_result.scalar()

        data = {
            "total_posts": total_posts,
            "total_engagement": int(total_engagement),
            "unique_users": unique_users,
            "sentiment": {
                "positive": sentiment_data.get("positive", 0),
                "negative": sentiment_data.get("negative", 0),
                "neutral": sentiment_data.get("neutral", 0)
            }
        }

        return BaseResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

