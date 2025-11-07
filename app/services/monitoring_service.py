"""
Data Source Monitoring Service
Tracks health and performance of all data sources
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models.social_media_sources import DataSourceMonitoring

logger = logging.getLogger(__name__)


class MonitoringService:
    """
    Service for monitoring data source health and performance
    """

    def __init__(self, db: AsyncSession):
        """Initialize monitoring service"""
        self.db = db

    async def record_fetch_attempt(
        self,
        source_type: str,
        source_name: str,
        success: bool,
        items_collected: int = 0,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Record a data fetch attempt

        Args:
            source_type: Type of source (google_trends, tiktok, facebook, apify)
            source_name: Specific source name (hashtag, page, etc.)
            success: Whether fetch was successful
            items_collected: Number of items collected
            error_message: Error message if failed

        Returns:
            True if recorded successfully
        """
        try:
            # Get or create monitoring record
            result = await self.db.execute(
                select(DataSourceMonitoring)
                .where(and_(
                    DataSourceMonitoring.source_type == source_type,
                    DataSourceMonitoring.source_name == source_name
                ))
            )
            monitor = result.scalar_one_or_none()

            now = datetime.utcnow()

            if not monitor:
                # Create new monitoring record
                monitor = DataSourceMonitoring(
                    source_type=source_type,
                    source_name=source_name,
                    status="active" if success else "failed",
                    last_successful_fetch=now if success else None,
                    last_attempt=now,
                    total_items_collected=items_collected,
                    items_collected_today=items_collected,
                    consecutive_failures=0 if success else 1,
                    last_error=error_message if not success else None,
                    error_count=0 if success else 1,
                    collection_frequency=3600,  # Default 1 hour
                    priority=1
                )
                self.db.add(monitor)
            else:
                # Update existing record
                if success:
                    monitor.status = "active"
                    monitor.last_successful_fetch = now
                    monitor.total_items_collected += items_collected
                    monitor.items_collected_today += items_collected
                    monitor.consecutive_failures = 0
                else:
                    monitor.status = "failed"
                    monitor.consecutive_failures += 1
                    monitor.last_error = error_message
                    monitor.error_count += 1

                    # Update status based on consecutive failures
                    if monitor.consecutive_failures >= 5:
                        monitor.status = "degraded"

                monitor.last_attempt = now
                monitor.updated_at = now

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error recording fetch attempt: {e}")
            await self.db.rollback()
            return False

    async def get_source_status(
        self,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get status of all data sources

        Args:
            source_type: Filter by source type (optional)

        Returns:
            List of source status information
        """
        try:
            query = select(DataSourceMonitoring)

            if source_type:
                query = query.where(DataSourceMonitoring.source_type == source_type)

            result = await self.db.execute(query.order_by(DataSourceMonitoring.priority))

            statuses = []
            for monitor in result.scalars():
                statuses.append({
                    "source_type": monitor.source_type,
                    "source_name": monitor.source_name,
                    "status": monitor.status,
                    "last_successful_fetch": monitor.last_successful_fetch.isoformat() if monitor.last_successful_fetch else None,
                    "last_attempt": monitor.last_attempt.isoformat() if monitor.last_attempt else None,
                    "total_items_collected": monitor.total_items_collected,
                    "items_collected_today": monitor.items_collected_today,
                    "consecutive_failures": monitor.consecutive_failures,
                    "error_count": monitor.error_count,
                    "last_error": monitor.last_error,
                    "collection_frequency": monitor.collection_frequency,
                    "priority": monitor.priority
                })

            return statuses

        except Exception as e:
            logger.error(f"Error getting source status: {e}")
            return []

    async def get_health_summary(self) -> Dict[str, Any]:
        """
        Get overall health summary of all data sources

        Returns:
            Health summary
        """
        try:
            result = await self.db.execute(
                select(DataSourceMonitoring)
            )

            sources = result.scalars().all()

            if not sources:
                return {
                    "overall_status": "unknown",
                    "total_sources": 0,
                    "active_sources": 0,
                    "failed_sources": 0,
                    "degraded_sources": 0
                }

            active = sum(1 for s in sources if s.status == "active")
            failed = sum(1 for s in sources if s.status == "failed")
            degraded = sum(1 for s in sources if s.status == "degraded")
            rate_limited = sum(1 for s in sources if s.status == "rate_limited")

            # Determine overall status
            if failed + degraded == 0:
                overall_status = "healthy"
            elif failed + degraded <= len(sources) * 0.3:
                overall_status = "warning"
            else:
                overall_status = "critical"

            return {
                "overall_status": overall_status,
                "total_sources": len(sources),
                "active_sources": active,
                "failed_sources": failed,
                "degraded_sources": degraded,
                "rate_limited_sources": rate_limited,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting health summary: {e}")
            return {"error": str(e)}

    async def reset_daily_counters(self) -> bool:
        """
        Reset daily counters (should be run daily)

        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(DataSourceMonitoring)
                .values(items_collected_today=0)
            )

            await self.db.commit()
            logger.info("Reset daily counters for all sources")
            return True

        except Exception as e:
            logger.error(f"Error resetting daily counters: {e}")
            await self.db.rollback()
            return False

    async def update_rate_limit_info(
        self,
        source_type: str,
        source_name: str,
        rate_limit_reset: datetime,
        requests_remaining: int
    ) -> bool:
        """
        Update rate limit information for a source

        Args:
            source_type: Type of source
            source_name: Source name
            rate_limit_reset: When rate limit resets
            requests_remaining: Number of requests remaining

        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(DataSourceMonitoring)
                .where(and_(
                    DataSourceMonitoring.source_type == source_type,
                    DataSourceMonitoring.source_name == source_name
                ))
                .values(
                    rate_limit_reset=rate_limit_reset,
                    requests_remaining=requests_remaining,
                    status="rate_limited" if requests_remaining == 0 else "active"
                )
            )

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error updating rate limit info: {e}")
            await self.db.rollback()
            return False

    async def get_sources_due_for_collection(self) -> List[Dict[str, Any]]:
        """
        Get sources that are due for data collection

        Returns:
            List of sources due for collection
        """
        try:
            now = datetime.utcnow()

            result = await self.db.execute(
                select(DataSourceMonitoring)
                .where(DataSourceMonitoring.status.in_(["active", "degraded"]))
                .order_by(DataSourceMonitoring.priority)
            )

            due_sources = []
            for monitor in result.scalars():
                # Check if collection is due
                if monitor.last_successful_fetch:
                    next_collection = monitor.last_successful_fetch + timedelta(
                        seconds=monitor.collection_frequency
                    )
                    if now >= next_collection:
                        due_sources.append({
                            "source_type": monitor.source_type,
                            "source_name": monitor.source_name,
                            "priority": monitor.priority,
                            "collection_frequency": monitor.collection_frequency
                        })
                else:
                    # Never collected, add to list
                    due_sources.append({
                        "source_type": monitor.source_type,
                        "source_name": monitor.source_name,
                        "priority": monitor.priority,
                        "collection_frequency": monitor.collection_frequency
                    })

            return due_sources

        except Exception as e:
            logger.error(f"Error getting sources due for collection: {e}")
            return []


def get_monitoring_service(db: AsyncSession) -> MonitoringService:
    """Get monitoring service instance"""
    return MonitoringService(db)
