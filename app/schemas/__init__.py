from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnomalyStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class DateRange(str, Enum):
    TODAY = "Today"
    LAST_7_DAYS = "Last 7 Days"
    LAST_30_DAYS = "Last 30 Days"
    LAST_90_DAYS = "Last 90 Days"
    CUSTOM = "Custom"


class Granularity(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


# Base Response
class BaseResponse(BaseModel):
    success: bool = True
    error: Optional[Dict[str, Any]] = None


# Auth Schemas
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    permissions: List[str]


class LoginResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Sentiment Schemas
class SentimentDistribution(BaseModel):
    pos: int = 0
    neg: int = 0
    neu: int = 0


class MetricsData(BaseModel):
    total_mentions: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    engagement_rate: float = 0.0


class TrendingHashtag(BaseModel):
    tag: str
    count: int
    change: float


class TrendingKeyword(BaseModel):
    keyword: str
    count: int
    change: float


class AnomalySummary(BaseModel):
    id: str
    title: str
    severity: str
    detected_at: datetime
    summary: str
    metric: str
    delta: str


class OverviewResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None


class LiveSentimentResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None


# Hashtag Schemas
class TopPost(BaseModel):
    handle: str
    text: str
    url: str
    engagement: str


class HashtagDetail(BaseModel):
    tag: str
    count: int
    change: float
    sentiment: SentimentDistribution
    top_posts: List[TopPost] = []


class TrendingHashtagsResponse(BaseResponse):
    data: List[HashtagDetail] = []


# Keyword Schemas
class KeywordTrend(BaseModel):
    keyword: str
    mentions: int
    trend: float
    split: SentimentDistribution
    emotion: Optional[str] = None
    sample: Optional[str] = None
    category: Optional[str] = None
    location_hint: Optional[str] = None
    score: float = 0.0


class KeywordTrendsResponse(BaseResponse):
    data: List[KeywordTrend] = []


# Influencer Schemas
class InfluencerData(BaseModel):
    handle: str
    engagement: int
    followers_primary: int
    following: int
    verified: bool
    avatar_url: Optional[str] = None
    engagement_rate: float
    top_mentions: List[Dict[str, Any]] = []


class InfluencersResponse(BaseResponse):
    data: List[InfluencerData] = []


# Post Schemas
class SocialPostData(BaseModel):
    id: str
    handle: str
    text: str
    url: str
    engagement: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    posted_at: datetime
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    topics: List[str] = []
    language: Optional[str] = None


class TopPostsResponse(BaseResponse):
    data: List[SocialPostData] = []


class SearchPostsRequest(BaseModel):
    q: str
    range: DateRange = DateRange.LAST_7_DAYS
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
    sentiment: Optional[SentimentType] = None
    language: Optional[str] = None


class PaginationInfo(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool


class SearchPostsResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None


# Anomaly Schemas
class AnomalyDetail(BaseModel):
    id: str
    title: str
    severity: str
    detected_at: datetime
    summary: str
    metric: str
    delta: str
    status: str
    affected_keywords: List[str] = []
    timeline: List[Dict[str, Any]] = []
    related_posts: List[Dict[str, Any]] = []
    recommendations: List[str] = []


class AnomaliesResponse(BaseResponse):
    data: List[AnomalySummary] = []


class AnomalyDetailResponse(BaseResponse):
    data: Optional[AnomalyDetail] = None


# Alert Rule Schemas
class AlertConditions(BaseModel):
    metric: str
    threshold: float
    time_window: str
    comparison: str


class CreateAlertRuleRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    conditions: AlertConditions
    actions: List[str] = []
    enabled: bool = True


class AlertRuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    enabled: bool
    conditions: AlertConditions
    actions: List[str]
    created_at: datetime
    updated_at: Optional[datetime]


class AlertRulesResponse(BaseResponse):
    data: List[AlertRuleResponse] = []


# Geographic Schemas
class GeographicState(BaseModel):
    state: str
    mentions: int
    percentage: float
    sentiment: SentimentDistribution
    top_keywords: List[str] = []
    language_distribution: Dict[str, float] = {}


class GeographicStatesResponse(BaseResponse):
    data: List[GeographicState] = []


# AI Schemas
class AIGenerateRequest(BaseModel):
    section: str = Field(..., pattern="^(overview|timeline|sentiment|narratives|geo|influencers|topPosts|claims|appendix)$")
    subject: str
    template: str = Field(..., pattern="^(hashtag|general|person|group)$")
    range: str
    context: Dict[str, Any]


class AIGenerateResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None


# Report Schemas
class ReportSections(BaseModel):
    overview: bool = True
    timeline: bool = True
    sentiment: bool = True
    narratives: bool = True
    geo: bool = True
    influencers: bool = True
    topPosts: bool = True
    claims: bool = False
    appendix: bool = True


class GenerateReportRequest(BaseModel):
    template: str = Field(..., pattern="^(hashtag|general|person|group)$")
    subject: str
    range: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sections: ReportSections = ReportSections()


class ReportStatusData(BaseModel):
    report_id: str
    status: str
    progress: int = 0
    estimated_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None


class GenerateReportResponse(BaseResponse):
    data: Optional[ReportStatusData] = None


class ReportStatusResponse(BaseResponse):
    data: Optional[ReportStatusData] = None


# Data Connector Schemas
class ConnectorConfig(BaseModel):
    api_version: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[str] = None


class ConnectorMetrics(BaseModel):
    total_posts: int = 0
    last_24h_posts: int = 0
    sync_success_rate: float = 0.0


class DataConnectorData(BaseModel):
    id: str
    name: str
    description: str
    status: str
    last_sync: Optional[datetime]
    config: ConnectorConfig
    metrics: ConnectorMetrics


class ConnectorsResponse(BaseResponse):
    data: List[DataConnectorData] = []


class ConnectDataSourceRequest(BaseModel):
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str


# Sentiment Time Series Schemas
class SentimentSeriesPoint(BaseModel):
    name: str
    pos: int
    neg: int
    neu: int


class SentimentSeriesSummary(BaseModel):
    average_sentiment: float
    trend: str
    volatility: str


class SentimentSeriesResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None


# Error Response
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]

