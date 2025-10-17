#!/usr/bin/env python3
"""
Twitter API Diagnostic Tool
Checks API health, rate limits, and quota status
"""
import tweepy
import asyncio
from datetime import datetime
from app.config import settings
from app.redis_client import get_redis
import json

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

async def main():
    print_section("🔍 TWITTER API DIAGNOSTICS")
    
    # 1. Check if Bearer Token is configured
    print("1️⃣  Checking Bearer Token Configuration...")
    if not settings.TWITTER_BEARER_TOKEN:
        print("❌ ERROR: TWITTER_BEARER_TOKEN is not set in .env file!")
        print("\n💡 To fix:")
        print("   1. Go to https://developer.twitter.com/")
        print("   2. Create a project and app")
        print("   3. Generate a Bearer Token")
        print("   4. Add it to your .env file: TWITTER_BEARER_TOKEN=your_token_here")
        return
    
    token_preview = settings.TWITTER_BEARER_TOKEN[:20] + "..." + settings.TWITTER_BEARER_TOKEN[-10:]
    print(f"✅ Bearer Token found: {token_preview}")
    
    # 2. Initialize Twitter client
    print("\n2️⃣  Initializing Twitter Client...")
    try:
        client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            wait_on_rate_limit=False
        )
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    # 3. Test API connectivity with a simple request
    print("\n3️⃣  Testing API Connectivity...")
    try:
        # Try to get rate limit status (this doesn't count against your quota)
        response = client.get_user(username="Twitter")
        if response.data:
            print(f"✅ API is reachable! Test user fetched: @{response.data.username}")
        else:
            print("⚠️  API responded but no data returned")
    except tweepy.Unauthorized as e:
        print("❌ AUTHENTICATION ERROR: Your Bearer Token is invalid or expired!")
        print(f"   Error: {e}")
        print("\n💡 To fix:")
        print("   1. Regenerate your Bearer Token in the Twitter Developer Portal")
        print("   2. Update your .env file with the new token")
        return
    except tweepy.TooManyRequests as e:
        print("⚠️  Rate limit exceeded (429 error)")
        print(f"   Error: {e}")
        print("\n   This is expected if you've been testing. Continuing diagnostics...")
    except Exception as e:
        print(f"❌ API Error: {e}")
        return
    
    # 4. Try a search request (this is what your app uses)
    print("\n4️⃣  Testing Tweet Search (RECENT SEARCH ENDPOINT)...")
    print("   Note: This endpoint has strict rate limits on the free tier")
    print("   Free Tier: 10 requests per month (not per 15 min!)")
    print("   Each request can fetch max 10 tweets")
    
    try:
        response = client.search_recent_tweets(
            query="Python",
            max_results=10,
            tweet_fields=["created_at", "public_metrics"]
        )
        
        if response.data:
            print(f"✅ Search successful! Found {len(response.data)} tweets")
            print(f"\n   Sample tweet: {response.data[0].text[:100]}...")
        else:
            print("⚠️  Search returned no results")
            
    except tweepy.TooManyRequests as e:
        print("❌ RATE LIMIT EXCEEDED (429 Error)")
        print("\n📊 DIAGNOSIS:")
        print("   Your Twitter API quota is exhausted!")
        print("\n❓ Why this happens:")
        print("   • Twitter Free Tier (Essential): Only 10 REQUESTS per MONTH")
        print("   • Each search request counts toward this limit")
        print("   • You've likely used all 10 requests already")
        print("\n⏰ When it resets:")
        print("   • Rate limits reset at the beginning of each calendar month")
        print(f"   • Next reset: {datetime.now().replace(day=1, month=datetime.now().month + 1).strftime('%B 1, %Y')}")
        print("\n💡 Solutions:")
        print("   1. WAIT: Wait until next month for quota reset")
        print("   2. UPGRADE: Upgrade to Twitter API Basic ($100/month) or Pro plan")
        print("   3. MOCK DATA: Use the mock data endpoint for testing (see below)")
        
        # Show rate limit headers if available
        if hasattr(e, 'response') and e.response:
            headers = e.response.headers
            if 'x-rate-limit-limit' in headers:
                print(f"\n   Rate Limit: {headers.get('x-rate-limit-limit')}")
                print(f"   Remaining: {headers.get('x-rate-limit-remaining')}")
                reset_time = int(headers.get('x-rate-limit-reset', 0))
                if reset_time:
                    reset_dt = datetime.fromtimestamp(reset_time)
                    print(f"   Resets at: {reset_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    
    except tweepy.Forbidden as e:
        print("❌ FORBIDDEN (403 Error)")
        print(f"   Error: {e}")
        print("\n📊 DIAGNOSIS:")
        print("   Your API access level doesn't allow tweet search!")
        print("\n💡 Solutions:")
        print("   1. Check your Twitter Developer Portal")
        print("   2. Ensure 'Recent search' endpoint is enabled")
        print("   3. You may need to upgrade your access level")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Check Redis rate limit cache
    print("\n5️⃣  Checking Local Rate Limit Cache (Redis)...")
    try:
        redis = await get_redis()
        keys = await redis.keys("rate_limit:*")
        
        if keys:
            print(f"✅ Found {len(keys)} rate limit tracking keys in Redis:")
            for key in keys[:5]:  # Show first 5
                value = await redis.get(key)
                ttl = await redis.ttl(key)
                print(f"   • {key}: {value} requests (expires in {ttl}s)")
        else:
            print("✅ No rate limit blocks in local cache")
            
    except Exception as e:
        print(f"⚠️  Could not check Redis: {e}")
    
    # 6. Configuration summary
    print_section("⚙️  CONFIGURATION SUMMARY")
    print(f"Twitter Search Requests (configured): {settings.TWITTER_SEARCH_REQUESTS_PER_15MIN} per 15 min")
    print(f"Max Results Per Request (configured): {settings.TWITTER_MAX_RESULTS_PER_REQUEST}")
    print("\n⚠️  NOTE: Your configuration shows 450 requests/15min, but Twitter")
    print("   Free Tier (Essential) actually limits to 10 REQUESTS PER MONTH!")
    print("   The configuration needs to be updated to reflect actual limits.")
    
    # 7. Recommendations
    print_section("💡 RECOMMENDATIONS")
    print("\n🎯 For Development & Testing:")
    print("   1. Use MOCK DATA mode to test without using API quota")
    print("   2. Create a mock data generator endpoint")
    print("   3. Test with sample tweets from a JSON file")
    
    print("\n🎯 For Production:")
    print("   1. Upgrade to Twitter API Basic ($100/month)")
    print("      • 10,000 tweets per month")
    print("      • Better rate limits")
    print("   2. Implement aggressive caching")
    print("   3. Use webhooks instead of polling")
    
    print("\n🎯 Immediate Actions:")
    print("   1. Check Twitter Developer Portal for exact quota:")
    print("      → https://developer.twitter.com/en/portal/projects-and-apps")
    print("   2. Clear Redis cache: redis-cli FLUSHDB")
    print("   3. Wait for quota reset OR use mock data")
    
    print_section("✅ DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())

