from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.auth import get_current_user_optional
from app.models import User, Report
from app.schemas import (
    GenerateReportRequest, GenerateReportResponse,
    ReportStatusResponse, BaseResponse 
)
import uuid
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/generate", response_model=GenerateReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Generate a new report"""
    # Create report record
    report = Report(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=f"{request.template.capitalize()} Report - {request.subject}",
        report_type=request.template,
        subject=request.subject,
        status="pending",
        progress=0,
        date_range=request.range,
        sections=request.sections.dict(),
        estimated_completion=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Queue background task to generate report
    # background_tasks.add_task(generate_report_task, report.id)

    return GenerateReportResponse(
        success=True,
        data={
            "report_id": report.id,
            "status": report.status,
            "progress": report.progress,
            "estimated_completion": report.estimated_completion
        }
    )


@router.get("/{report_id}/status", response_model=ReportStatusResponse)
async def get_report_status(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get report generation status"""
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportStatusResponse(
        success=True,
        data={
            "report_id": report.id,
            "status": report.status,
            "progress": report.progress,
            "estimated_completion": report.estimated_completion,
            "completed_at": report.completed_at,
            "download_url": report.download_url
        }
    )


@router.get("/", response_model=BaseResponse)
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """List user's reports"""
    result = await db.execute(
        select(Report).where(Report.user_id == current_user.id).order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()

    return BaseResponse(
        success=True,
        data=[
            {
                "id": r.id,
                "title": r.title,
                "status": r.status,
                "progress": r.progress,
                "created_at": r.created_at,
                "completed_at": r.completed_at
            }
            for r in reports
        ]
    )


@router.delete("/{report_id}", response_model=BaseResponse)
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Delete a report"""
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    await db.delete(report)
    await db.commit()

    return BaseResponse(success=True)
