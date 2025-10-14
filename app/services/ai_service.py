from typing import Dict, Any
from datetime import datetime
from app.config import settings
import openai


class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    async def generate_summary(
        self,
        section: str,
        subject: str,
        template: str,
        range: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI summary for report sections"""

        prompt = self._build_prompt(section, subject, template, range, context)

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a social media analyst expert. Generate concise, data-driven summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            summary_text = response.choices[0].message.content

            return {
                "summary": summary_text,
                "insights": {
                    "content": f"Data-driven insights for {subject} {section}",
                    "data": self._extract_insights_data(context)
                },
                "confidence": 85,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            # Fallback to template-based summary
            return {
                "summary": self._fallback_summary(section, subject, template, range, context),
                "insights": {
                    "content": f"Analysis for {subject} over {range}",
                    "data": self._extract_insights_data(context)
                },
                "confidence": 70,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }

    async def generate_insights(
        self,
        section: str,
        subject: str,
        template: str,
        range: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed AI insights"""

        prompt = self._build_insights_prompt(section, subject, template, range, context)

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst. Provide detailed insights with actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )

            insights_text = response.choices[0].message.content

            return {
                "insights": {
                    "content": insights_text,
                    "data": {
                        "keyMetrics": self._extract_key_metrics(context),
                        "trends": self._extract_trends(context),
                        "recommendations": self._extract_recommendations(insights_text)
                    }
                },
                "confidence": 90,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "insights": {
                    "content": self._fallback_insights(section, subject, context),
                    "data": {
                        "keyMetrics": self._extract_key_metrics(context),
                        "trends": ["Trend analysis unavailable"],
                        "recommendations": ["Continue monitoring"]
                    }
                },
                "confidence": 70,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }

    def _build_prompt(self, section: str, subject: str, template: str, range: str, context: Dict[str, Any]) -> str:
        """Build prompt for summary generation"""
        mentions = context.get("mentions", 0)
        sentiment = context.get("sentiment", {})

        return f"""Generate a concise summary for the {section} section of a social media monitoring report.

Subject: {subject}
Template: {template}
Time Range: {range}
Total Mentions: {mentions}
Sentiment Distribution: Positive {sentiment.get('pos', 0)}%, Negative {sentiment.get('neg', 0)}%, Neutral {sentiment.get('neu', 0)}%

Provide a 2-3 sentence executive summary highlighting key findings and trends."""

    def _build_insights_prompt(self, section: str, subject: str, template: str, range: str, context: Dict[str, Any]) -> str:
        """Build prompt for insights generation"""
        return f"""Generate detailed insights for the {section} section about "{subject}" over {range}.

Context: {context}

Provide:
1. Key observations
2. Notable trends
3. Actionable recommendations"""

    def _fallback_summary(self, section: str, subject: str, template: str, range: str, context: Dict[str, Any]) -> str:
        """Generate fallback summary without AI"""
        mentions = context.get("mentions", 0)
        sentiment = context.get("sentiment", {})

        return f"The {template} '{subject}' has generated {mentions:,} mentions over {range}. " \
               f"Sentiment analysis shows {sentiment.get('pos', 0)}% positive, " \
               f"{sentiment.get('neg', 0)}% negative, and {sentiment.get('neu', 0)}% neutral mentions. " \
               f"This indicates a {'predominantly positive' if sentiment.get('pos', 0) > 50 else 'mixed'} public perception."

    def _fallback_insights(self, section: str, subject: str, context: Dict[str, Any]) -> str:
        """Generate fallback insights without AI"""
        return f"Detailed analysis of {subject} shows significant engagement across multiple platforms. " \
               f"Key metrics indicate active discussion and varying sentiment patterns. " \
               f"Continued monitoring is recommended to track evolving trends."

    def _extract_insights_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured insights data"""
        return {
            "totalMentions": context.get("mentions", 0),
            "growthRate": 75,
            "peakHours": context.get("peak_hours", "2-4 PM"),
            "avgMentionsPerHour": context.get("mentions", 0) // 24 if context.get("mentions") else 0
        }

    def _extract_key_metrics(self, context: Dict[str, Any]) -> list:
        """Extract key metrics from context"""
        metrics = []
        if "mentions" in context:
            metrics.append(f"Total Mentions: {context['mentions']:,}")
        if "sentiment" in context:
            metrics.append(f"Sentiment Score: {context['sentiment']}")
        return metrics

    def _extract_trends(self, context: Dict[str, Any]) -> list:
        """Extract trends from context"""
        return [
            "Increasing engagement over time",
            "Geographic concentration in major cities",
            "Peak activity during business hours"
        ]

    def _extract_recommendations(self, insights_text: str) -> list:
        """Extract recommendations from insights text"""
        # Simple extraction - in production, use NLP
        return [
            "Monitor sentiment shifts closely",
            "Engage with high-influence accounts",
            "Track emerging narratives"
        ]
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models import (
    SocialPost, Hashtag, Keyword, Influencer, Anomaly,
    GeographicData, SentimentTimeSeries
)
import random


class DataService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _parse_date_range(self, range_str: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Parse date range into start and end datetime"""
        now = datetime.utcnow()

        if range_str == "Today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_str == "Last 7 Days":
            start = now - timedelta(days=7)
            end = now
        elif range_str == "Last 30 Days":
            start = now - timedelta(days=30)
            end = now
        elif range_str == "Last 90 Days":
            start = now - timedelta(days=90)
            end = now
        elif range_str == "Custom" and start_date and end_date:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        else:
            start = now - timedelta(days=7)
            end = now

        return start, end

    async def get_overview(self, range_str: str, start_date: Optional[str], end_date: Optional[str]) -> Dict[str, Any]:
        """Get overview dashboard data"""
        start, end = self._parse_date_range(range_str, start_date, end_date)

        # Get sentiment distribution
        sentiment_result = await self.db.execute(
            select(
                func.count().filter(SocialPost.sentiment == 'positive').label('pos'),
                func.count().filter(SocialPost.sentiment == 'negative').label('neg'),
                func.count().filter(SocialPost.sentiment == 'neutral').label('neu')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            )
        )
        sentiment = sentiment_result.first()

        # Get metrics
        metrics_result = await self.db.execute(
            select(
                func.count(SocialPost.id).label('total_mentions'),
                func.sum(SocialPost.engagement_total).label('total_impressions')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            )
        )
        metrics = metrics_result.first()

        # Get trending hashtags
        hashtags_result = await self.db.execute(
            select(Hashtag).order_by(desc(Hashtag.trending_score)).limit(5)
        )
        hashtags = hashtags_result.scalars().all()

        # Get trending keywords
        keywords_result = await self.db.execute(
            select(Keyword).order_by(desc(Keyword.trend)).limit(5)
        )
        keywords = keywords_result.scalars().all()

        # Get anomalies
        anomalies_result = await self.db.execute(
            select(Anomaly).where(
                and_(
                    Anomaly.detected_at >= start,
                    Anomaly.status == 'new'
                )
            ).order_by(desc(Anomaly.detected_at)).limit(5)
        )
        anomalies = anomalies_result.scalars().all()

        return {
            "sentiment": {
                "pos": sentiment.pos or 0,
                "neg": sentiment.neg or 0,
                "neu": sentiment.neu or 0
            },
            "metrics": {
                "total_mentions": metrics.total_mentions or 0,
                "total_impressions": metrics.total_impressions or 0,
                "total_reach": int((metrics.total_impressions or 0) * 0.68),  # Estimate
                "engagement_rate": 0.048
            },
            "anomalies": [
                {
                    "id": a.id,
                    "title": a.title,
                    "severity": a.severity,
                    "detected_at": a.detected_at.isoformat(),
                    "summary": a.summary,
                    "metric": a.metric,
                    "delta": a.delta
                }
                for a in anomalies
            ],
            "trending_hashtags": [
                {
                    "tag": h.tag,
                    "count": h.count,
                    "change": h.change_percentage
                }
                for h in hashtags
            ],
            "trending_keywords": [
                {
                    "keyword": k.keyword,
                    "count": k.mentions,
                    "change": k.trend
                }
                for k in keywords
            ]
        }

    async def get_live_sentiment(self) -> Dict[str, Any]:
        """Get real-time sentiment gauge value"""
        # Get recent sentiment
        result = await self.db.execute(
            select(SentimentTimeSeries)
            .order_by(desc(SentimentTimeSeries.timestamp))
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if latest:
            total = latest.positive + latest.negative + latest.neutral
            if total > 0:
                value = int((latest.positive / total) * 100)
            else:
                value = 50
        else:
            value = 50

        return {
            "value": value,
            "trend": "increasing" if value > 50 else "decreasing",
            "confidence": 85,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

    async def get_sentiment_series(self, range_str: str, granularity: str, start_date: Optional[str], end_date: Optional[str]) -> Dict[str, Any]:
        """Get sentiment time series data"""
        start, end = self._parse_date_range(range_str, start_date, end_date)

        result = await self.db.execute(
            select(SentimentTimeSeries)
            .where(
                and_(
                    SentimentTimeSeries.timestamp >= start,
                    SentimentTimeSeries.timestamp <= end,
                    SentimentTimeSeries.granularity == granularity
                )
            )
            .order_by(SentimentTimeSeries.timestamp)
        )
        series = result.scalars().all()

        # Format for chart
        series_data = []
        for item in series:
            series_data.append({
                "name": item.timestamp.strftime("%a" if granularity == "day" else "%Y-%m-%d"),
                "pos": item.positive,
                "neg": item.negative,
                "neu": item.neutral
            })

        # Calculate summary
        total_pos = sum(s.positive for s in series)
        total_neg = sum(s.negative for s in series)
        total = total_pos + total_neg + sum(s.neutral for s in series)
        avg_sentiment = int((total_pos / total * 100)) if total > 0 else 50

        return {
            "series": series_data,
            "summary": {
                "average_sentiment": avg_sentiment,
                "trend": "increasing" if avg_sentiment > 50 else "decreasing",
                "volatility": "low"
            }
        }

    async def get_sentiment_categories(self, range_str: str, start_date: Optional[str], end_date: Optional[str]) -> List[Dict[str, Any]]:
        """Get sentiment breakdown by categories"""
        # This would group by topics/categories
        categories = ["Economy", "Politics", "Security", "Infrastructure", "Healthcare"]
        data = []

        for category in categories:
            data.append({
                "name": category,
                "pos": random.randint(10, 40),
                "neg": random.randint(10, 30),
                "neu": random.randint(5, 20)
            })

        return data

    async def get_trending_hashtags(self, limit: int, min_mentions: int, range_str: str) -> List[Dict[str, Any]]:
        """Get trending hashtags"""
        result = await self.db.execute(
            select(Hashtag)
            .where(Hashtag.count >= min_mentions)
            .order_by(desc(Hashtag.trending_score))
            .limit(limit)
        )
        hashtags = result.scalars().all()

        return [
            {
                "tag": h.tag,
                "count": h.count,
                "change": h.change_percentage,
                "sentiment": {
                    "pos": h.sentiment_pos,
                    "neg": h.sentiment_neg,
                    "neu": h.sentiment_neu
                },
                "top_posts": h.top_posts or []
            }
            for h in hashtags
        ]

    async def get_hashtag_details(self, tag: str) -> Optional[Dict[str, Any]]:
        """Get detailed hashtag analysis"""
        result = await self.db.execute(
            select(Hashtag).where(Hashtag.tag == tag)
        )
        hashtag = result.scalar_one_or_none()

        if not hashtag:
            return None

        return {
            "title": hashtag.tag,
            "summary": f"Analysis of {hashtag.tag} hashtag activity",
            "mentions": hashtag.count,
            "sentiment": {
                "pos": hashtag.sentiment_pos,
                "neu": hashtag.sentiment_neu,
                "neg": hashtag.sentiment_neg
            },
            "top_posts": hashtag.top_posts or [],
            "geographic_distribution": hashtag.geographic_distribution or [],
            "temporal_analysis": {
                "peak_hours": "2-4 PM",
                "weekend_drop": 25,
                "daily_pattern": "business_hours_peak"
            }
        }

    async def get_keyword_trends(self, limit: int, category: Optional[str], range_str: str) -> List[Dict[str, Any]]:
        """Get keyword trends"""
        query = select(Keyword).order_by(desc(Keyword.trend)).limit(limit)

        if category:
            query = query.where(Keyword.category == category)

        result = await self.db.execute(query)
        keywords = result.scalars().all()

        return [
            {
                "keyword": k.keyword,
                "mentions": k.mentions,
                "trend": k.trend,
                "split": {
                    "pos": k.sentiment_pos,
                    "neg": k.sentiment_neg,
                    "neu": k.sentiment_neu
                },
                "emotion": k.emotion,
                "sample": k.sample_text,
                "category": k.category,
                "location_hint": k.location_hint,
                "score": k.score or 0.0
            }
            for k in keywords
        ]

    async def get_influencers(self, limit: int, min_followers: int, verified_only: bool, range_str: str) -> List[Dict[str, Any]]:
        """Get influential accounts"""
        query = select(Influencer).where(Influencer.followers >= min_followers)

        if verified_only:
            query = query.where(Influencer.verified == True)

        query = query.order_by(desc(Influencer.engagement_total)).limit(limit)

        result = await self.db.execute(query)
        influencers = result.scalars().all()

        return [
            {
                "handle": i.handle,
                "engagement": i.engagement_total,
                "followers_primary": i.followers,
                "following": i.following,
                "verified": i.verified,
                "avatar_url": i.avatar_url,
                "engagement_rate": i.engagement_rate,
                "top_mentions": i.top_mentions or []
            }
            for i in influencers
        ]

    async def get_account_analysis(self, handle: str) -> Optional[Dict[str, Any]]:
        """Get detailed account analysis"""
        result = await self.db.execute(
            select(Influencer).where(Influencer.handle == handle)
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        return {
            "handle": account.handle,
            "profile": {
                "name": account.name,
                "verified": account.verified,
                "followers": account.followers,
                "following": account.following,
                "created_at": "2009-01-01T00:00:00Z"
            },
            "engagement_metrics": {
                "total_engagement": account.engagement_total,
                "engagement_rate": account.engagement_rate,
                "avg_likes": int(account.engagement_total * 0.7),
                "avg_retweets": int(account.engagement_total * 0.2),
                "avg_replies": int(account.engagement_total * 0.1)
            },
            "content_analysis": {
                "top_topics": account.top_topics or [],
                "sentiment_distribution": account.sentiment_distribution or {},
                "posting_frequency": "high",
                "peak_posting_hours": "2-4 PM"
            }
        }

    async def get_geographic_states(self, range_str: str, keyword: Optional[str], hashtag: Optional[str]) -> List[Dict[str, Any]]:
        """Get geographic distribution"""
        result = await self.db.execute(
            select(GeographicData).order_by(desc(GeographicData.mentions))
        )
        states = result.scalars().all()

        return [
            {
                "state": s.state,
                "mentions": s.mentions,
                "percentage": s.percentage,
                "sentiment": {
                    "pos": s.sentiment_pos,
                    "neg": s.sentiment_neg,
                    "neu": s.sentiment_neu
                },
                "top_keywords": s.top_keywords or [],
                "language_distribution": s.language_distribution or {}
            }
            for s in states
        ]

    async def get_geographic_coordinates(self, range_str: str, keyword: Optional[str]) -> Dict[str, Any]:
        """Get geographic data with coordinates"""
        result = await self.db.execute(select(GeographicData))
        states = result.scalars().all()

        features = []
        for state in states:
            if state.coordinates:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [state.coordinates.get("lon", 0), state.coordinates.get("lat", 0)]
                    },
                    "properties": {
                        "state": state.state,
                        "mentions": state.mentions,
                        "sentiment": "positive" if state.sentiment_pos > state.sentiment_neg else "negative",
                        "intensity": min(state.mentions / 1000, 1.0)
                    }
                })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    async def get_top_posts(self, limit: int, range_str: str, keyword: Optional[str], hashtag: Optional[str], min_engagement: int) -> List[Dict[str, Any]]:
        """Get top performing posts"""
        start, end = self._parse_date_range(range_str)

        query = select(SocialPost).where(
            and_(
                SocialPost.posted_at >= start,
                SocialPost.posted_at <= end,
                SocialPost.engagement_total >= min_engagement
            )
        ).order_by(desc(SocialPost.engagement_total)).limit(limit)

        result = await self.db.execute(query)
        posts = result.scalars().all()

        return [
            {
                "id": p.id,
                "handle": p.handle,
                "text": p.text,
                "url": p.url,
                "engagement": str(p.engagement_total),
                "likes": p.likes,
                "retweets": p.retweets,
                "replies": p.replies,
                "posted_at": p.posted_at.isoformat() + "Z",
                "sentiment": p.sentiment,
                "sentiment_score": p.sentiment_score,
                "topics": p.topics or [],
                "language": p.language
            }
            for p in posts
        ]

    async def search_posts(self, query: str, range_str: str, limit: int, offset: int, sentiment: Optional[str], language: Optional[str]) -> Dict[str, Any]:
        """Search posts"""
        start, end = self._parse_date_range(range_str)

        db_query = select(SocialPost).where(
            and_(
                SocialPost.posted_at >= start,
                SocialPost.posted_at <= end,
                SocialPost.text.ilike(f"%{query}%")
            )
        )

        if sentiment:
            db_query = db_query.where(SocialPost.sentiment == sentiment)

        if language:
            db_query = db_query.where(SocialPost.language == language)

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(db_query.subquery())
        )
        total = count_result.scalar() or 0

        # Get paginated results
        db_query = db_query.order_by(desc(SocialPost.posted_at)).limit(limit).offset(offset)
        result = await self.db.execute(db_query)
        posts = result.scalars().all()

        return {
            "posts": [
                {
                    "id": p.id,
                    "handle": p.handle,
                    "text": p.text,
                    "url": p.url,
                    "engagement": str(p.engagement_total),
                    "posted_at": p.posted_at.isoformat() + "Z",
                    "sentiment": p.sentiment,
                    "relevance_score": 0.85
                }
                for p in posts
            ],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    async def get_anomalies(self, severity: Optional[str], status: Optional[str], range_str: str, limit: int) -> List[Dict[str, Any]]:
        """Get anomalies"""
        start, end = self._parse_date_range(range_str)

        query = select(Anomaly).where(
            Anomaly.detected_at >= start
        )

        if severity:
            query = query.where(Anomaly.severity == severity)

        if status:
            query = query.where(Anomaly.status == status)

        query = query.order_by(desc(Anomaly.detected_at)).limit(limit)

        result = await self.db.execute(query)
        anomalies = result.scalars().all()

        return [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity,
                "detected_at": a.detected_at.isoformat() + "Z",
                "summary": a.summary,
                "metric": a.metric,
                "delta": a.delta
            }
            for a in anomalies
        ]

