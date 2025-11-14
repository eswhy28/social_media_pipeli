#!/usr/bin/env python3
"""
Detailed Apify test - actually run actors to see errors
"""

import asyncio
import sys
from app.config import settings
from app.services.apify_service import ApifyService


async def test_facebook_scraping():
    """Test Facebook scraping with Apify"""
    print("=" * 60)
    print("🧪 Testing Facebook Scraping via Apify")
    print("=" * 60)

    apify_service = ApifyService()

    print("\n1️⃣  Testing Facebook page scraping...")
    print("   📘 Target: https://www.facebook.com/legit.ng")
    print("   🔄 Starting scrape...\n")

    try:
        result = await apify_service.scrape_facebook_page(
            page_url="https://www.facebook.com/legit.ng",
            posts_limit=10
        )

        print(f"\n   📊 Results:")
        print(f"      • Platform: {result.get('platform')}")
        print(f"      • Total posts: {result.get('total_posts', 0)}")
        print(f"      • Status: {result.get('status', 'unknown')}")

        if 'error' in result:
            print(f"      • ❌ Error: {result['error']}")
            return False

        if result.get('posts'):
            print(f"      • ✅ Successfully scraped {len(result['posts'])} posts")
            # Show first post
            first_post = result['posts'][0]
            print(f"\n   📝 Sample post:")
            print(f"      • Content: {first_post.get('content', 'N/A')[:100]}...")
            print(f"      • Likes: {first_post.get('metrics', {}).get('likes', 0)}")
            return True
        else:
            print(f"      • ⚠️  No posts returned")
            return False

    except Exception as e:
        print(f"\n   ❌ Error during Facebook scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_twitter_scraping():
    """Test Twitter scraping with Apify"""
    print("\n" + "=" * 60)
    print("🧪 Testing Twitter Scraping via Apify")
    print("=" * 60)

    apify_service = ApifyService()

    print("\n2️⃣  Testing Twitter profile scraping...")
    print("   🐦 Target: @NigeriaStories")
    print("   🔄 Starting scrape...\n")

    try:
        result = await apify_service.scrape_twitter_profile(
            username="NigeriaStories",
            tweets_limit=10
        )

        print(f"\n   📊 Results:")
        print(f"      • Platform: {result.get('platform')}")
        print(f"      • Total tweets: {result.get('total_tweets', 0)}")
        print(f"      • Username: {result.get('username')}")

        if 'error' in result:
            print(f"      • ❌ Error: {result['error']}")
            return False

        if result.get('tweets'):
            print(f"      • ✅ Successfully scraped {len(result['tweets'])} tweets")
            # Show first tweet
            first_tweet = result['tweets'][0]
            print(f"\n   📝 Sample tweet:")
            print(f"      • Content: {first_tweet.get('content', 'N/A')[:100]}...")
            print(f"      • Likes: {first_tweet.get('metrics', {}).get('likes', 0)}")
            return True
        else:
            print(f"      • ⚠️  No tweets returned")
            return False

    except Exception as e:
        print(f"\n   ❌ Error during Twitter scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("\n🚀 Starting Detailed Apify Scraping Tests...\n")

    # Test Facebook
    fb_ok = await test_facebook_scraping()
    await asyncio.sleep(3)

    # Test Twitter
    tw_ok = await test_twitter_scraping()

    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"   Facebook: {'✅ PASSED' if fb_ok else '❌ FAILED'}")
    print(f"   Twitter: {'✅ PASSED' if tw_ok else '❌ FAILED'}")
    print("=" * 60)

    if fb_ok and tw_ok:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed - see details above")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)