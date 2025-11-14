from typing import Dict, List, Any, Optional
import tweepy
from datetime import datetime, timedelta
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from app.models import SocialPost, SentimentTimeSeries, TrendingTopic, AnomalyDetection
from app.services.ai_service import AIService
from app.redis_client import get_redis
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class DataService:
    """Data service with Twitter API v2 integration and rate limiting"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()

        # Initialize Twitter client if token is available
        if settings.TWITTER_BEARER_TOKEN:
            self.twitter_client = tweepy.Client(
                bearer_token=settings.TWITTER_BEARER_TOKEN,
                wait_on_rate_limit=False  # Don't wait - fail fast instead
            )
        else:
            self.twitter_client = None
            logger.warning("Twitter API token not configured")

        self.rate_limit_window = 900  # 15 minutes in seconds
        self.max_requests_per_window = settings.TWITTER_SEARCH_REQUESTS_PER_15MIN

    async def fetch_recent_tweets(
        self,
        query: str,
        max_results: int = 10,
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent tweets using Twitter API v2 free tier
        Maximizes data per request since free tier only allows 10 requests/month
        """
        if not self.twitter_client:
            logger.error("Twitter client not initialized")
            return []

        try:
            # Check rate limit before making request
            rate_limit_ok = await self._check_rate_limit("twitter_search")
            if not rate_limit_ok:
                logger.warning("Rate limit reached, skipping request")
                return []

            # MAXIMIZE results per request - free tier only gives 10 requests/month!
            max_results = min(max_results, settings.TWITTER_MAX_RESULTS_PER_REQUEST)

            logger.info(f"Fetching maximum {max_results} tweets per request (optimized for free tier)")

            # Request ALL available tweet fields to get maximum data value
            params = {
                "query": query,
                "max_results": max_results,
                "tweet_fields": [
                    "created_at",
                    "public_metrics",  # likes, retweets, replies, quotes
                    "lang",
                    "author_id",
                    "conversation_id",
                    "entities",  # hashtags, mentions, urls
                    "geo",  # location data if available
                    "in_reply_to_user_id",
                    "referenced_tweets",  # retweets, quotes, replies
                    "reply_settings",
                    "source",  # what app was used
                    "context_annotations",  # topics and entities
                    "possibly_sensitive"
                ],
                "expansions": [
                    "author_id",
                    "referenced_tweets.id",
                    "in_reply_to_user_id",
                    "geo.place_id",
                    "entities.mentions.username",
                    "referenced_tweets.id.author_id"
                ],
                "user_fields": [
                    "username",
                    "name",
                    "verified",
                    "description",
                    "public_metrics",  # followers, following, tweet count
                    "profile_image_url",
                    "location",
                    "created_at"
                ],
                "place_fields": [
                    "full_name",
                    "country",
                    "country_code",
                    "geo",
                    "place_type"
                ]
            }

            if start_time:
                # Twitter API requires RFC3339 format with timezone
                # Convert to UTC and add 'Z' suffix
                params["start_time"] = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            # Make API request (runs in thread pool to avoid blocking)
            logger.info(f"Making Twitter API request with enhanced fields for maximum data extraction")
            response = await asyncio.to_thread(
                self.twitter_client.search_recent_tweets,
                **params
            )

            # Track rate limit usage
            await self._track_rate_limit("twitter_search")

            if not response.data:
                logger.info(f"No tweets found for query: {query}")
                return []

            # Parse response with ENHANCED data extraction
            tweets = []
            users_dict = {user.id: user for user in (response.includes.get('users', []) or [])}
            places_dict = {place.id: place for place in (response.includes.get('places', []) or [])} if response.includes and 'places' in response.includes else {}

            for tweet in response.data:
                author = users_dict.get(tweet.author_id)

                # Extract place/location data
                place_data = None
                if hasattr(tweet, 'geo') and tweet.geo and tweet.geo.get('place_id'):
                    place = places_dict.get(tweet.geo['place_id'])
                    if place:
                        place_data = {
                            "name": place.full_name,
                            "country": place.country,
                            "country_code": place.country_code,
                            "type": place.place_type
                        }

                # Extract entities (hashtags, mentions, urls)
                entities_data = {}
                if hasattr(tweet, 'entities') and tweet.entities:
                    entities_data = {
                        "hashtags": [tag.get('tag', '') for tag in tweet.entities.get('hashtags', [])],
                        "mentions": [mention.get('username', '') for mention in tweet.entities.get('mentions', [])],
                        "urls": [url.get('expanded_url', url.get('url', '')) for url in tweet.entities.get('urls', [])]
                    }

                # Extract context annotations (topics/entities detected by Twitter)
                context_data = []
                if hasattr(tweet, 'context_annotations') and tweet.context_annotations:
                    context_data = [
                        {
                            "domain": ctx.get('domain', {}).get('name'),
                            "entity": ctx.get('entity', {}).get('name')
                        }
                        for ctx in tweet.context_annotations[:5]  # Top 5 contexts
                    ]

                tweet_data = {
                    "id": str(tweet.id),
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "author": {
                        "id": str(tweet.author_id),
                        "username": author.username if author else None,
                        "name": author.name if author else None,
                        "verified": author.verified if author and hasattr(author, 'verified') else False,
                        "description": author.description if author and hasattr(author, 'description') else None,
                        "followers_count": author.public_metrics.get('followers_count', 0) if author and hasattr(author, 'public_metrics') else 0,
                        "following_count": author.public_metrics.get('following_count', 0) if author and hasattr(author, 'public_metrics') else 0,
                        "tweet_count": author.public_metrics.get('tweet_count', 0) if author and hasattr(author, 'public_metrics') else 0,
                        "profile_image_url": author.profile_image_url if author and hasattr(author, 'profile_image_url') else None,
                        "location": author.location if author and hasattr(author, 'location') else None
                    },
                    "metrics": {
                        "likes": tweet.public_metrics.get("like_count", 0),
                        "retweets": tweet.public_metrics.get("retweet_count", 0),
                        "replies": tweet.public_metrics.get("reply_count", 0),
                        "quotes": tweet.public_metrics.get("quote_count", 0)
                    } if tweet.public_metrics else {},
                    "language": tweet.lang if hasattr(tweet, 'lang') else None,
                    "source": tweet.source if hasattr(tweet, 'source') else None,
                    "possibly_sensitive": tweet.possibly_sensitive if hasattr(tweet, 'possibly_sensitive') else False,
                    "conversation_id": str(tweet.conversation_id) if hasattr(tweet, 'conversation_id') else None,
                    "entities": entities_data,
                    "place": place_data,
                    "context_annotations": context_data,
                    "is_reply": bool(tweet.in_reply_to_user_id) if hasattr(tweet, 'in_reply_to_user_id') else False,
                    "is_retweet": any(ref.get('type') == 'retweeted' for ref in (tweet.referenced_tweets or [])) if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets else False
                }

                tweets.append(tweet_data)

            logger.info(f"✅ Successfully fetched {len(tweets)} tweets with FULL data extraction")
            logger.info(f"   → Extracted: metrics, entities, context, author details, location data")
            return tweets

        except tweepy.TooManyRequests as e:
            logger.warning(f"Twitter API rate limit exceeded: {str(e)}")
            # Mark rate limit in Redis to prevent further requests
            await self._mark_rate_limit_exceeded("twitter_search")
            return []  # Return empty list instead of raising
        except tweepy.Unauthorized as e:
            logger.error("Twitter API authentication failed")
            return []
        except Exception as e:
            logger.error(f"Error fetching tweets: {str(e)}")
            return []

    async def store_posts(self, posts: List[Dict[str, Any]]) -> int:
        """Store social media posts in database"""
        stored_count = 0

        for post_data in posts:
            try:
                # Check if post already exists
                result = await self.db.execute(
                    select(SocialPost).where(SocialPost.id == post_data['id'])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    continue

                # Analyze sentiment
                sentiment_result = await self.ai_service.analyze_sentiment(post_data['text'])

                # Extract hashtags
                import re
                hashtags = re.findall(r'#(\w+)', post_data['text'])

                # Calculate total engagement
                metrics = post_data.get('metrics', {})
                engagement = metrics.get('likes', 0) + metrics.get('retweets', 0) + metrics.get('replies', 0)

                # Create post object
                post = SocialPost(
                    id=post_data['id'],
                    platform='twitter',
                    handle=post_data['author']['username'] if post_data.get('author') else None,
                    text=post_data['text'],
                    likes=metrics.get('likes', 0),
                    retweets=metrics.get('retweets', 0),
                    replies=metrics.get('replies', 0),
                    engagement_total=engagement,
                    sentiment=sentiment_result['label'],
                    sentiment_score=sentiment_result['score'],
                    sentiment_confidence=sentiment_result['confidence'],
                    hashtags=hashtags,
                    language=post_data.get('language', 'en'),
                    posted_at=datetime.fromisoformat(post_data['created_at'].replace('Z', '+00:00')) if post_data.get('created_at') else datetime.utcnow()
                )

                self.db.add(post)
                stored_count += 1

            except Exception as e:
                logger.error(f"Error storing post {post_data.get('id')}: {str(e)}")
                continue

        # Commit all posts
        try:
            await self.db.commit()
            logger.info(f"Stored {stored_count} posts")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error committing posts: {str(e)}")

        return stored_count

    async def get_overview(
        self,
        date_range: str = "Last 7 Days",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get overview metrics with caching"""

        # Try cache first
        cache_key = f"overview:{date_range}:{start_date}:{end_date}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # Calculate date range
        end = datetime.utcnow()
        if date_range == "Last 7 Days":
            start = end - timedelta(days=7)
        elif date_range == "Last 30 Days":
            start = end - timedelta(days=30)
        elif date_range == "Today":
            start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start = end - timedelta(days=7)

        # Query database
        result = await self.db.execute(
            select(
                func.count(SocialPost.id).label('total_posts'),
                func.sum(SocialPost.engagement_total).label('total_engagement'),
                func.count(func.distinct(SocialPost.handle)).label('unique_users')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            )
        )
        stats = result.one()

        # Sentiment breakdown
        sentiment_result = await self.db.execute(
            select(
                SocialPost.sentiment,
                func.count(SocialPost.id).label('count')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            ).group_by(SocialPost.sentiment)
        )
        sentiment_data = {row.sentiment: row.count for row in sentiment_result}

        overview = {
            "total_posts": stats.total_posts or 0,
            "total_engagement": int(stats.total_engagement or 0),
            "unique_users": stats.unique_users or 0,
            "sentiment": {
                "positive": sentiment_data.get("positive", 0),
                "negative": sentiment_data.get("negative", 0),
                "neutral": sentiment_data.get("neutral", 0)
            },
            "date_range": {
                "start": start.isoformat(),
                "end": end.isoformat()
            }
        }

        # Cache result
        await self._set_cache(cache_key, overview, ttl=settings.CACHE_TTL_MEDIUM)

        return overview

    async def get_sentiment_time_series(
        self,
        granularity: str = "hour",
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get sentiment time series data"""

        cache_key = f"sentiment_series:{granularity}:{hours}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        end = datetime.utcnow()
        start = end - timedelta(hours=hours)

        result = await self.db.execute(
            select(SentimentTimeSeries).where(
                and_(
                    SentimentTimeSeries.timestamp >= start,
                    SentimentTimeSeries.timestamp <= end,
                    SentimentTimeSeries.granularity == granularity
                )
            ).order_by(SentimentTimeSeries.timestamp)
        )

        series = result.scalars().all()

        data = [{
            "timestamp": s.timestamp.isoformat(),
            "positive": s.positive_count,
            "negative": s.negative_count,
            "neutral": s.neutral_count,
            "total": s.total_count,
            "avg_score": s.avg_sentiment_score
        } for s in series]

        await self._set_cache(cache_key, data, ttl=settings.CACHE_TTL_SHORT)

        return data

    async def get_trending_topics(self, limit: int = 10) -> Dict[str, Any]:
        """Get trending topics with caching"""

        cache_key = f"trending_topics:{limit}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # Get recent posts
        end = datetime.utcnow()
        start = end - timedelta(hours=24)

        result = await self.db.execute(
            select(SocialPost).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            ).limit(1000)
        )
        posts = result.scalars().all()

        # Extract and count hashtags
        from collections import Counter
        hashtag_counter = Counter()

        for post in posts:
            if post.hashtags:
                for tag in post.hashtags:
                    hashtag_counter[tag] += 1

        # Get top trending hashtags
        trends = {
            "hashtags": [
                {"tag": tag, "count": count}
                for tag, count in hashtag_counter.most_common(limit)
            ],
            "total_posts": len(posts),
            "time_window": "24h"
        }

        await self._set_cache(cache_key, trends, ttl=settings.CACHE_TTL_MEDIUM)

        return trends

    async def _check_rate_limit(self, api_name: str) -> bool:
        """Check if we're within rate limits"""
        redis = await get_redis()
        # Use 15-minute windows by rounding down to nearest 15 minutes
        now = datetime.utcnow()
        window_key = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0).strftime('%Y%m%d%H%M')
        key = f"rate_limit:{api_name}:{window_key}"

        count = await redis.get(key)
        if count and int(count) >= self.max_requests_per_window:
            logger.warning(f"Rate limit reached for {api_name}: {count}/{self.max_requests_per_window}")
            return False

        return True

    async def _track_rate_limit(self, api_name: str):
        """Track API usage for rate limiting"""
        redis = await get_redis()
        # Use 15-minute windows by rounding down to nearest 15 minutes
        now = datetime.utcnow()
        window_key = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0).strftime('%Y%m%d%H%M')
        key = f"rate_limit:{api_name}:{window_key}"

        await redis.incr(key)
        await redis.expire(key, self.rate_limit_window)

    async def _mark_rate_limit_exceeded(self, api_name: str):
        """Mark that rate limit has been exceeded by Twitter API"""
        redis = await get_redis()
        # Set rate limit to max for current window
        now = datetime.utcnow()
        window_key = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0).strftime('%Y%m%d%H%M')
        key = f"rate_limit:{api_name}:{window_key}"

        await redis.set(key, self.max_requests_per_window)
        await redis.expire(key, self.rate_limit_window)
        logger.info(f"Marked rate limit exceeded for {api_name}, blocking requests for this window")

    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        try:
            redis = await get_redis()
            data = await redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
        return None

    async def _set_cache(self, key: str, value: Any, ttl: int):
        """Set data in Redis cache"""
        try:
            redis = await get_redis()
            await redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")

    async def get_live_sentiment(self) -> Dict[str, Any]:
        """Get real-time sentiment gauge value"""
        cache_key = "live_sentiment"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # Get recent posts from last hour
        end = datetime.utcnow()
        start = end - timedelta(hours=1)

        result = await self.db.execute(
            select(
                func.avg(SocialPost.sentiment_score).label('avg_score'),
                func.count(SocialPost.id).label('total_posts')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end,
                    SocialPost.sentiment_score.isnot(None)
                )
            )
        )
        stats = result.one()

        # Convert to 0-100 scale
        sentiment_value = ((stats.avg_score or 0) + 1) * 50

        data = {
            "value": round(sentiment_value, 1),
            "total_posts": stats.total_posts or 0,
            "timestamp": end.isoformat()
        }

        await self._set_cache(cache_key, data, ttl=60)  # Cache for 1 minute
        return data

    async def get_sentiment_series(
        self,
        range_str: str = "Last 7 Days",
        granularity: str = "day",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sentiment time series data"""
        cache_key = f"sentiment_series:{range_str}:{granularity}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        end = datetime.utcnow()
        if range_str == "Last 7 Days":
            start = end - timedelta(days=7)
        elif range_str == "Last 30 Days":
            start = end - timedelta(days=30)
        else:
            start = end - timedelta(days=7)

        # Query posts grouped by time
        result = await self.db.execute(
            select(
                func.date_trunc(granularity, SocialPost.posted_at).label('time_bucket'),
                func.count(func.case((SocialPost.sentiment == 'positive', 1))).label('pos'),
                func.count(func.case((SocialPost.sentiment == 'negative', 1))).label('neg'),
                func.count(func.case((SocialPost.sentiment == 'neutral', 1))).label('neu')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            ).group_by('time_bucket').order_by('time_bucket')
        )

        series_data = []
        for row in result:
            series_data.append({
                "name": row.time_bucket.strftime('%Y-%m-%d %H:%M') if row.time_bucket else "",
                "pos": row.pos or 0,
                "neg": row.neg or 0,
                "neu": row.neu or 0
            })

        data = {
            "series": series_data,
            "summary": {
                "average_sentiment": 0.5,
                "trend": "stable",
                "volatility": "low"
            }
        }

        await self._set_cache(cache_key, data, ttl=settings.CACHE_TTL_MEDIUM)
        return data

    async def get_sentiment_categories(
        self,
        range_str: str = "Last 7 Days",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sentiment breakdown by categories"""
        cache_key = f"sentiment_categories:{range_str}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        end = datetime.utcnow()
        if range_str == "Last 7 Days":
            start = end - timedelta(days=7)
        elif range_str == "Last 30 Days":
            start = end - timedelta(days=30)
        else:
            start = end - timedelta(days=7)

        result = await self.db.execute(
            select(
                SocialPost.sentiment,
                func.count(SocialPost.id).label('count')
            ).where(
                and_(
                    SocialPost.posted_at >= start,
                    SocialPost.posted_at <= end
                )
            ).group_by(SocialPost.sentiment)
        )

        categories = {row.sentiment: row.count for row in result}

        data = {
            "positive": categories.get("positive", 0),
            "negative": categories.get("negative", 0),
            "neutral": categories.get("neutral", 0)
        }

        await self._set_cache(cache_key, data, ttl=settings.CACHE_TTL_MEDIUM)
        return data

    async def get_trending_hashtags(
        self,
        limit: int = 20,
        min_mentions: int = 100,
        range_str: str = "Last 7 Days"
    ) -> List[Dict[str, Any]]:
        """Get trending hashtags"""
        from app.models import Hashtag

        result = await self.db.execute(
            select(Hashtag).where(
                Hashtag.count >= min_mentions
            ).order_by(desc(Hashtag.count)).limit(limit)
        )
        hashtags = result.scalars().all()

        return [{
            "tag": h.tag,
            "count": h.count,
            "change": h.change,
            "sentiment": {
                "pos": h.sentiment_pos,
                "neg": h.sentiment_neg,
                "neu": h.sentiment_neu
            },
            "top_posts": []
        } for h in hashtags]

    async def get_hashtag_details(self, tag: str) -> Optional[Dict[str, Any]]:
        """Get detailed hashtag analysis"""
        from app.models import Hashtag

        result = await self.db.execute(
            select(Hashtag).where(Hashtag.tag == tag)
        )
        hashtag = result.scalar_one_or_none()

        if not hashtag:
            return None

        # Get top posts with this hashtag
        posts_result = await self.db.execute(
            select(SocialPost).where(
                SocialPost.text.ilike(f'%#{tag}%')
            ).order_by(desc(SocialPost.engagement_total)).limit(5)
        )
        posts = posts_result.scalars().all()

        return {
            "tag": hashtag.tag,
            "count": hashtag.count,
            "change": hashtag.change,
            "sentiment": {
                "pos": hashtag.sentiment_pos,
                "neg": hashtag.sentiment_neg,
                "neu": hashtag.sentiment_neu
            },
            "top_posts": [{
                "handle": p.handle,
                "text": p.text,
                "url": p.url or "",
                "engagement": str(p.engagement_total)
            } for p in posts]
        }

    async def get_keyword_trends(
        self,
        limit: int = 20,
        category: Optional[str] = None,
        range_str: str = "Last 7 Days"
    ) -> List[Dict[str, Any]]:
        """Get keyword trends and analysis"""
        from app.models import Keyword

        query = select(Keyword)
        if category:
            query = query.where(Keyword.category == category)

        query = query.order_by(desc(Keyword.mentions)).limit(limit)

        result = await self.db.execute(query)
        keywords = result.scalars().all()

        return [{
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
            "score": k.score
        } for k in keywords]

    async def get_influencers(
        self,
        limit: int = 20,
        min_followers: int = 100000,
        verified_only: bool = False,
        range_str: str = "Last 7 Days"
    ) -> List[Dict[str, Any]]:
        """Get influential accounts and their metrics"""
        from app.models import Influencer

        query = select(Influencer).where(
            Influencer.followers_primary >= min_followers
        )

        if verified_only:
            query = query.where(Influencer.verified == True)

        query = query.order_by(desc(Influencer.engagement)).limit(limit)

        result = await self.db.execute(query)
        influencers = result.scalars().all()

        return [{
            "handle": i.handle,
            "engagement": i.engagement,
            "followers_primary": i.followers_primary,
            "following": i.following,
            "verified": i.verified,
            "avatar_url": i.avatar_url,
            "engagement_rate": i.engagement_rate,
            "top_mentions": i.top_mentions or []
        } for i in influencers]

    async def get_account_analysis(self, handle: str) -> Optional[Dict[str, Any]]:
        """Get detailed account analysis"""
        from app.models import Influencer

        result = await self.db.execute(
            select(Influencer).where(Influencer.handle == handle)
        )
        influencer = result.scalar_one_or_none()

        if not influencer:
            return None

        # Get posts from this account
        posts_result = await self.db.execute(
            select(SocialPost).where(
                SocialPost.handle == handle
            ).order_by(desc(SocialPost.posted_at)).limit(10)
        )
        posts = posts_result.scalars().all()

        return {
            "handle": influencer.handle,
            "engagement": influencer.engagement,
            "followers": influencer.followers_primary,
            "following": influencer.following,
            "verified": influencer.verified,
            "engagement_rate": influencer.engagement_rate,
            "recent_posts": [{
                "id": p.id,
                "text": p.text,
                "engagement": p.engagement_total,
                "sentiment": p.sentiment,
                "posted_at": p.posted_at.isoformat()
            } for p in posts]
        }

    async def get_geographic_states(
        self,
        range_str: str = "Last 7 Days",
        keyword: Optional[str] = None,
        hashtag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get geographic distribution data"""
        from app.models import GeographicData

        result = await self.db.execute(
            select(GeographicData).order_by(desc(GeographicData.mentions))
        )
        states = result.scalars().all()

        return [{
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
        } for s in states]

    async def get_geographic_coordinates(
        self,
        range_str: str = "Last 7 Days",
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get geographic data with coordinates for mapping"""
        from app.models import GeographicData

        result = await self.db.execute(select(GeographicData))
        states = result.scalars().all()

        features = []
        for state in states:
            if state.coordinates:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            state.coordinates.get("lon", 0),
                            state.coordinates.get("lat", 0)
                        ]
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

    async def get_top_posts(
        self,
        limit: int = 20,
        range_str: str = "Last 7 Days",
        keyword: Optional[str] = None,
        hashtag: Optional[str] = None,
        min_engagement: int = 100
    ) -> List[Dict[str, Any]]:
        """Get top performing posts"""
        end = datetime.utcnow()
        if range_str == "Last 7 Days":
            start = end - timedelta(days=7)
        elif range_str == "Last 30 Days":
            start = end - timedelta(days=30)
        else:
            start = end - timedelta(days=7)

        query = select(SocialPost).where(
            and_(
                SocialPost.posted_at >= start,
                SocialPost.posted_at <= end,
                SocialPost.engagement_total >= min_engagement
            )
        ).order_by(desc(SocialPost.engagement_total)).limit(limit)

        result = await self.db.execute(query)
        posts = result.scalars().all()

        return [{
            "id": p.id,
            "handle": p.handle or "",
            "text": p.text,
            "url": p.url or "",
            "engagement": str(p.engagement_total),
            "likes": p.likes,
            "retweets": p.retweets,
            "replies": p.replies,
            "posted_at": p.posted_at,
            "sentiment": p.sentiment,
            "sentiment_score": p.sentiment_score,
            "topics": p.hashtags or [],
            "language": p.language
        } for p in posts]

    async def search_posts(
        self,
        query: str,
        range_str: str = "Last 7 Days",
        limit: int = 50,
        offset: int = 0,
        sentiment: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search posts with filters"""
        end = datetime.utcnow()
        if range_str == "Last 7 Days":
            start = end - timedelta(days=7)
        elif range_str == "Last 30 Days":
            start = end - timedelta(days=30)
        else:
            start = end - timedelta(days=7)

        db_query = select(SocialPost).where(
            and_(
                SocialPost.posted_at >= start,
                SocialPost.posted_at <= end,
                SocialPost.text.ilike(f'%{query}%')
            )
        )

        if sentiment:
            db_query = db_query.where(SocialPost.sentiment == sentiment)

        if language:
            db_query = db_query.where(SocialPost.language == language)

        # Get total count
        count_query = select(func.count()).select_from(
            db_query.subquery()
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        db_query = db_query.order_by(desc(SocialPost.posted_at)).limit(limit).offset(offset)
        result = await self.db.execute(db_query)
        posts = result.scalars().all()

        return {
            "posts": [{
                "id": p.id,
                "handle": p.handle or "",
                "text": p.text,
                "url": p.url or "",
                "engagement": str(p.engagement_total),
                "posted_at": p.posted_at,
                "sentiment": p.sentiment,
                "relevance_score": 0.85
            } for p in posts],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    async def get_anomalies(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        range_str: str = "Last 7 Days",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get anomalies with filtering"""
        from app.models import Anomaly

        end = datetime.utcnow()
        if range_str == "Last 7 Days":
            start = end - timedelta(days=7)
        elif range_str == "Last 30 Days":
            start = end - timedelta(days=30)
        else:
            start = end - timedelta(days=7)

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

        return [{
            "id": str(a.id),
            "title": a.title,
            "severity": a.severity,
            "detected_at": a.detected_at,
            "summary": a.summary or "",
            "metric": a.metric or "",
            "delta": a.delta or ""
        } for a in anomalies]

    async def get_fetch_summary(
        self,
        query: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Get analytics summary for recently fetched tweets"""
        try:
            end_time = datetime.utcnow()

            # Get tweets from this fetch
            result = await self.db.execute(
                select(SocialPost).where(
                    and_(
                        SocialPost.posted_at >= start_time,
                        SocialPost.posted_at <= end_time,
                        SocialPost.processed_at >= start_time  # Recently processed
                    )
                )
            )
            posts = result.scalars().all()

            if not posts:
                return {
                    "total_posts": 0,
                    "sentiment_breakdown": {},
                    "avg_engagement": 0,
                    "top_hashtags": []
                }

            # Sentiment breakdown
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_engagement = 0
            all_hashtags = []

            for post in posts:
                sentiment_counts[post.sentiment] = sentiment_counts.get(post.sentiment, 0) + 1
                total_engagement += post.engagement_total
                if post.hashtags:
                    all_hashtags.extend(post.hashtags)

            # Count hashtags
            from collections import Counter
            hashtag_counts = Counter(all_hashtags)

            return {
                "total_posts": len(posts),
                "sentiment_breakdown": sentiment_counts,
                "avg_engagement": total_engagement / len(posts) if posts else 0,
                "total_engagement": total_engagement,
                "top_hashtags": [
                    {"tag": tag, "count": count}
                    for tag, count in hashtag_counts.most_common(5)
                ],
                "avg_sentiment_score": sum(p.sentiment_score for p in posts) / len(posts) if posts else 0
            }

        except Exception as e:
            logger.error(f"Error getting fetch summary: {str(e)}")
            return {}

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            # Total posts
            total_result = await self.db.execute(
                select(func.count(SocialPost.id))
            )
            total_posts = total_result.scalar() or 0

            # Sentiment breakdown
            sentiment_result = await self.db.execute(
                select(
                    SocialPost.sentiment,
                    func.count(SocialPost.id).label('count')
                ).group_by(SocialPost.sentiment)
            )
            sentiment_data = {row.sentiment: row.count for row in sentiment_result}

            # Engagement stats
            engagement_result = await self.db.execute(
                select(
                    func.sum(SocialPost.engagement_total).label('total'),
                    func.avg(SocialPost.engagement_total).label('average'),
                    func.max(SocialPost.engagement_total).label('max')
                )
            )
            engagement = engagement_result.one()

            # Most recent tweet
            recent_result = await self.db.execute(
                select(SocialPost.posted_at).order_by(desc(SocialPost.posted_at)).limit(1)
            )
            most_recent = recent_result.scalar()

            # Date range
            oldest_result = await self.db.execute(
                select(SocialPost.posted_at).order_by(SocialPost.posted_at).limit(1)
            )
            oldest = oldest_result.scalar()

            # Top hashtags
            hashtag_result = await self.db.execute(
                select(SocialPost.hashtags).where(SocialPost.hashtags.isnot(None))
            )
            from collections import Counter
            all_hashtags = Counter()
            for row in hashtag_result:
                if row[0]:
                    all_hashtags.update(row[0])

            return {
                "total_posts": total_posts,
                "sentiment_distribution": sentiment_data,
                "engagement": {
                    "total": int(engagement.total or 0),
                    "average": float(engagement.average or 0),
                    "max": int(engagement.max or 0)
                },
                "date_range": {
                    "oldest_tweet": oldest.isoformat() if oldest else None,
                    "newest_tweet": most_recent.isoformat() if most_recent else None
                },
                "top_hashtags": [
                    {"tag": tag, "count": count}
                    for tag, count in all_hashtags.most_common(10)
                ]
            }

        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {}

    async def reanalyze_all_tweets(self) -> int:
        """Re-run sentiment analysis on all tweets in database"""
        try:
            result = await self.db.execute(select(SocialPost))
            posts = result.scalars().all()

            count = 0
            for post in posts:
                # Re-analyze sentiment
                sentiment_result = await self.ai_service.analyze_sentiment(post.text)
                post.sentiment = sentiment_result['label']
                post.sentiment_score = sentiment_result['score']
                post.sentiment_confidence = sentiment_result['confidence']
                count += 1

            await self.db.commit()
            logger.info(f"Re-analyzed {count} tweets")
            return count

        except Exception as e:
            logger.error(f"Error re-analyzing tweets: {str(e)}")
            await self.db.rollback()
            return 0

# Factory function for dependency injection
def get_data_service(db: AsyncSession) -> DataService:
    """Get data service instance with database session"""
    return DataService(db)
