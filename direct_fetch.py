#!/usr/bin/env python3
"""
Direct Twitter API fetch - bypasses local rate limiting
"""
import asyncio
from datetime import datetime, timedelta
import tweepy
import os
from app.database import AsyncSessionLocal
from app.services.data_service import DataService
from app.config import settings

async def fetch_and_store():
    print("=" * 80)
    print("🇳🇬 DIRECT FETCH: Nigerian Hot Topics")
    print("=" * 80)
    print()
    print(f"🔑 Using Bearer Token: {settings.TWITTER_BEARER_TOKEN[:30]}...")
    print()
    
    # Create Twitter client directly
    client = tweepy.Client(
        bearer_token=settings.TWITTER_BEARER_TOKEN,
        wait_on_rate_limit=False
    )
    
    # Search query for Nigerian hot topics
    query = "Nigeria"
    
    print(f"🔍 Search Query: {query}")
    print(f"📅 Fetching tweets from the last 7 days...")
    print()
    
    try:
        # Fetch tweets
        response = client.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=['created_at', 'public_metrics', 'lang', 'author_id'],
            expansions=['author_id'],
            user_fields=['username', 'name', 'verified', 'public_metrics']
        )
        
        if not response.data:
            print("❌ No tweets found")
            return
        
        print(f"✅ Fetched {len(response.data)} tweets!")
        print()
        
        # Parse tweets
        users_dict = {user.id: user for user in (response.includes.get('users', []) or [])} if response.includes else {}
        
        tweets = []
        for tweet in response.data:
            author = users_dict.get(tweet.author_id)
            
            tweet_data = {
                "id": str(tweet.id),
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                "author": {
                    "id": str(tweet.author_id),
                    "username": author.username if author else None,
                    "name": author.name if author else None,
                    "verified": author.verified if author and hasattr(author, 'verified') else False,
                    "followers_count": author.public_metrics.get('followers_count', 0) if author and hasattr(author, 'public_metrics') else 0,
                    "following_count": author.public_metrics.get('following_count', 0) if author and hasattr(author, 'public_metrics') else 0,
                },
                "metrics": {
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                    "quotes": tweet.public_metrics.get("quote_count", 0)
                } if tweet.public_metrics else {},
                "language": tweet.lang if hasattr(tweet, 'lang') else None,
            }
            tweets.append(tweet_data)
        
        # Store in database
        print("💾 Storing tweets in database...")
        async with AsyncSessionLocal() as db:
            data_service = DataService(db)
            stored_count = await data_service.store_posts(tweets)
            print(f"✅ Stored {stored_count} new tweets in database")
            print()
            
            # Display stored tweets
            from sqlalchemy import select, func, desc
            from app.models import SocialPost
            
            result = await db.execute(
                select(SocialPost)
                .order_by(desc(SocialPost.posted_at))
                .limit(10)
            )
            posts = result.scalars().all()
            
            print("=" * 80)
            print("📊 TWEET ANALYSIS")
            print("=" * 80)
            
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            
            for i, post in enumerate(posts, 1):
                print(f"\n📝 Tweet #{i}")
                print(f"   Author: @{post.author_username} ({post.author_name})")
                if post.author_verified:
                    print(f"   ✓ Verified | Followers: {post.author_followers_count:,}")
                print(f"   Posted: {post.posted_at}")
                print(f"   Text: {post.content}")
                print(f"   Engagement: ❤️ {post.likes_count} | 🔄 {post.shares_count} | 💬 {post.comments_count}")
                
                if post.sentiment_score > 0.1:
                    sentiment = "😊 Positive"
                    sentiment_counts["positive"] += 1
                elif post.sentiment_score < -0.1:
                    sentiment = "😢 Negative"
                    sentiment_counts["negative"] += 1
                else:
                    sentiment = "😐 Neutral"
                    sentiment_counts["neutral"] += 1
                
                print(f"   Sentiment: {sentiment} (score: {post.sentiment_score:.3f})")
                
                if post.hashtags:
                    print(f"   Hashtags: {', '.join(['#' + h for h in post.hashtags[:5]])}")
            
            # Summary
            print()
            print("=" * 80)
            print("📈 SENTIMENT SUMMARY")
            print("=" * 80)
            total = len(posts)
            if total > 0:
                print(f"Total Tweets: {total}")
                print(f"😊 Positive: {sentiment_counts['positive']} ({sentiment_counts['positive']/total*100:.0f}%)")
                print(f"😐 Neutral:  {sentiment_counts['neutral']} ({sentiment_counts['neutral']/total*100:.0f}%)")
                print(f"😢 Negative: {sentiment_counts['negative']} ({sentiment_counts['negative']/total*100:.0f}%)")
                
                avg_sentiment = sum(p.sentiment_score for p in posts) / total
                overall = "😊 POSITIVE" if avg_sentiment > 0.1 else "😢 NEGATIVE" if avg_sentiment < -0.1 else "😐 NEUTRAL"
                print(f"\nOverall: {overall} (avg: {avg_sentiment:.3f})")
            
            # Total database count
            result = await db.execute(select(func.count(SocialPost.id)))
            total_db = result.scalar()
            print(f"\n📊 Total tweets in database: {total_db}")
        
        print()
        print("=" * 80)
        print("✅ SUCCESS! Tweets fetched and saved to database")
        print("=" * 80)
        
    except tweepy.TooManyRequests as e:
        print(f"❌ Rate limit exceeded: {e}")
        print("   You've used your 10 requests for this month")
    except tweepy.Unauthorized as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your bearer token")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fetch_and_store())

