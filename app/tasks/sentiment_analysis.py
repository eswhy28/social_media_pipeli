from app.celery_app import celery_app
from app.services.ai_service import AIService
from app.database import AsyncSessionLocal
from app.models import SocialPost, SentimentTimeSeries
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, case
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.sentiment_analysis.analyze_recent_posts")
async def analyze_recent_posts():
    """Analyze sentiment of recent posts using TextBlob"""
    logger.info("Starting sentiment analysis...")

    try:
        data_service = DataService()
        ai_service = AIService()

        # Fetch recent tweets (last 24 hours)
        recent_tweets = await data_service.fetch_recent_tweets(
            query="your_search_query",
            max_results=10  # Limit for free tier
        )

        analyzed_posts = 0
        for tweet in recent_tweets:
            sentiment_result = await ai_service.analyze_sentiment(tweet['text'])
            
            # TODO: Store sentiment results in database
            # For POC, just log the results
            logger.info(f"Sentiment for tweet {tweet['id']}: {sentiment_result['label']}")
            analyzed_posts += 1

        logger.info("Sentiment analysis completed successfully")
        return {"status": "success", "posts_analyzed": analyzed_posts}
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.sentiment_analysis.aggregate_sentiment_timeseries")
def aggregate_sentiment_timeseries(granularity: str = "hour"):
    """
    Aggregate sentiment data into time series
    Runs periodically to update sentiment trends
    """
    logger.info(f"Aggregating sentiment timeseries with {granularity} granularity")

    import asyncio

    async def run_task():
        async with AsyncSessionLocal() as db:
            try:
                # Determine time window based on granularity
                now = datetime.utcnow()

                if granularity == "hour":
                    timestamp = now.replace(minute=0, second=0, microsecond=0)
                    start = timestamp
                    end = timestamp + timedelta(hours=1)
                elif granularity == "day":
                    timestamp = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    start = timestamp
                    end = timestamp + timedelta(days=1)
                else:
                    timestamp = now.replace(minute=0, second=0, microsecond=0)
                    start = timestamp
                    end = timestamp + timedelta(hours=1)

                # Query posts in the time window
                result = await db.execute(
                    select(
                        func.count(SocialPost.id).label('total'),
                        func.sum(case((SocialPost.sentiment == 'positive', 1), else_=0)).label('positive'),
                        func.sum(case((SocialPost.sentiment == 'negative', 1), else_=0)).label('negative'),
                        func.sum(case((SocialPost.sentiment == 'neutral', 1), else_=0)).label('neutral'),
                        func.avg(SocialPost.sentiment_score).label('avg_score'),
                        func.sum(SocialPost.engagement_total).label('total_engagement')
                    ).where(
                        and_(
                            SocialPost.posted_at >= start,
                            SocialPost.posted_at < end
                        )
                    )
                )

                # Re-run query with proper case statement
                result = await db.execute(
                    select(
                        func.count(SocialPost.id).label('total'),
                        func.sum(SocialPost.engagement_total).label('total_engagement'),
                        func.avg(SocialPost.sentiment_score).label('avg_score')
                    ).where(
                        and_(
                            SocialPost.posted_at >= start,
                            SocialPost.posted_at < end
                        )
                    )
                )
                stats = result.one()

                # Get sentiment counts separately
                sentiment_counts = {}
                for sentiment_type in ['positive', 'negative', 'neutral']:
                    result = await db.execute(
                        select(func.count(SocialPost.id)).where(
                            and_(
                                SocialPost.posted_at >= start,
                                SocialPost.posted_at < end,
                                SocialPost.sentiment == sentiment_type
                            )
                        )
                    )
                    sentiment_counts[sentiment_type] = result.scalar() or 0

                total_count = stats.total or 0

                if total_count > 0:
                    # Check if record exists
                    existing = await db.execute(
                        select(SentimentTimeSeries).where(
                            and_(
                                SentimentTimeSeries.timestamp == timestamp,
                                SentimentTimeSeries.granularity == granularity
                            )
                        )
                    )
                    record = existing.scalar_one_or_none()

                    avg_engagement = (stats.total_engagement or 0) / total_count if total_count > 0 else 0

                    if record:
                        # Update existing record
                        record.positive_count = sentiment_counts['positive']
                        record.negative_count = sentiment_counts['negative']
                        record.neutral_count = sentiment_counts['neutral']
                        record.total_count = total_count
                        record.avg_sentiment_score = float(stats.avg_score or 0)
                        record.total_engagement = stats.total_engagement or 0
                        record.avg_engagement = avg_engagement
                    else:
                        # Create new record
                        record = SentimentTimeSeries(
                            timestamp=timestamp,
                            positive_count=sentiment_counts['positive'],
                            negative_count=sentiment_counts['negative'],
                            neutral_count=sentiment_counts['neutral'],
                            total_count=total_count,
                            avg_sentiment_score=float(stats.avg_score or 0),
                            total_engagement=stats.total_engagement or 0,
                            avg_engagement=avg_engagement,
                            granularity=granularity
                        )
                        db.add(record)

                    await db.commit()

                    logger.info(f"Aggregated {total_count} posts into timeseries")

                    return {
                        "status": "success",
                        "timestamp": timestamp.isoformat(),
                        "granularity": granularity,
                        "posts_aggregated": total_count
                    }
                else:
                    logger.info("No posts to aggregate in this time window")
                    return {
                        "status": "success",
                        "posts_aggregated": 0
                    }

            except Exception as e:
                await db.rollback()
                logger.error(f"Error aggregating sentiment: {str(e)}")
                return {"status": "error", "error": str(e)}

    return asyncio.run(run_task())


@celery_app.task(name="app.tasks.sentiment_analysis.detect_sentiment_anomalies")
def detect_sentiment_anomalies():
    """
    Detect anomalies in sentiment patterns
    Uses statistical methods to identify unusual spikes or drops
    """
    logger.info("Detecting sentiment anomalies")

    import asyncio
    from app.models import AnomalyDetection

    async def run_task():
        async with AsyncSessionLocal() as db:
            try:
                ai_service = AIService()

                # Get recent sentiment time series (last 24 hours)
                end = datetime.utcnow()
                start = end - timedelta(hours=24)

                result = await db.execute(
                    select(SentimentTimeSeries).where(
                        and_(
                            SentimentTimeSeries.timestamp >= start,
                            SentimentTimeSeries.granularity == "hour"
                        )
                    ).order_by(SentimentTimeSeries.timestamp)
                )

                series = result.scalars().all()

                if len(series) < 3:
                    logger.info("Not enough data for anomaly detection")
                    return {"status": "success", "anomalies_detected": 0}

                # Prepare data for anomaly detection
                time_series_data = [
                    {
                        "timestamp": s.timestamp.isoformat(),
                        "value": s.avg_sentiment_score
                    }
                    for s in series
                ]

                # Detect anomalies
                anomalies = await ai_service.detect_anomalies(time_series_data, threshold=2.0)

                # Store anomalies in database
                for anomaly in anomalies:
                    anomaly_record = AnomalyDetection(
                        detected_at=datetime.fromisoformat(anomaly['timestamp']),
                        anomaly_type='sentiment_spike',
                        severity=anomaly['severity'],
                        metric_name='avg_sentiment_score',
                        expected_value=anomaly['expected_value'],
                        actual_value=anomaly['value'],
                        deviation_score=anomaly['z_score'],
                        description=anomaly['description'],
                        status='new'
                    )
                    db.add(anomaly_record)

                await db.commit()

                logger.info(f"Detected {len(anomalies)} anomalies")

                return {
                    "status": "success",
                    "anomalies_detected": len(anomalies),
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                await db.rollback()
                logger.error(f"Error detecting anomalies: {str(e)}")
                return {"status": "error", "error": str(e)}

    return asyncio.run(run_task())
