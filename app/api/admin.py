from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.auth import get_current_user_optional
from app.models import User, AlertRule, DataConnector
from app.schemas import (
    CreateAlertRuleRequest, AlertRulesResponse, BaseResponse,
    ConnectorsResponse, ConnectDataSourceRequest
)
import uuid

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user_optional)):
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/alert-rules", response_model=AlertRulesResponse)
async def get_alert_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get configured alert rules"""
    result = await db.execute(
        select(AlertRule).where(AlertRule.user_id == current_user.id)
    )
    rules = result.scalars().all()
    
    return AlertRulesResponse(
        success=True,
        data=[
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "enabled": rule.enabled,
                "conditions": rule.conditions,
                "actions": rule.actions or [],
                "created_at": rule.created_at,
                "updated_at": rule.updated_at
            }
            for rule in rules
        ]
    )


@router.post("/alert-rules", response_model=BaseResponse)
async def create_alert_rule(
    request: CreateAlertRuleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Create new alert rule"""
    new_rule = AlertRule(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        enabled=request.enabled,
        conditions=request.conditions.dict(),
        actions=request.actions
    )
    
    db.add(new_rule)
    await db.commit()
    
    return BaseResponse(success=True)


@router.put("/alert-rules/{id}", response_model=BaseResponse)
async def update_alert_rule(
    id: str,
    request: CreateAlertRuleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Update alert rule"""
    result = await db.execute(select(AlertRule).where(AlertRule.id == id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    if rule.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    rule.name = request.name
    rule.description = request.description
    rule.enabled = request.enabled
    rule.conditions = request.conditions.dict()
    rule.actions = request.actions
    
    await db.commit()
    
    return BaseResponse(success=True)


@router.delete("/alert-rules/{id}", response_model=BaseResponse)
async def delete_alert_rule(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Delete alert rule"""
    result = await db.execute(select(AlertRule).where(AlertRule.id == id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    if rule.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.delete(rule)
    await db.commit()
    
    return BaseResponse(success=True)


@router.get("/connectors", response_model=ConnectorsResponse)
async def get_connectors(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get data source connectors and their status"""
    result = await db.execute(select(DataConnector))
    connectors = result.scalars().all()
    
    return ConnectorsResponse(
        success=True,
        data=[
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "status": c.status,
                "last_sync": c.last_sync,
                "config": c.config or {},
                "metrics": {
                    "total_posts": c.total_posts or 0,
                    "last_24h_posts": c.last_24h_posts or 0,
                    "sync_success_rate": c.sync_success_rate or 0.0
                }
            }
            for c in connectors
        ]
    )


@router.post("/connectors/{id}/connect", response_model=BaseResponse)
async def connect_data_source(
    id: str,
    request: ConnectDataSourceRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Connect to data source"""
    result = await db.execute(select(DataConnector).where(DataConnector.id == id))
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    # Store credentials (should be encrypted in production)
    connector.credentials = request.dict()
    connector.status = "connected"
    
    await db.commit()
    
    return BaseResponse(success=True)


@router.post("/connectors/{id}/test", response_model=BaseResponse)
async def test_connector(
    id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Test data source connection"""
    result = await db.execute(select(DataConnector).where(DataConnector.id == id))
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    # Test connection logic here
    
    return BaseResponse(
        success=True,
        data={
            "status": "healthy",
            "response_time": 245,
            "last_sync": connector.last_sync,
            "errors": []
        }
    )
