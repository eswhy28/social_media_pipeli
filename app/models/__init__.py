from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # user, admin
    permissions = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    alert_rules = relationship("AlertRule", back_populates="user")
    reports = relationship("Report", back_populates="user")


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(String, primary_key=True)
    platform = Column(String(50), nullable=False)  # twitter, facebook, etc.
    handle = Column(String(255), index=True)
    text = Column(Text, nullable=False)
    url = Column(String(500))

    # Engagement metrics
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    engagement_total = Column(Integer, default=0)

    # Sentiment
    sentiment = Column(String(20))  # positive, negative, neutral
    sentiment_score = Column(Float)

    # Metadata
    topics = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    language = Column(String(10))
    location = Column(String(255))
    state = Column(String(100))

    # Timestamps
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_posts_sentiment', 'sentiment'),
        Index('ix_posts_posted_at', 'posted_at'),
        Index('ix_posts_platform_posted_at', 'platform', 'posted_at'),
    )


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    count = Column(Integer, default=0)
    sentiment_pos = Column(Integer, default=0)
    sentiment_neg = Column(Integer, default=0)
    sentiment_neu = Column(Integer, default=0)

    # Trends
    change_percentage = Column(Float, default=0.0)
    trending_score = Column(Float, default=0.0)

    # Metadata
    top_posts = Column(JSON, default=list)
    geographic_distribution = Column(JSON, default=dict)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(255), nullable=False, index=True)
    mentions = Column(Integer, default=0)
    trend = Column(Float, default=0.0)

    # Sentiment
    sentiment_pos = Column(Integer, default=0)
    sentiment_neg = Column(Integer, default=0)
    sentiment_neu = Column(Integer, default=0)

    # Metadata
    category = Column(String(100))
    emotion = Column(String(100))
    location_hint = Column(String(255))
    sample_text = Column(Text)
    score = Column(Float)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True)
    handle = Column(String(255), unique=True, nullable=False, index=True)
    platform = Column(String(50), nullable=False)

    # Profile
    name = Column(String(255))
    verified = Column(Boolean, default=False)
    avatar_url = Column(String(500))

    # Metrics
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    engagement_total = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Content
    top_mentions = Column(JSON, default=list)
    top_topics = Column(JSON, default=list)
    sentiment_distribution = Column(JSON, default=dict)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high
    metric = Column(String(100), nullable=False)
    delta = Column(String(50))
    summary = Column(Text)

    # Status
    status = Column(String(20), default="new")  # new, acknowledged, resolved

    # Data
    affected_keywords = Column(JSON, default=list)
    timeline = Column(JSON, default=list)
    related_posts = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index('ix_anomalies_severity_status', 'severity', 'status'),
    )


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)

    # Conditions
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="alert_rules")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    template = Column(String(50), nullable=False)  # hashtag, general, person, group
    subject = Column(String(255), nullable=False)
    date_range = Column(String(50))

    # Status
    status = Column(String(20), default="generating")  # generating, completed, failed
    progress = Column(Integer, default=0)

    # Data
    sections = Column(JSON, default=dict)
    download_url = Column(String(500))
    file_path = Column(String(500))

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="reports")

    __table_args__ = (
        Index('ix_reports_user_status', 'user_id', 'status'),
    )


class DataConnector(Base):
    __tablename__ = "data_connectors"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="disconnected")  # connected, disconnected

    # Config
    config = Column(JSON, default=dict)
    credentials = Column(JSON, default=dict)  # encrypted

    # Metrics
    total_posts = Column(Integer, default=0)
    last_24h_posts = Column(Integer, default=0)
    sync_success_rate = Column(Float, default=0.0)

    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SentimentTimeSeries(Base):
    __tablename__ = "sentiment_timeseries"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    granularity = Column(String(20), nullable=False)  # hour, day, week, month

    # Sentiment counts
    positive = Column(Integer, default=0)
    negative = Column(Integer, default=0)
    neutral = Column(Integer, default=0)

    # Calculated metrics
    sentiment_score = Column(Float)  # -100 to 100
    total_mentions = Column(Integer, default=0)

    __table_args__ = (
        Index('ix_sentiment_ts_granularity', 'timestamp', 'granularity'),
    )


class GeographicData(Base):
    __tablename__ = "geographic_data"

    id = Column(Integer, primary_key=True)
    state = Column(String(100), nullable=False, index=True)

    # Metrics
    mentions = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)

    # Sentiment
    sentiment_pos = Column(Integer, default=0)
    sentiment_neg = Column(Integer, default=0)
    sentiment_neu = Column(Integer, default=0)

    # Metadata
    top_keywords = Column(JSON, default=list)
    language_distribution = Column(JSON, default=dict)
    coordinates = Column(JSON)  # {lat, lon}

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

