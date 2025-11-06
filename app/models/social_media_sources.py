"""
Extended database models for new social media data sources
Supports Google Trends, TikTok, Facebook, and Apify scraped data
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Text, Index
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime


class GoogleTrendsData(Base):
    """Model for Google Trends data"""
    __tablename__ = "google_trends_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Trend information
    keyword = Column(String(255), nullable=False, index=True)
    trend_type = Column(String(50))  # trending_search, interest_over_time, regional, related

    # Data
    data_json = Column(JSON)  # Store the full trend data
    interest_value = Column(Integer, default=0)
    rank = Column(Integer)

    # Geographic information
    geo_region = Column(String(10), default="NG", index=True)  # ISO country code
    sub_region = Column(String(50))  # State/province for regional data

    # Temporal information
    timeframe = Column(String(50))  # e.g., "today 3-m", "today 12-m"
    trend_date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Metadata
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_keyword_date', 'keyword', 'trend_date'),
        Index('idx_geo_date', 'geo_region', 'trend_date'),
    )


class TikTokContent(Base):
    """Model for TikTok video content"""
    __tablename__ = "tiktok_content"

    id = Column(String, primary_key=True)  # TikTok video ID

    # Author information
    author_username = Column(String(255), index=True)
    author_nickname = Column(String(255))
    author_verified = Column(Boolean, default=False)
    author_follower_count = Column(Integer, default=0)

    # Content
    description = Column(Text)
    duration = Column(Integer)  # Video duration in seconds
    music_title = Column(String(500))

    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Hashtags and categorization
    hashtags = Column(JSON, default=list)

    # Geographic information
    geo_location = Column(String(100), default="Nigeria")

    # Timestamps
    posted_at = Column(DateTime(timezone=True))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_author_posted', 'author_username', 'posted_at'),
        Index('idx_engagement', 'engagement_rate'),
        Index('idx_posted_at', 'posted_at'),
    )


class FacebookContent(Base):
    """Model for Facebook post content"""
    __tablename__ = "facebook_content"

    id = Column(String, primary_key=True)  # Facebook post ID

    # Page/Author information
    page_name = Column(String(255), index=True)
    author = Column(String(255))

    # Content
    text = Column(Text)
    post_text = Column(Text)
    has_image = Column(Boolean, default=False)
    has_video = Column(Boolean, default=False)
    link = Column(String(1000))
    post_url = Column(String(1000))

    # Engagement metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)

    # Reactions breakdown
    reactions_json = Column(JSON)  # Store all reaction types

    # Media information
    images = Column(JSON, default=list)
    video_url = Column(String(1000))

    # Geographic information
    geo_location = Column(String(100), default="Nigeria")

    # Timestamps
    posted_at = Column(DateTime(timezone=True), index=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_page_posted', 'page_name', 'posted_at'),
        Index('idx_engagement_posted', 'total_engagement', 'posted_at'),
    )


class ApifyScrapedData(Base):
    """Model for Apify scraped data from various platforms"""
    __tablename__ = "apify_scraped_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Source information
    platform = Column(String(50), nullable=False, index=True)  # instagram, tiktok, twitter, etc.
    source_id = Column(String(255), index=True)  # Platform-specific ID
    actor_id = Column(String(255))  # Apify actor used
    run_id = Column(String(255))  # Apify run ID

    # Author/Account information
    author = Column(String(255), index=True)
    account_name = Column(String(255))

    # Content
    content = Column(Text)
    content_type = Column(String(50))  # post, video, story, etc.

    # Metrics (flexible JSON for different platforms)
    metrics_json = Column(JSON)  # All engagement metrics

    # Additional data
    hashtags = Column(JSON, default=list)
    mentions = Column(JSON, default=list)
    media_urls = Column(JSON, default=list)

    # Raw data backup
    raw_data = Column(JSON)  # Store full scraped data

    # Geographic information
    location = Column(String(255))
    geo_location = Column(String(100), default="Nigeria")

    # Timestamps
    posted_at = Column(DateTime(timezone=True))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_platform_posted', 'platform', 'posted_at'),
        Index('idx_author_platform', 'author', 'platform'),
        Index('idx_source_platform', 'source_id', 'platform'),
    )


class SocialMediaAggregation(Base):
    """Aggregated metrics across all platforms"""
    __tablename__ = "social_media_aggregation"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Time period
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    granularity = Column(String(20), default="hour")  # hour, day, week

    # Platform breakdown
    platform = Column(String(50), index=True)  # twitter, tiktok, facebook, google_trends, etc.

    # Content counts
    total_posts = Column(Integer, default=0)
    total_videos = Column(Integer, default=0)
    total_trends = Column(Integer, default=0)

    # Engagement metrics
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)

    # Top content
    top_hashtags = Column(JSON, default=list)  # Top 10 hashtags for the period
    top_keywords = Column(JSON, default=list)  # Top 10 keywords
    top_authors = Column(JSON, default=list)  # Top 10 authors by engagement

    # Geographic
    geo_region = Column(String(100), default="Nigeria")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_timestamp_platform', 'timestamp', 'platform'),
        Index('idx_timestamp_granularity', 'timestamp', 'granularity'),
    )


class DataSourceMonitoring(Base):
    """Track data source health and collection status"""
    __tablename__ = "data_source_monitoring"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Source information
    source_type = Column(String(50), nullable=False, index=True)  # google_trends, tiktok, facebook, apify
    source_name = Column(String(255))  # Specific account, page, or hashtag

    # Status
    status = Column(String(50), default="active")  # active, paused, failed, rate_limited
    last_successful_fetch = Column(DateTime(timezone=True))
    last_attempt = Column(DateTime(timezone=True))

    # Metrics
    total_items_collected = Column(Integer, default=0)
    items_collected_today = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)

    # Error tracking
    last_error = Column(Text)
    error_count = Column(Integer, default=0)

    # Rate limiting info
    rate_limit_reset = Column(DateTime(timezone=True))
    requests_remaining = Column(Integer)

    # Configuration
    collection_frequency = Column(Integer, default=3600)  # seconds
    priority = Column(Integer, default=1)  # 1=high, 5=low

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_source_status', 'source_type', 'status'),
        Index('idx_last_fetch', 'last_successful_fetch'),
    )
