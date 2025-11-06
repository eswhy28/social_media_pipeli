from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime


class User(Base):
    """Simplified user model for authentication"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SocialPost(Base):
    """Core social media post model - simplified for POC"""
    __tablename__ = "social_posts"

    id = Column(String, primary_key=True)
    platform = Column(String(50), nullable=False, default="twitter")
    handle = Column(String(255), index=True)
    text = Column(Text, nullable=False)
    url = Column(String(500))

    # Engagement metrics
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    engagement_total = Column(Integer, default=0)

    # Sentiment analysis (TextBlob)
    sentiment = Column(String(20))  # positive, negative, neutral
    sentiment_score = Column(Float)  # -1.0 to 1.0
    sentiment_confidence = Column(Float, default=0.0)

    # Metadata
    hashtags = Column(JSON, default=list)
    language = Column(String(10), default="en")
    location = Column(String(255))

    # Timestamps
    posted_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index('idx_posted_at', 'posted_at'),
        Index('idx_sentiment', 'sentiment'),
        Index('idx_platform_posted', 'platform', 'posted_at'),
    )


class SentimentTimeSeries(Base):
    """Time series data for sentiment tracking"""
    __tablename__ = "sentiment_timeseries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Sentiment counts
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)

    # Average scores
    avg_sentiment_score = Column(Float, default=0.0)

    # Engagement metrics
    total_engagement = Column(Integer, default=0)
    avg_engagement = Column(Float, default=0.0)

    # Granularity (hour, day, week)
    granularity = Column(String(20), default="hour")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_timestamp_granularity', 'timestamp', 'granularity'),
    )


class TrendingTopic(Base):
    """Trending hashtags and keywords"""
    __tablename__ = "trending_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False, index=True)
    topic_type = Column(String(50), default="hashtag")  # hashtag, keyword

    # Metrics
    mention_count = Column(Integer, default=0)
    engagement_count = Column(Integer, default=0)
    sentiment_score = Column(Float, default=0.0)

    # Time window
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_topic_window', 'topic', 'window_start'),
    )


class AnomalyDetection(Base):
    """Simple anomaly detection records"""
    __tablename__ = "anomaly_detections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)

    anomaly_type = Column(String(50), nullable=False)  # sentiment_spike, volume_spike
    severity = Column(String(20), default="medium")  # low, medium, high

    # Detection details
    metric_name = Column(String(100))
    expected_value = Column(Float)
    actual_value = Column(Float)
    deviation_score = Column(Float)

    # Context
    description = Column(Text)
    meta_data = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy reserved name

    # Status
    status = Column(String(50), default="new")  # new, acknowledged, resolved

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class APIRateLimit(Base):
    """Track API rate limit usage"""
    __tablename__ = "api_rate_limits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_name = Column(String(50), nullable=False, index=True)  # twitter_search, twitter_timeline

    # Rate limit tracking
    requests_made = Column(Integer, default=0)
    requests_limit = Column(Integer, nullable=False)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)

    # Reset info
    reset_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_api_window', 'api_name', 'window_start'),
    )


class Hashtag(Base):
    """Trending hashtag tracking"""
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(255), nullable=False, unique=True, index=True)
    count = Column(Integer, default=0)
    change = Column(Float, default=0.0)

    # Sentiment breakdown
    sentiment_pos = Column(Integer, default=0)
    sentiment_neg = Column(Integer, default=0)
    sentiment_neu = Column(Integer, default=0)

    # Metadata
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Keyword(Base):
    """Keyword tracking and analysis"""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(255), nullable=False, index=True)
    mentions = Column(Integer, default=0)
    trend = Column(Float, default=0.0)

    # Sentiment split
    sentiment_pos = Column(Integer, default=0)
    sentiment_neg = Column(Integer, default=0)
    sentiment_neu = Column(Integer, default=0)

    # Additional metadata
    category = Column(String(100))
    emotion = Column(String(50))
    sample_text = Column(Text)
    location_hint = Column(String(255))
    score = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Influencer(Base):
    """Influential accounts tracking"""
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    handle = Column(String(255), nullable=False, unique=True, index=True)

    # Metrics
    engagement = Column(Integer, default=0)
    followers_primary = Column(Integer, default=0)
    following = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    avatar_url = Column(String(500))
    engagement_rate = Column(Float, default=0.0)

    # Top mentions
    top_mentions = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Anomaly(Base):
    """Anomaly detection records with detailed information"""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    summary = Column(Text)
    metric = Column(String(100))
    delta = Column(String(50))

    # Status tracking
    status = Column(String(50), default="new")  # new, acknowledged, resolved

    # Additional context
    anomaly_type = Column(String(50))
    expected_value = Column(Float)
    actual_value = Column(Float)
    deviation_score = Column(Float)
    meta_data = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy reserved name

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GeographicData(Base):
    """Geographic distribution data"""
    __tablename__ = "geographic_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(100), nullable=False, index=True)
    mentions = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)

    # Sentiment breakdown
    sentiment_pos = Column(Integer, default=0)
    sentiment_neg = Column(Integer, default=0)
    sentiment_neu = Column(Integer, default=0)

    # Additional data
    top_keywords = Column(JSON, default=list)
    language_distribution = Column(JSON, default=dict)
    coordinates = Column(JSON, default=dict)  # {"lat": 0, "lon": 0}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AlertRule(Base):
    """Alert rules for automated monitoring"""
    __tablename__ = "alert_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)

    # Conditions and actions stored as JSON
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DataConnector(Base):
    """Data source connectors configuration"""
    __tablename__ = "data_connectors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    connector_type = Column(String(50), nullable=False)  # twitter, facebook, etc.
    status = Column(String(50), default="inactive")  # active, inactive, error

    # Configuration stored as JSON
    config = Column(JSON, default=dict)

    # Metrics
    last_sync = Column(DateTime(timezone=True))
    total_posts_synced = Column(Integer, default=0)
    last_24h_posts = Column(Integer, default=0)
    sync_success_rate = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Report(Base):
    """Generated reports tracking"""
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # hashtag, general, person, group
    subject = Column(String(255))
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)

    # Report configuration
    date_range = Column(String(50))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    sections = Column(JSON, default=dict)

    # Output
    file_path = Column(String(500))
    download_url = Column(String(500))

    # Timestamps
    estimated_completion = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SentimentAnalysis(Base):
    """AI-powered sentiment analysis results"""
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, ForeignKey('social_posts.id'), nullable=False, index=True)
    
    # Sentiment results
    label = Column(String(20), nullable=False)  # positive, negative, neutral
    score = Column(Float, nullable=False)  # -1.0 to 1.0
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Model information
    model_name = Column(String(100), nullable=False)  # roberta, textblob, etc.
    model_version = Column(String(50))
    
    # Additional scores (for models that provide multiple outputs)
    all_scores = Column(JSON, default=dict)  # {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
    
    # Analysis metadata
    text_length = Column(Integer)
    language_detected = Column(String(10))
    processing_time_ms = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_sentiment_post_model', 'post_id', 'model_name'),
        Index('idx_sentiment_label_score', 'label', 'score'),
    )


class LocationExtraction(Base):
    """AI-powered location/geographic entity extraction"""
    __tablename__ = "location_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, ForeignKey('social_posts.id'), nullable=False, index=True)
    
    # Location information
    location_text = Column(String(255), nullable=False)  # Extracted location text
    location_type = Column(String(50))  # GPE, LOC, etc.
    confidence = Column(Float, nullable=False)
    
    # Position in text
    start_position = Column(Integer)
    end_position = Column(Integer)
    
    # Model information
    model_name = Column(String(100), nullable=False)  # huggingface, spacy
    model_version = Column(String(50))
    
    # Geographic data (if resolved)
    country = Column(String(100))
    state_province = Column(String(100))
    city = Column(String(100))
    coordinates = Column(JSON)  # {"lat": 0.0, "lon": 0.0}
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_location_post_text', 'post_id', 'location_text'),
        Index('idx_location_type_confidence', 'location_type', 'confidence'),
    )


class EntityExtraction(Base):
    """AI-powered named entity recognition results"""
    __tablename__ = "entity_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, ForeignKey('social_posts.id'), nullable=False, index=True)
    
    # Entity information
    entity_text = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)  # PERSON, ORG, GPE, LOC, etc.
    confidence = Column(Float, nullable=False)
    
    # Position in text
    start_position = Column(Integer)
    end_position = Column(Integer)
    
    # Model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    
    # Additional context
    context_before = Column(String(100))  # Text before entity
    context_after = Column(String(100))   # Text after entity
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    category = Column(String(100))  # Additional categorization
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_entity_post_type', 'post_id', 'entity_type'),
        Index('idx_entity_text_type', 'entity_text', 'entity_type'),
    )


class KeywordExtraction(Base):
    """AI-powered keyword and phrase extraction"""
    __tablename__ = "keyword_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, ForeignKey('social_posts.id'), nullable=False, index=True)
    
    # Keyword information
    keyword_text = Column(String(255), nullable=False)
    keyword_type = Column(String(50))  # noun_phrase, frequent_word, etc.
    relevance_score = Column(Float)
    frequency = Column(Integer, default=1)
    
    # Model information
    extraction_method = Column(String(100))  # textblob, frequency, etc.
    
    # Context
    context = Column(Text)  # Surrounding context
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_keyword_post_text', 'post_id', 'keyword_text'),
        Index('idx_keyword_type_score', 'keyword_type', 'relevance_score'),
    )


class AIAnalysisSession(Base):
    """Track AI analysis sessions for posts"""
    __tablename__ = "ai_analysis_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String, ForeignKey('social_posts.id'), nullable=False, index=True)
    
    # Session information
    session_type = Column(String(50), nullable=False)  # comprehensive, sentiment_only, etc.
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Models used
    models_used = Column(JSON, default=list)  # List of model names
    
    # Results summary
    sentiment_result = Column(JSON)
    locations_found = Column(Integer, default=0)
    entities_found = Column(Integer, default=0)
    keywords_found = Column(Integer, default=0)
    
    # Performance metrics
    processing_time_seconds = Column(Float)
    total_tokens_processed = Column(Integer)
    
    # Error information
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_analysis_post_status', 'post_id', 'status'),
        Index('idx_analysis_session_type', 'session_type'),
    )


class ModelPerformance(Base):
    """Track AI model performance metrics"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50))
    task_type = Column(String(50), nullable=False)  # sentiment, ner, keyword_extraction
    
    # Performance metrics
    avg_processing_time_ms = Column(Float)
    avg_confidence_score = Column(Float)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Resource usage
    avg_memory_usage_mb = Column(Float)
    avg_cpu_usage_percent = Column(Float)
    
    # Time window for metrics
    measurement_start = Column(DateTime(timezone=True), nullable=False)
    measurement_end = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_model_perf_name_task', 'model_name', 'task_type'),
        Index('idx_model_perf_time_window', 'measurement_start', 'measurement_end'),
    )
