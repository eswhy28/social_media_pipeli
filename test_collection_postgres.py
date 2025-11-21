#!/usr/bin/env python3
"""
Test data collection with PostgreSQL
"""

import asyncio
import os
import sys

# Force PostgreSQL
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline'

sys.path.insert(0, '.')

from app.services.google_trends_service import get_google_trends_service
from app.services.apify_service import get_apify_service
from app.database import AsyncSessionLocal
from app.services.database_storage_service import get_storage_service
from sqlalchemy import text


async def test_google_trends():
    """Test Google Trends collection"""
    print("=" * 70)
    print("Testing Google Trends Collection with PostgreSQL")
    print("=" * 70)

    trends_service = get_google_trends_service()

    # Test 1: Get trending searches for Nigeria
    print("\n1. Fetching trending searches for Nigeria...")
    try:
        trending = await trends_service.get_trending_searches("NG")
        print(f"   Found {len(trending)} trending searches")
        if trending:
            print(f"   Sample: {trending[0]}")
    except Exception as e:
        print(f"   Error: {e}")
        trending = []

    # Test 2: Analyze specific keywords
    print("\n2. Analyzing Nigerian keywords...")
    try:
        analysis = await trends_service.get_comprehensive_analysis(
            keywords=["Tinubu", "Nigeria", "Lagos"],
            include_related=True,
            include_regional=True
        )

        interest = analysis.get("interest_over_time", [])
        regional = analysis.get("regional_interest", {})
        related = analysis.get("related_queries", {})

        print(f"   Interest over time: {len(interest)} data points")
        print(f"   Regional data: {len(regional)} regions")
        print(f"   Related queries: {len(related)} keywords")

        # Test 3: Store in PostgreSQL
        print("\n3. Storing in PostgreSQL...")
        async with AsyncSessionLocal() as db:
            storage_service = get_storage_service(db)

            # Store trends data
            if interest:
                stored = await storage_service.store_google_trends(
                    trends_data=interest,
                    trend_type="interest_over_time",
                    source_name="google_trends_ng"
                )
                print(f"   ✅ Stored {stored} trend data points")

            # Check database
            result = await db.execute(text("SELECT COUNT(*) FROM google_trends_data"))
            count = result.scalar()
            print(f"   📊 Total records in database: {count}")

            if count > 0:
                # Get recent records
                result = await db.execute(
                    text("""
                        SELECT keyword, trend_date, interest_value
                        FROM google_trends_data
                        ORDER BY created_at DESC
                        LIMIT 5
                    """)
                )
                records = result.fetchall()
                print(f"\n   Recent records:")
                for r in records:
                    print(f"      • {r[0]}: {r[2]} ({r[1]})")

                return True
            else:
                print("   ⚠️ No data stored in database")
                return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_apify_twitter():
    """Test Twitter collection with new Apify token"""
    print("\n" + "=" * 70)
    print("Testing Twitter Collection with Apify (Paid Plan)")
    print("=" * 70)

    apify_service = get_apify_service()

    print("\n1. Testing Twitter profile scraping...")
    try:
        result = await apify_service.scrape_twitter_profile(
            username="NigeriaStories",
            tweets_limit=10
        )

        tweets = result.get('tweets', [])
        print(f"   ✅ Scraped {len(tweets)} tweets")

        if tweets and len(tweets) > 0:
            first_tweet = tweets[0]
            content = first_tweet.get('content', '')
            if content:
                print(f"   📝 First tweet: {content[:100]}...")
                print(f"   ✅ Twitter scraping working (has content)")

                # Store in database
                async with AsyncSessionLocal() as db:
                    storage_service = get_storage_service(db)
                    # Store as apify data
                    await storage_service.store_apify_scraped_data(
                        platform="twitter",
                        data_json=tweets,
                        source_name="@NigeriaStories"
                    )
                    print(f"   ✅ Stored in database")

                return True
            else:
                print(f"   ⚠️ Tweets returned but content is empty (demo mode?)")
                return False
        else:
            print(f"   ⚠️ No tweets returned")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_apify_facebook():
    """Test Facebook collection with new Apify token"""
    print("\n" + "=" * 70)
    print("Testing Facebook Collection with Apify (Paid Plan)")
    print("=" * 70)

    apify_service = get_apify_service()

    print("\n1. Testing Facebook page scraping...")
    try:
        result = await apify_service.scrape_facebook_page(
            page_url="https://www.facebook.com/legit.ng",
            posts_limit=10
        )

        posts = result.get('posts', [])
        print(f"   ✅ Scraped {len(posts)} posts")

        if posts and len(posts) > 0:
            first_post = posts[0]
            content = first_post.get('content', '')
            if content:
                print(f"   📝 First post: {content[:100]}...")
                print(f"   ✅ Facebook scraping working (has content)")

                # Store in database
                async with AsyncSessionLocal() as db:
                    storage_service = get_storage_service(db)
                    stored = await storage_service.store_facebook_posts(
                        posts=posts,
                        source_name="legit.ng"
                    )
                    print(f"   ✅ Stored {stored} posts in database")

                return True
            else:
                print(f"   ⚠️ Posts returned but content is empty")
                return False
        else:
            print(f"   ⚠️ No posts returned")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("\n🚀 Starting Data Collection Test with PostgreSQL\n")

    # Test Google Trends
    trends_ok = await test_google_trends()

    # Test Apify Twitter
    twitter_ok = await test_apify_twitter()

    # Test Apify Facebook
    facebook_ok = await test_apify_facebook()

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"   Google Trends: {'✅ PASSED' if trends_ok else '❌ FAILED'}")
    print(f"   Twitter (Apify): {'✅ PASSED' if twitter_ok else '❌ FAILED'}")
    print(f"   Facebook (Apify): {'✅ PASSED' if facebook_ok else '❌ FAILED'}")
    print("=" * 70)

    if trends_ok or twitter_ok or facebook_ok:
        print("\n✅ At least one source is working and data is in PostgreSQL!")
        return 0
    else:
        print("\n❌ All tests failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)