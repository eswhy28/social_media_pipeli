"""
Extended AI Analysis Models for ApifyScrapedData
Tracks AI processing status and results for scraped social media data
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base
import uuid


class ApifyDataProcessingStatus(Base):
    """Track which ApifyScrapedData records have been processed by AI services"""
    __tablename__ = "apify_data_processing_status"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scraped_data_id = Column(String, ForeignKey('apify_scraped_data.id'), nullable=False, unique=True, index=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False, index=True)
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    
    # Individual service status
    sentiment_processed = Column(Boolean, default=False)
    location_processed = Column(Boolean, default=False)
    entity_processed = Column(Boolean, default=False)
    keyword_processed = Column(Boolean, default=False)
    
    # Processing details
    processing_attempts = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_processing_status', 'is_processed'),
        Index('idx_scraped_data_processed', 'scraped_data_id', 'is_processed'),
    )


class ApifySentimentAnalysis(Base):
    """Sentiment analysis results for ApifyScrapedData"""
    __tablename__ = "apify_sentiment_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_data_id = Column(String, ForeignKey('apify_scraped_data.id'), nullable=False, index=True)
    
    # Sentiment results
    label = Column(String(20), nullable=False)  # positive, negative, neutral
    score = Column(Float, nullable=False)  # -1.0 to 1.0
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    
    # Additional scores
    all_scores = Column(JSON, default=dict)  # {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
    
    # Analysis metadata
    text_length = Column(Integer)
    language_detected = Column(String(10))
    processing_time_ms = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_apify_sentiment_data', 'scraped_data_id', 'model_name'),
        Index('idx_apify_sentiment_label', 'label', 'score'),
    )


class ApifyLocationExtraction(Base):
    """Location extraction results for ApifyScrapedData"""
    __tablename__ = "apify_location_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_data_id = Column(String, ForeignKey('apify_scraped_data.id'), nullable=False, index=True)
    
    # Location information
    location_text = Column(String(255), nullable=False)
    location_type = Column(String(50))  # GPE, LOC, CITY, STATE, etc.
    confidence = Column(Float, nullable=False)
    
    # Position in text
    start_position = Column(Integer)
    end_position = Column(Integer)
    
    # Model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    
    # Geographic data (geocoded)
    country = Column(String(100))
    state_province = Column(String(100))
    city = Column(String(100))
    region = Column(String(100))  # Nigerian region
    coordinates = Column(JSON)  # {"lat": 0.0, "lon": 0.0}
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_apify_location_data', 'scraped_data_id', 'location_text'),
        Index('idx_apify_location_type', 'location_type', 'confidence'),
    )


class ApifyEntityExtraction(Base):
    """Entity extraction results for ApifyScrapedData"""
    __tablename__ = "apify_entity_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_data_id = Column(String, ForeignKey('apify_scraped_data.id'), nullable=False, index=True)
    
    # Entity information
    entity_text = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)  # PERSON, ORG, GPE, LOC, EVENT, etc.
    confidence = Column(Float, nullable=False)
    
    # Position in text
    start_position = Column(Integer)
    end_position = Column(Integer)
    
    # Model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    
    # Additional context
    context_before = Column(String(100))
    context_after = Column(String(100))
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    category = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_apify_entity_data', 'scraped_data_id', 'entity_type'),
        Index('idx_apify_entity_text', 'entity_text', 'entity_type'),
    )


class ApifyKeywordExtraction(Base):
    """Keyword extraction results for ApifyScrapedData"""
    __tablename__ = "apify_keyword_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_data_id = Column(String, ForeignKey('apify_scraped_data.id'), nullable=False, index=True)
    
    # Keyword information
    keyword_text = Column(String(255), nullable=False)
    keyword_type = Column(String(50))  # noun_phrase, topic, key_term, etc.
    relevance_score = Column(Float)
    frequency = Column(Integer, default=1)
    
    # Model information
    extraction_method = Column(String(100))
    
    # Context
    context = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_apify_keyword_data', 'scraped_data_id', 'keyword_text'),
        Index('idx_apify_keyword_score', 'keyword_type', 'relevance_score'),
    )


class ApifyAIBatchJob(Base):
    """Track batch AI processing jobs"""
    __tablename__ = "apify_ai_batch_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Job information
    job_type = Column(String(50), nullable=False)  # sentiment, location, entity, keyword, comprehensive
    status = Column(String(20), default="pending", index=True)  # pending, processing, completed, failed, partial
    
    # Batch details
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    skipped_records = Column(Integer, default=0)  # Already processed
    
    # Processing configuration
    config = Column(JSON)  # Model names, parameters, etc.
    
    # Results summary
    results_summary = Column(JSON)  # Aggregated results
    
    # Performance metrics
    processing_time_seconds = Column(Float)
    avg_time_per_record = Column(Float)
    
    # Error tracking
    errors = Column(JSON)  # List of errors encountered
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_batch_job_status', 'status', 'job_type'),
        Index('idx_batch_job_created', 'created_at'),
    )
