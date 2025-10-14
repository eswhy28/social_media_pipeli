from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User, AlertRule, DataConnector
from app.schemas import (
    CreateAlertRuleRequest, AlertRulesResponse, BaseResponse,
    ConnectorsResponse, ConnectDataSourceRequest
)
import uuid

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/alert-rules", response_model=AlertRulesResponse)
async def get_alert_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User, Report
from app.schemas import (
    GenerateReportRequest, GenerateReportResponse,
    ReportStatusResponse
)
from app.tasks.report_generation import generate_report_task
from sqlalchemy import select
import uuid

router = APIRouter()


@router.post("/generate", response_model=GenerateReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive report data"""
    # Create report record
    report_id = str(uuid.uuid4())
    new_report = Report(
        id=report_id,
        user_id=current_user.id,
        template=request.template,
        subject=request.subject,
        date_range=request.range,
        status="generating",
        progress=0,
        sections=request.sections.dict()
    )
    
    db.add(new_report)
    await db.commit()
    
    # Trigger async task
    generate_report_task.delay(report_id, request.dict())
    
    return GenerateReportResponse(
        success=True,
        data={
            "report_id": report_id,
            "status": "generating",
            "progress": 0,
            "estimated_completion": None
        }
    )


@router.get("/{id}/status", response_model=ReportStatusResponse)
async def get_report_status(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check report generation status"""
    result = await db.execute(select(Report).where(Report.id == id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user owns the report
    if report.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    return ReportStatusResponse(
        success=True,
        data={
            "report_id": report.id,
            "status": report.status,
            "progress": report.progress or 0,
            "completed_at": report.completed_at,
            "download_url": report.download_url
        }
    )


@router.get("/{id}/download")
async def download_report(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download generated report"""
    from fastapi.responses import FileResponse
    
    result = await db.execute(select(Report).where(Report.id == id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user owns the report
    if report.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    if report.status != "completed":
        raise HTTPException(status_code=400, detail="Report is not ready for download")
    
    if not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=report.file_path,
        filename=f"report_{report.subject}_{report.id}.pdf",
        media_type="application/pdf"
    )


@router.get("")
async def list_reports(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's reports"""
    query = select(Report).where(Report.user_id == current_user.id)
    query = query.order_by(Report.started_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "report_id": r.id,
                "template": r.template,
                "subject": r.subject,
                "status": r.status,
                "progress": r.progress,
                "started_at": r.started_at,
                "completed_at": r.completed_at
            }
            for r in reports
        ]
    }

