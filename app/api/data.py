from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User, SocialPost, Hashtag, Keyword, Influencer, Anomaly, GeographicData, SentimentTimeSeries
from app.schemas import (
    OverviewResponse, LiveSentimentResponse, SentimentSeriesResponse,
    TrendingHashtagsResponse, KeywordTrendsResponse, InfluencersResponse,
    TopPostsResponse, SearchPostsRequest, SearchPostsResponse,
    AnomaliesResponse, AnomalyDetailResponse, GeographicStatesResponse,
    DateRange, SentimentType
)
from app.services.data_service import DataService
import random

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    range: str = Query("Last 7 Days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview dashboard data"""
    data_service = DataService(db)
    overview_data = await data_service.get_overview(range, start_date, end_date)

    return OverviewResponse(success=True, data=overview_data)


@router.get("/sentiment/live", response_model=LiveSentimentResponse)
async def get_live_sentiment(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time sentiment gauge value"""
    data_service = DataService(db)
    sentiment_data = await data_service.get_live_sentiment()

    return LiveSentimentResponse(success=True, data=sentiment_data)


@router.get("/sentiment/series", response_model=SentimentSeriesResponse)
async def get_sentiment_series(
    range: str = Query("Last 7 Days"),
    granularity: str = Query("day"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sentiment time series data"""
    data_service = DataService(db)
    series_data = await data_service.get_sentiment_series(range, granularity, start_date, end_date)

    return SentimentSeriesResponse(success=True, data=series_data)


@router.get("/sentiment/categories", response_model=OverviewResponse)
async def get_sentiment_categories(
    range: str = Query("Last 7 Days"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sentiment breakdown by categories"""
    data_service = DataService(db)
    categories_data = await data_service.get_sentiment_categories(range, start_date, end_date)

    return OverviewResponse(success=True, data=categories_data)


@router.get("/hashtags/trending", response_model=TrendingHashtagsResponse)
async def get_trending_hashtags(
    limit: int = Query(20, ge=1, le=100),
    min_mentions: int = Query(100, ge=0),
    range: str = Query("Last 7 Days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trending hashtags"""
    data_service = DataService(db)
    hashtags = await data_service.get_trending_hashtags(limit, min_mentions, range)

    return TrendingHashtagsResponse(success=True, data=hashtags)


@router.get("/hashtags/{tag}", response_model=OverviewResponse)
async def get_hashtag_details(
    tag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed hashtag analysis"""
    data_service = DataService(db)
    hashtag_data = await data_service.get_hashtag_details(tag)

    if not hashtag_data:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    return OverviewResponse(success=True, data=hashtag_data)


@router.get("/keywords/trends", response_model=KeywordTrendsResponse)
async def get_keyword_trends(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    range: str = Query("Last 7 Days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get keyword trends and analysis"""
    data_service = DataService(db)
    keywords = await data_service.get_keyword_trends(limit, category, range)

    return KeywordTrendsResponse(success=True, data=keywords)


@router.get("/influencers", response_model=InfluencersResponse)
async def get_influencers(
    limit: int = Query(20, ge=1, le=100),
    min_followers: int = Query(100000, ge=0),
    verified_only: bool = Query(False),
    range: str = Query("Last 7 Days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get influential accounts and their metrics"""
    data_service = DataService(db)
    influencers = await data_service.get_influencers(limit, min_followers, verified_only, range)

    return InfluencersResponse(success=True, data=influencers)


@router.get("/accounts/{handle}/analysis", response_model=OverviewResponse)
async def get_account_analysis(
    handle: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed account analysis"""
    data_service = DataService(db)
    account_data = await data_service.get_account_analysis(handle)

    if not account_data:
        raise HTTPException(status_code=404, detail="Account not found")

    return OverviewResponse(success=True, data=account_data)


@router.get("/geographic/states", response_model=GeographicStatesResponse)
async def get_geographic_states(
    range: str = Query("Last 7 Days"),
    keyword: Optional[str] = None,
    hashtag: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get geographic distribution data for Nigeria states"""
    data_service = DataService(db)
    states = await data_service.get_geographic_states(range, keyword, hashtag)

    return GeographicStatesResponse(success=True, data=states)


@router.get("/geographic/coordinates", response_model=OverviewResponse)
async def get_geographic_coordinates(
    range: str = Query("Last 7 Days"),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get geographic data with coordinates for mapping"""
    data_service = DataService(db)
    geo_data = await data_service.get_geographic_coordinates(range, keyword)

    return OverviewResponse(success=True, data=geo_data)


@router.get("/posts/top", response_model=TopPostsResponse)
async def get_top_posts(
    limit: int = Query(20, ge=1, le=100),
    range: str = Query("Last 7 Days"),
    keyword: Optional[str] = None,
    hashtag: Optional[str] = None,
    min_engagement: int = Query(100, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top performing posts"""
    data_service = DataService(db)
    posts = await data_service.get_top_posts(limit, range, keyword, hashtag, min_engagement)

    return TopPostsResponse(success=True, data=posts)


@router.post("/posts/search", response_model=SearchPostsResponse)
async def search_posts(
    request: SearchPostsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search posts by content, keywords, or hashtags"""
    data_service = DataService(db)
    search_results = await data_service.search_posts(
        request.q, request.range, request.limit, request.offset,
        request.sentiment, request.language
    )

    return SearchPostsResponse(success=True, data=search_results)


@router.get("/anomalies", response_model=AnomaliesResponse)
async def get_anomalies(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    range: str = Query("Last 7 Days"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detected anomalies and alerts"""
    data_service = DataService(db)
    anomalies = await data_service.get_anomalies(severity, status, range, limit)

    return AnomaliesResponse(success=True, data=anomalies)


@router.get("/anomalies/{id}", response_model=AnomalyDetailResponse)
async def get_anomaly_detail(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed anomaly information"""
    result = await db.execute(select(Anomaly).where(Anomaly.id == id))
    anomaly = result.scalar_one_or_none()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    return AnomalyDetailResponse(
        success=True,
        data={
            "id": anomaly.id,
            "title": anomaly.title,
            "severity": anomaly.severity,
            "detected_at": anomaly.detected_at,
            "summary": anomaly.summary,
            "metric": anomaly.metric,
            "delta": anomaly.delta,
            "status": anomaly.status,
            "affected_keywords": anomaly.affected_keywords or [],
            "timeline": anomaly.timeline or [],
            "related_posts": anomaly.related_posts or [],
            "recommendations": anomaly.recommendations or []
        }
    )
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database import get_db
from app.config import settings
from app.schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest,
    UserResponse, BaseResponse
)
from app.models import User
from sqlalchemy import select
import uuid

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """User authentication and login"""
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return LoginResponse(
        success=True,
        data={
            "token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "permissions": user.permissions or []
            }
        }
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh expired JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token"
    )
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    access_token = create_access_token(data={"sub": user.id})

    return LoginResponse(
        success=True,
        data={
            "token": access_token
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        permissions=current_user.permissions or []
    )


@router.post("/register", response_model=LoginResponse)
async def register(
    username: str,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user (for testing purposes)"""
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.username == username) | (User.email == email)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role="user",
        permissions=["read"],
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.id})

    return LoginResponse(
        success=True,
        data={
            "token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
                "permissions": new_user.permissions or []
            }
        }
    )
