"""
Test script for updated Apify service (Twitter and Facebook only)
Run this to verify the Apify service is working correctly
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.apify_service import get_apify_service
from app.config import settings


async def test_twitter_search():
    """Test Twitter search functionality"""
    print("\n" + "="*60)
    print("Testing Twitter Search")
    print("="*60)
    
    apify_service = get_apify_service()
    
    result = await apify_service.scrape_twitter_search(
        search_queries=["#Nigeria"],
        max_tweets=5
    )
    
    print(f"Status: {'✅ Success' if result.get('success') else '❌ Failed'}")
    print(f"Platform: {result.get('platform')}")
    print(f"Queries: {result.get('queries')}")
    print(f"Total tweets: {result.get('total_tweets', 0)}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    elif result.get('tweets'):
        print(f"\nSample tweet:")
        tweet = result['tweets'][0]
        print(f"  Author: {tweet.get('author')}")
        print(f"  Content: {tweet.get('content', '')[:100]}...")
        print(f"  Metrics: {tweet.get('metrics')}")
    
    return result


async def test_twitter_profile():
    """Test Twitter profile scraping"""
    print("\n" + "="*60)
    print("Testing Twitter Profile")
    print("="*60)
    
    apify_service = get_apify_service()
    
    result = await apify_service.scrape_twitter_profile(
        username="NigeriaStories",
        tweets_limit=5
    )
    
    print(f"Platform: {result.get('platform')}")
    print(f"Username: {result.get('username')}")
    print(f"Total tweets: {result.get('total_tweets', 0)}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    elif result.get('tweets'):
        print(f"\nSample tweet:")
        tweet = result['tweets'][0]
        print(f"  Author: {tweet.get('author')}")
        print(f"  Content: {tweet.get('content', '')[:100]}...")
    
    return result


async def test_facebook_page():
    """Test Facebook page scraping"""
    print("\n" + "="*60)
    print("Testing Facebook Page")
    print("="*60)
    
    apify_service = get_apify_service()
    
    result = await apify_service.scrape_facebook_page(
        page_url="https://www.facebook.com/legit.ng",
        posts_limit=5
    )
    
    print(f"Platform: {result.get('platform')}")
    print(f"Page URL: {result.get('page_url')}")
    print(f"Total posts: {result.get('total_posts', 0)}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    elif result.get('posts'):
        print(f"\nSample post:")
        post = result['posts'][0]
        print(f"  Page: {post.get('page')}")
        print(f"  Content: {post.get('content', '')[:100]}...")
        print(f"  Metrics: {post.get('metrics')}")
    
    return result


async def test_comprehensive_scraping():
    """Test comprehensive Nigerian social media scraping"""
    print("\n" + "="*60)
    print("Testing Comprehensive Nigerian Scraping")
    print("="*60)
    
    apify_service = get_apify_service()
    
    result = await apify_service.scrape_nigerian_social_media(
        platforms=["twitter", "facebook"],
        items_per_platform=3
    )
    
    print(f"Region: {result.get('region')}")
    print(f"Timestamp: {result.get('timestamp')}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    else:
        platforms = result.get('platforms', {})
        print(f"\nPlatforms scraped: {list(platforms.keys())}")
        
        for platform, data in platforms.items():
            if 'error' in data:
                print(f"  {platform}: ❌ {data['error']}")
            else:
                count = data.get('total_tweets', data.get('total_posts', 0))
                print(f"  {platform}: ✅ {count} items")
    
    return result


async def main():
    """Run all tests"""
    print("\n🧪 Apify Service Test Suite (Twitter & Facebook Only)")
    print("=" * 60)
    
    # Check if API token is configured
    if not settings.APIFY_API_TOKEN:
        print("❌ ERROR: APIFY_API_TOKEN not configured in environment variables")
        print("Please set APIFY_API_TOKEN in your .env file")
        return
    
    print(f"✅ API Token configured")
    print(f"✅ Using actors:")
    print(f"   - Twitter: apidojo/tweet-scraper")
    print(f"   - Facebook: apify/facebook-posts-scraper")
    
    try:
        # Test Twitter search
        await test_twitter_search()
        
        # Test Twitter profile
        # await test_twitter_profile()
        
        # Test Facebook page
        # await test_facebook_page()
        
        # Test comprehensive scraping
        # await test_comprehensive_scraping()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        print("\nNote: Uncomment other tests in main() to run them")
        print("Each test will consume Apify compute units")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
