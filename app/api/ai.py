from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.auth import get_current_user_optional
from app.models import (
    User, SocialPost, SentimentAnalysis, LocationExtraction, 
    EntityExtraction, AIAnalysisSession
)
from app.schemas import AIGenerateRequest, AIGenerateResponse
from pydantic import BaseModel
from app.services.ai_service import AIService
from app.services.enhanced_ai_service import enhanced_ai_service
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

router = APIRouter()

class BaseResponse(BaseModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TextAnalysisRequest(BaseModel):
    text: str


@router.post("/generate/summary", response_model=AIGenerateResponse)
async def generate_summary(
    request: AIGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Generate AI summary for report sections"""
    ai_service = AIService()
    
    summary = await ai_service.generate_summary(
        section=request.section,
        subject=request.subject,
        template=request.template,
        range=request.range,
        context=request.context
    )
    
    return AIGenerateResponse(success=True, data=summary)


@router.post("/generate/insights", response_model=AIGenerateResponse)
async def generate_insights(
    request: AIGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Generate detailed AI insights for report sections"""
    ai_service = AIService()
    
    insights = await ai_service.generate_insights(
        section=request.section,
        subject=request.subject,
        template=request.template,
        range=request.range,
        context=request.context
    )
    
    return AIGenerateResponse(success=True, data=insights)


from pydantic import BaseModel

class TextAnalysisRequest(BaseModel):
    text: str

@router.post("/analyze/sentiment", response_model=BaseResponse)
async def analyze_sentiment_advanced(
    request: TextAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Analyze sentiment using advanced Hugging Face models"""
    try:
        result = await enhanced_ai_service.analyze_sentiment_advanced(request.text)
        return BaseResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/locations", response_model=BaseResponse)
async def extract_locations(
    request: TextAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Extract location entities from text using NER models"""
    try:
        locations = await enhanced_ai_service.extract_locations(request.text)
        return BaseResponse(success=True, data={"locations": locations})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/comprehensive", response_model=BaseResponse)
async def comprehensive_analysis(
    request: TextAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Comprehensive text analysis including sentiment, locations, and entities"""
    try:
        analysis = await enhanced_ai_service.analyze_text_comprehensive(request.text)
        return BaseResponse(success=True, data=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/post/{post_id}", response_model=BaseResponse)
async def analyze_post_advanced(
    post_id: str,
    save_to_db: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Analyze a specific post with advanced AI models and optionally save results"""
    try:
        # Get the post
        result = await db.execute(select(SocialPost).where(SocialPost.id == post_id))
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Perform comprehensive analysis
        analysis = await enhanced_ai_service.analyze_text_comprehensive(post.text)
        
        if save_to_db:
            # Create analysis session
            session_id = str(uuid.uuid4())
            analysis_session = AIAnalysisSession(
                id=session_id,
                post_id=post_id,
                session_type="comprehensive",
                status="processing",
                models_used=analysis.get("models_used", {}),
                started_at=datetime.utcnow()
            )
            db.add(analysis_session)
            
            # Save sentiment analysis
            sentiment = analysis.get("sentiment", {})
            if sentiment:
                sentiment_record = SentimentAnalysis(
                    post_id=post_id,
                    label=sentiment.get("label", "neutral"),
                    score=sentiment.get("score", 0.0),
                    confidence=sentiment.get("confidence", 0.0),
                    model_name=sentiment.get("model", "unknown"),
                    all_scores=sentiment.get("all_scores", {}),
                    text_length=len(post.text),
                    processing_time_ms=sentiment.get("processing_time_ms", 0)
                )
                db.add(sentiment_record)
            
            # Save location extractions
            locations = analysis.get("locations", [])
            for location in locations:
                location_record = LocationExtraction(
                    post_id=post_id,
                    location_text=location.get("text", ""),
                    location_type=location.get("label", ""),
                    confidence=location.get("confidence", 0.0),
                    start_position=location.get("start", 0),
                    end_position=location.get("end", 0),
                    model_name=location.get("source", "unknown")
                )
                db.add(location_record)
            
            # Save entity extractions
            entities = analysis.get("entities", [])
            for entity in entities:
                entity_record = EntityExtraction(
                    post_id=post_id,
                    entity_text=entity.get("text", ""),
                    entity_type=entity.get("label", ""),
                    confidence=entity.get("confidence", 0.0),
                    start_position=entity.get("start", 0),
                    end_position=entity.get("end", 0),
                    model_name=entity.get("source", "unknown")
                )
                db.add(entity_record)
            
            # Update analysis session
            analysis_session.status = "completed"
            analysis_session.sentiment_result = sentiment
            analysis_session.locations_found = len(locations)
            analysis_session.entities_found = len(entities)
            analysis_session.keywords_found = len(analysis.get("keywords", []))
            analysis_session.completed_at = datetime.utcnow()
            
            await db.commit()
            
            analysis["analysis_session_id"] = session_id
        
        return BaseResponse(success=True, data=analysis)
        
    except Exception as e:
        if save_to_db:
            await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/info", response_model=BaseResponse)
async def get_model_info(
    current_user: User = Depends(get_current_user_optional)
):
    """Get information about loaded AI models"""
    try:
        model_info = await enhanced_ai_service.get_model_info()
        return BaseResponse(success=True, data=model_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/post/{post_id}", response_model=BaseResponse)
async def get_post_analysis(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get saved AI analysis results for a specific post"""
    try:
        # Get sentiment analysis
        sentiment_result = await db.execute(
            select(SentimentAnalysis).where(SentimentAnalysis.post_id == post_id)
        )
        sentiment_records = sentiment_result.scalars().all()
        
        # Get location extractions
        location_result = await db.execute(
            select(LocationExtraction).where(LocationExtraction.post_id == post_id)
        )
        location_records = location_result.scalars().all()
        
        # Get entity extractions
        entity_result = await db.execute(
            select(EntityExtraction).where(EntityExtraction.post_id == post_id)
        )
        entity_records = entity_result.scalars().all()
        
        # Get analysis sessions
        session_result = await db.execute(
            select(AIAnalysisSession).where(AIAnalysisSession.post_id == post_id)
        )
        session_records = session_result.scalars().all()
        
        data = {
            "post_id": post_id,
            "sentiment_analyses": [
                {
                    "label": s.label,
                    "score": s.score,
                    "confidence": s.confidence,
                    "model_name": s.model_name,
                    "all_scores": s.all_scores,
                    "created_at": s.created_at.isoformat()
                } for s in sentiment_records
            ],
            "locations": [
                {
                    "text": l.location_text,
                    "type": l.location_type,
                    "confidence": l.confidence,
                    "model_name": l.model_name,
                    "country": l.country,
                    "state_province": l.state_province,
                    "city": l.city,
                    "created_at": l.created_at.isoformat()
                } for l in location_records
            ],
            "entities": [
                {
                    "text": e.entity_text,
                    "type": e.entity_type,
                    "confidence": e.confidence,
                    "model_name": e.model_name,
                    "created_at": e.created_at.isoformat()
                } for e in entity_records
            ],
            "analysis_sessions": [
                {
                    "id": s.id,
                    "session_type": s.session_type,
                    "status": s.status,
                    "models_used": s.models_used,
                    "sentiment_result": s.sentiment_result,
                    "locations_found": s.locations_found,
                    "entities_found": s.entities_found,
                    "keywords_found": s.keywords_found,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None
                } for s in session_records
            ]
        }
        
        return BaseResponse(success=True, data=data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/analyze", response_model=BaseResponse)
async def batch_analyze_posts(
    post_ids: List[str],
    save_to_db: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Batch analyze multiple posts with advanced AI models"""
    try:
        if len(post_ids) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 50 posts per batch")
        
        # Get posts
        result = await db.execute(
            select(SocialPost).where(SocialPost.id.in_(post_ids))
        )
        posts = result.scalars().all()
        
        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")
        
        # Prepare data for batch analysis
        post_data = [
            {
                "id": post.id,
                "text": post.text,
                "platform": post.platform,
                "posted_at": post.posted_at.isoformat() if post.posted_at else None
            }
            for post in posts
        ]
        
        # Perform batch analysis
        results = await enhanced_ai_service.batch_analyze_posts(post_data)
        
        return BaseResponse(
            success=True, 
            data={
                "analyzed_posts": len(results),
                "results": results
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))