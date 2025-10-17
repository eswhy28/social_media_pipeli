from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import BaseResponse
import hmac
import hashlib
from app.config import settings

router = APIRouter()


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


@router.post("/alerts")
async def receive_alert_webhook(
    event: str,
    data: dict,
    x_webhook_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Receive real-time alert notifications"""
    # Verify signature in production
    # if not verify_webhook_signature(payload, x_webhook_signature):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook event
    # This could trigger notifications, logging, etc.
    
    return BaseResponse(success=True)
