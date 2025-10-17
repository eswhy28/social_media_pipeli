from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User
from app.schemas import AIGenerateRequest, AIGenerateResponse
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/generate/summary", response_model=AIGenerateResponse)
async def generate_summary(
    request: AIGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
