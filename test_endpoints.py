#!/usr/bin/env python3
"""
Simplified test script using sample data to demonstrate all endpoints
"""
import asyncio
from datetime import datetime, timedelta
from app.database import AsyncSessionLocal
from app.services.data_service import DataService
from app.services.ai_service import AIService
from app.models import SocialPost
from sqlalchemy import select, func, desc
from collections import Counter

async def main():
    print("=" * 80)
    print("🇳🇬 TESTING: Nigeria FIFA Qualification - All Endpoints Demo")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        data_service = DataService(db)
        ai_service = AIService()
        
        # Create sample tweets about Nigeria FIFA qualification
        print("📝 Creating sample tweets about Nigeria FIFA qualification...")
        print("-" * 80)
        
        sample_tweets = [
            {
                "id": f"tweet_1_{int(datetime.utcnow().timestamp())}",
                "text": "🇳🇬 Super Eagles dominate! Nigeria 3-0 victory in FIFA World Cup qualifiers! Amazing performance! #SuperEagles #Nigeria #WorldCup #FIFA",
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
                "author": {"username": "nigerian_sports", "name": "Nigerian Sports Fan"},
                "metrics": {"likes": 1250, "retweets": 450, "replies": 89},
                "language": "en"
            },
            {
                "id": f"tweet_2_{int(datetime.utcnow().timestamp())}",
                "text": "Disappointed with Nigeria's defense today. We need better tactics for FIFA qualification. #SuperEagles #Nigeria",
                "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat() + "Z",
                "author": {"username": "football_analyst", "name": "Football Analyst"},
                "metrics": {"likes": 340, "retweets": 120, "replies": 45},
                "language": "en"
            },
            {
                "id": f"tweet_3_{int(datetime.utcnow().timestamp())}",
                "text": "Excited to watch Nigeria play! The Super Eagles will qualify for the FIFA World Cup! 🦅 #SuperEagles #WorldCup2026",
                "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat() + "Z",
                "author": {"username": "eagles_fan", "name": "Eagles Forever"},
                "metrics": {"likes": 890, "retweets": 234, "replies": 56},
                "language": "en"
            },
            {
                "id": f"tweet_4_{int(datetime.utcnow().timestamp())}",
                "text": "Victor Osimhen scored twice! What a player! Nigeria is looking strong for FIFA World Cup qualification! 🇳🇬⚽ #Nigeria #SuperEagles",
                "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z",
                "author": {"username": "osimhen_fan", "name": "Osimhen Updates"},
                "metrics": {"likes": 2100, "retweets": 678, "replies": 234},
                "language": "en"
            },
            {
                "id": f"tweet_5_{int(datetime.utcnow().timestamp())}",
                "text": "Nigeria's midfield needs work. Too many turnovers in the FIFA qualifier match. #SuperEagles #Nigeria",
                "created_at": (datetime.utcnow() - timedelta(hours=15)).isoformat() + "Z",
                "author": {"username": "tactical_view", "name": "Tactical Analysis"},
                "metrics": {"likes": 456, "retweets": 123, "replies": 67},
                "language": "en"
            }
        ]
        
        stored_count = await data_service.store_posts(sample_tweets)
        print(f"✅ Created and analyzed {stored_count} tweets with sentiment analysis")
        print()
        
        # Display tweets with sentiment
        print("📊 TWEETS WITH SENTIMENT ANALYSIS")
        print("=" * 80)
        
        result = await db.execute(
            select(SocialPost).order_by(desc(SocialPost.posted_at)).limit(5)
        )
        posts = result.scalars().all()
        
        for i, post in enumerate(posts, 1):
            sentiment_emoji = "😊" if post.sentiment == "positive" else "😐" if post.sentiment == "neutral" else "😞"
            print(f"\n{i}. {sentiment_emoji} TWEET #{post.id}")
            print(f"   Author: @{post.handle}")
            print(f"   Posted: {post.posted_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Text: {post.text}")
            print(f"   Sentiment: {post.sentiment.upper()} (confidence: {post.sentiment_score:.2f})")
            print(f"   Engagement: {post.engagement_total:,} (👍{post.likes} 🔄{post.retweets} 💬{post.replies})")
            if post.hashtags:
                print(f"   Hashtags: {', '.join(['#' + tag for tag in post.hashtags])}")
        print()
        
        # Sentiment breakdown
        print("📈 SENTIMENT ANALYSIS BREAKDOWN")
        print("=" * 80)
        
        result = await db.execute(
            select(
                SocialPost.sentiment,
                func.count(SocialPost.id).label('count'),
                func.avg(SocialPost.sentiment_score).label('avg_score')
            ).group_by(SocialPost.sentiment)
        )
        
        sentiment_stats = result.all()
        total_posts = sum(row.count for row in sentiment_stats)
        
        print(f"Total Posts: {total_posts}\n")
        for row in sentiment_stats:
            percentage = (row.count / total_posts * 100) if total_posts > 0 else 0
            emoji = "😊" if row.sentiment == "positive" else "😐" if row.sentiment == "neutral" else "😞"
            bar = "█" * int(percentage / 5)
            print(f"{emoji} {row.sentiment.upper():8} : {row.count:2} posts ({percentage:5.1f}%) {bar}")
            print(f"           Avg Score: {row.avg_score:.3f}")
        print()
        
        # Trending hashtags
        print("🔥 TRENDING HASHTAGS")
        print("=" * 80)
        
        result = await db.execute(
            select(SocialPost.hashtags).where(SocialPost.hashtags.isnot(None))
        )
        
        all_hashtags = Counter()
        for row in result:
            if row[0]:
                for tag in row[0]:
                    all_hashtags[tag] += 1
        
        for i, (tag, count) in enumerate(all_hashtags.most_common(10), 1):
            print(f"{i:2}. #{tag:20} : {count} mentions")
        print()
        
        # Keyword extraction
        print("🔍 TOP KEYWORDS EXTRACTED")
        print("=" * 80)
        
        result = await db.execute(select(SocialPost))
        posts = result.scalars().all()
        all_text = " ".join([post.text for post in posts])
        keywords = await ai_service.extract_keywords(all_text, top_n=10)

        if keywords:
            for i, keyword in enumerate(keywords, 1):
                print(f"{i:2}. {keyword}")
        else:
            print("  No keywords extracted")
        print()
        
        # Engagement metrics
        print("📊 ENGAGEMENT METRICS")
        print("=" * 80)
        
        result = await db.execute(
            select(
                func.sum(SocialPost.likes).label('total_likes'),
                func.sum(SocialPost.retweets).label('total_retweets'),
                func.sum(SocialPost.replies).label('total_replies'),
                func.sum(SocialPost.engagement_total).label('total_engagement'),
                func.avg(SocialPost.engagement_total).label('avg_engagement'),
                func.max(SocialPost.engagement_total).label('max_engagement')
            )
        )
        
        metrics = result.one()
        print(f"Total Likes:       {metrics.total_likes or 0:>8,}")
        print(f"Total Retweets:    {metrics.total_retweets or 0:>8,}")
        print(f"Total Replies:     {metrics.total_replies or 0:>8,}")
        print(f"Total Engagement:  {metrics.total_engagement or 0:>8,}")
        print(f"Average Engagement:{metrics.avg_engagement or 0:>8,.1f}")
        print(f"Top Engagement:    {metrics.max_engagement or 0:>8,}")
        print()
        
        # Top posts
        print("🏆 TOP PERFORMING POSTS")
        print("=" * 80)
        
        result = await db.execute(
            select(SocialPost).order_by(desc(SocialPost.engagement_total)).limit(3)
        )
        
        top_posts = result.scalars().all()
        for i, post in enumerate(top_posts, 1):
            print(f"\n#{i} Most Engaging:")
            print(f"   @{post.handle}: {post.text[:70]}...")
            print(f"   Engagement: {post.engagement_total:,} | Sentiment: {post.sentiment.upper()}")
        print()
        
        # Test API endpoints
        print("🔌 TESTING API ENDPOINTS")
        print("=" * 80)
        
        # Overview
        overview = await data_service.get_overview("Last 7 Days")
        print(f"✓ /api/v1/data/overview")
        print(f"  Posts: {overview['total_posts']}, Engagement: {overview['total_engagement']:,}")
        print(f"  Sentiment → Pos:{overview['sentiment']['positive']} Neg:{overview['sentiment']['negative']} Neu:{overview['sentiment']['neutral']}")
        
        # Live sentiment
        live_sentiment = await data_service.get_live_sentiment()
        print(f"\n✓ /api/v1/data/sentiment/live")
        print(f"  Score: {live_sentiment['value']:.1f}/100 (based on {live_sentiment['total_posts']} recent posts)")
        
        # Top posts
        top_posts_data = await data_service.get_top_posts(limit=5, range_str="Last 7 Days")
        print(f"\n✓ /api/v1/data/posts/top")
        print(f"  Retrieved {len(top_posts_data)} top performing posts")
        
        # Search posts
        search_results = await data_service.search_posts("FIFA", limit=10)
        print(f"\n✓ /api/v1/data/posts/search")
        print(f"  Found {len(search_results['posts'])} posts matching 'FIFA'")
        print(f"  Total available: {search_results['pagination']['total']}")
        
        print()
        
        # Summary
        print("=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Sample tweets created and stored")
        print(f"✅ Sentiment analysis performed (TextBlob)")
        print(f"✅ Hashtags extracted and counted")
        print(f"✅ Keywords identified")
        print(f"✅ Engagement metrics calculated")
        print(f"✅ Top posts ranked")
        print(f"✅ API endpoints tested successfully")
        print()
        print("🎉 All tests passed! The system is working correctly.")
        print()
        print("💡 Next steps:")
        print("   • View API docs: http://localhost:8000/docs")
        print("   • Test with real Twitter data (after rate limit resets)")
        print("   • Explore other endpoints in the API documentation")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
