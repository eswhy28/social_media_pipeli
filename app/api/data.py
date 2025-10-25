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


@router.get("/sentiment/series")
async def get_sentiment_series(
    range: str = Query("Last 7 Days"),
    granularity: str = Query("day", description="hour, day, week, month"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sentiment time series data"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select
        from datetime import datetime, timedelta

        # Parse date range
        if range == "Today":
            start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        elif range == "Last 7 Days":
            start = datetime.utcnow() - timedelta(days=7)
        elif range == "Last 30 Days":
            start = datetime.utcnow() - timedelta(days=30)
        elif range == "Last 90 Days":
            start = datetime.utcnow() - timedelta(days=90)
        else:
            start = datetime.utcnow() - timedelta(days=7)

        # Get posts
        result = await db.execute(
            select(SocialPost).where(SocialPost.posted_at >= start)
        )
        posts = result.scalars().all()

        # Group by time buckets
        series_data = {}
        for post in posts:
            if granularity == "hour":
                key = post.posted_at.strftime("%Y-%m-%d %H:00")
            elif granularity == "day":
                key = post.posted_at.strftime("%a")
            elif granularity == "week":
                key = f"Week {post.posted_at.isocalendar()[1]}"
            else:
                key = post.posted_at.strftime("%B")

            if key not in series_data:
                series_data[key] = {"pos": 0, "neg": 0, "neu": 0}

            if post.sentiment == "positive":
                series_data[key]["pos"] += 1
            elif post.sentiment == "negative":
                series_data[key]["neg"] += 1
            else:
                series_data[key]["neu"] += 1

        series = [{"name": k, **v} for k, v in series_data.items()]

        return BaseResponse(success=True, data={"series": series})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/top")
async def get_top_posts(
    limit: int = Query(20, ge=1, le=100),
    range: str = Query("Last 7 Days"),
    min_engagement: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top performing posts by engagement"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select, desc
        from datetime import datetime, timedelta

        # Parse date range
        if range == "Today":
            start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        elif range == "Last 7 Days":
            start = datetime.utcnow() - timedelta(days=7)
        elif range == "Last 30 Days":
            start = datetime.utcnow() - timedelta(days=30)
        else:
            start = datetime.utcnow() - timedelta(days=7)

        query = select(SocialPost).where(
            SocialPost.posted_at >= start,
            SocialPost.engagement_total >= min_engagement
        ).order_by(desc(SocialPost.engagement_total)).limit(limit)

        result = await db.execute(query)
        posts = result.scalars().all()

        posts_data = [
            {
                "id": post.id,
                "handle": post.handle,
                "text": post.text,
                "url": post.url or f"https://twitter.com/{post.handle}/status/{post.id}",
                "engagement": f"{post.engagement_total/1000:.1f}K" if post.engagement_total >= 1000 else str(post.engagement_total),
                "likes": post.likes,
                "retweets": post.retweets,
                "replies": post.replies,
                "posted_at": post.posted_at.isoformat(),
                "sentiment": post.sentiment,
                "sentiment_score": post.sentiment_score
            }
            for post in posts
        ]

        return BaseResponse(success=True, data={"posts": posts_data, "count": len(posts_data)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/search")
async def search_posts(
    q: str = Query(..., description="Search query"),
    range: str = Query("Last 7 Days"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sentiment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search posts by content, keywords, or hashtags"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select, or_, desc, func
        from datetime import datetime, timedelta

        # Parse date range
        if range == "Today":
            start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        elif range == "Last 7 Days":
            start = datetime.utcnow() - timedelta(days=7)
        elif range == "Last 30 Days":
            start = datetime.utcnow() - timedelta(days=30)
        else:
            start = datetime.utcnow() - timedelta(days=7)

        # Build query
        query = select(SocialPost).where(
            SocialPost.posted_at >= start,
            or_(
                SocialPost.text.ilike(f"%{q}%"),
                SocialPost.handle.ilike(f"%{q}%")
            )
        )

        if sentiment:
            query = query.where(SocialPost.sentiment == sentiment)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.order_by(desc(SocialPost.posted_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        posts = result.scalars().all()

        posts_data = [
            {
                "id": post.id,
                "handle": post.handle,
                "text": post.text,
                "url": post.url or f"https://twitter.com/{post.handle}/status/{post.id}",
                "engagement": f"{post.engagement_total/1000:.1f}K" if post.engagement_total >= 1000 else str(post.engagement_total),
                "posted_at": post.posted_at.isoformat(),
                "sentiment": post.sentiment,
                "relevance_score": 0.85
            }
            for post in posts
        ]

        return BaseResponse(success=True, data={
            "posts": posts_data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtags/{tag}")
async def get_hashtag_detail(
    tag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed hashtag analysis"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select
        from datetime import datetime, timedelta

        # Clean tag
        tag = tag.replace("#", "")

        # Get posts with this hashtag from last 7 days
        start_date = datetime.utcnow() - timedelta(days=7)

        result = await db.execute(
            select(SocialPost).where(
                SocialPost.posted_at >= start_date
            )
        )
        all_posts = result.scalars().all()

        # Filter posts containing the hashtag
        matching_posts = [p for p in all_posts if p.hashtags and tag in p.hashtags]

        # Calculate sentiment
        sentiment_counts = {"pos": 0, "neg": 0, "neu": 0}
        for post in matching_posts:
            if post.sentiment == "positive":
                sentiment_counts["pos"] += 1
            elif post.sentiment == "negative":
                sentiment_counts["neg"] += 1
            else:
                sentiment_counts["neu"] += 1

        # Get top posts
        top_posts = sorted(matching_posts, key=lambda x: x.engagement_total, reverse=True)[:5]
        top_posts_data = [
            {
                "handle": post.handle,
                "text": post.text[:100] + "..." if len(post.text) > 100 else post.text,
                "url": post.url or f"https://twitter.com/{post.handle}/status/{post.id}",
                "engagement": f"{post.engagement_total/1000:.1f}K" if post.engagement_total >= 1000 else str(post.engagement_total)
            }
            for post in top_posts
        ]

        data = {
            "title": f"#{tag}",
            "summary": f"Analysis of #{tag} over the last 7 days",
            "mentions": len(matching_posts),
            "sentiment": sentiment_counts,
            "top_posts": top_posts_data
        }

        return BaseResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/influencers")
async def get_influencers(
    limit: int = Query(20, ge=1, le=100),
    min_followers: int = Query(100000),
    verified_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get influential accounts and their metrics"""
    try:
        from app.models import SocialPost
        from sqlalchemy import select, func, desc

        # Get handles with most engagement
        result = await db.execute(
            select(
                SocialPost.handle,
                func.sum(SocialPost.engagement_total).label('total_engagement'),
                func.count(SocialPost.id).label('post_count')
            ).group_by(SocialPost.handle)
            .order_by(desc('total_engagement'))
            .limit(limit)
        )

        influencers = []
        for row in result:
            influencers.append({
                "handle": row.handle,
                "engagement": int(row.total_engagement),
                "followers_primary": min_followers,
                "following": 280,
                "verified": True if row.total_engagement > 50000 else False,
                "engagement_rate": 0.002,
                "post_count": row.post_count
            })

        return BaseResponse(success=True, data={"influencers": influencers, "count": len(influencers)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geographic/states")
async def get_geographic_states(
    range: str = Query("Last 7 Days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get geographic distribution data for Nigeria states"""
    try:
        from datetime import datetime, timedelta

        # Mock geographic data for Nigerian states
        states_data = [
            {
                "state": "Lagos",
                "mentions": 125000,
                "percentage": 72,
                "sentiment": {"pos": 45, "neg": 25, "neu": 30},
                "top_keywords": ["Economy", "Technology", "Entertainment"]
            },
            {
                "state": "Abuja",
                "mentions": 45000,
                "percentage": 26,
                "sentiment": {"pos": 40, "neg": 30, "neu": 30},
                "top_keywords": ["Politics", "Governance", "Policy"]
            }
        ]

        return BaseResponse(success=True, data={"states": states_data, "count": len(states_data)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies")
async def get_anomalies(
    severity: Optional[str] = None,
    status: str = Query("new"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detected anomalies and alerts"""
    try:
        from app.models import Anomaly
        from sqlalchemy import select, desc

        query = select(Anomaly).order_by(desc(Anomaly.detected_at)).limit(limit)

        if severity:
            query = query.where(Anomaly.severity == severity)

        if status:
            query = query.where(Anomaly.status == status)

        result = await db.execute(query)
        anomalies = result.scalars().all()

        anomalies_data = [
            {
                "id": str(anomaly.id),
                "title": anomaly.title,
                "severity": anomaly.severity,
                "detected_at": anomaly.detected_at.isoformat(),
                "summary": anomaly.summary,
                "metric": anomaly.metric,
                "delta": anomaly.delta,
                "status": anomaly.status
            }
            for anomaly in anomalies
        ]

        return BaseResponse(success=True, data={"anomalies": anomalies_data, "count": len(anomalies_data)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connectors")
async def get_connectors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get data source connectors and their status"""
    try:
        from datetime import datetime, timedelta

        # Mock connector data for POC
        connectors = [
            {
                "id": "twitter",
                "name": "X (Twitter) API",
                "description": "Search, filtered stream, historical backfill",
                "status": "connected",
                "last_sync": datetime.utcnow().isoformat(),
                "config": {
                    "api_version": "v2",
                    "rate_limit_remaining": 450,
                    "rate_limit_reset": (datetime.utcnow() + timedelta(hours=1)).isoformat()
                },
                "metrics": {
                    "total_posts": 800,
                    "last_24h_posts": 150,
                    "sync_success_rate": 99.8
                }
            }
        ]

        return BaseResponse(success=True, data={"connectors": connectors, "count": len(connectors)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


