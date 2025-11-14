"""
Comprehensive Test Suite for Social Media Pipeline
Tests all data collection libraries and functionalities
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

# Test results storage
test_results = {
    "timestamp": datetime.utcnow().isoformat(),
    "tests": []
}

def log_test(name: str, status: str, details: str = "", error: str = ""):
    """Log test result"""
    result = {
        "test": name,
        "status": status,
        "details": details,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }
    test_results["tests"].append(result)

    # Print to console
    status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"\n{status_emoji} {name}: {status}")
    if details:
        print(f"   Details: {details}")
    if error:
        print(f"   Error: {error}")


async def test_database_connection():
    """Test PostgreSQL database connection"""
    try:
        from app.database import AsyncSessionLocal, engine
        from sqlalchemy import text

        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT 1"))
            await db.execute(text("SELECT current_database()"))
            db_name = (await db.execute(text("SELECT current_database()"))).scalar()

        log_test(
            "Database Connection",
            "PASS",
            f"Connected to PostgreSQL database: {db_name}"
        )
        return True
    except Exception as e:
        log_test("Database Connection", "FAIL", error=str(e))
        return False


async def test_google_trends():
    """Test Google Trends service"""
    try:
        from app.services.google_trends_service import get_google_trends_service

        service = get_google_trends_service()
        trends = await service.get_trending_searches("NG", limit=5)

        if trends and len(trends) > 0:
            log_test(
                "Google Trends Service",
                "PASS",
                f"Retrieved {len(trends)} trending topics. Sample: {trends[0]['title'][:50]}"
            )
            return True
        else:
            log_test(
                "Google Trends Service",
                "WARN",
                "Service connected but no trends returned"
            )
            return False
    except Exception as e:
        log_test("Google Trends Service", "FAIL", error=str(e))
        return False


async def test_tiktok_service():
    """Test TikTok-Api library integration"""
    try:
        from app.services.tiktok_service import get_tiktok_service

        service = get_tiktok_service()

        # Test with a popular Nigerian hashtag
        videos = await service.search_hashtag("nigeria", count=5)

        if videos and len(videos) > 0:
            log_test(
                "TikTok-Api Service",
                "PASS",
                f"Retrieved {len(videos)} videos from hashtag #nigeria"
            )
            return True
        else:
            log_test(
                "TikTok-Api Service",
                "WARN",
                "Service initialized but no videos returned (may be rate limited or access restricted)"
            )
            return False
    except Exception as e:
        error_msg = str(e)
        # TikTok API often has authentication/access issues
        if "playwright" in error_msg.lower() or "browser" in error_msg.lower():
            log_test(
                "TikTok-Api Service",
                "WARN",
                error=f"Browser automation required: {error_msg[:100]}"
            )
        else:
            log_test("TikTok-Api Service", "FAIL", error=error_msg)
        return False


async def test_facebook_service():
    """Test facebook-scraper library integration"""
    try:
        from app.services.facebook_service import get_facebook_service

        service = get_facebook_service()

        # Test with a popular Nigerian news page
        posts = await service.scrape_page_posts("legit.ng", pages=1, timeout=20)

        if posts and len(posts) > 0:
            log_test(
                "Facebook Scraper Service",
                "PASS",
                f"Retrieved {len(posts)} posts from legit.ng page"
            )
            return True
        else:
            log_test(
                "Facebook Scraper Service",
                "WARN",
                "Service initialized but no posts returned (may be rate limited or blocked)"
            )
            return False
    except Exception as e:
        error_msg = str(e)
        log_test("Facebook Scraper Service", "FAIL", error=error_msg)
        return False


async def test_apify_service():
    """Test Apify service for Twitter data"""
    try:
        from app.services.apify_service import get_apify_service

        service = get_apify_service()

        # Test with a simple search query
        result = await service.scrape_twitter_search(
            search_queries=["nigeria"],
            max_tweets=5
        )

        if result.get("success") and result.get("tweets"):
            log_test(
                "Apify Twitter Service",
                "PASS",
                f"Retrieved {len(result['tweets'])} tweets about 'nigeria'"
            )
            return True
        else:
            log_test(
                "Apify Twitter Service",
                "WARN",
                f"API call made but returned: {result.get('error', 'No tweets')}"
            )
            return False
    except Exception as e:
        error_msg = str(e)
        log_test("Apify Twitter Service", "FAIL", error=error_msg)
        return False


async def test_hashtag_discovery():
    """Test Hashtag Discovery service"""
    try:
        from app.database import AsyncSessionLocal
        from app.services.hashtag_discovery_service import get_hashtag_discovery_service

        async with AsyncSessionLocal() as db:
            service = get_hashtag_discovery_service(db)

            # Test getting trending hashtags
            hashtags = await service.discover_nigerian_hashtags(
                include_google_trends=True,
                include_collected=True,
                limit=10
            )

            if hashtags and len(hashtags) > 0:
                log_test(
                    "Hashtag Discovery Service",
                    "PASS",
                    f"Discovered {len(hashtags)} trending hashtags. Top 3: {', '.join(hashtags[:3])}"
                )
                return True
            else:
                log_test(
                    "Hashtag Discovery Service",
                    "WARN",
                    "Service initialized but no hashtags discovered"
                )
                return False
    except Exception as e:
        log_test("Hashtag Discovery Service", "FAIL", error=str(e))
        return False


async def test_redis_connection():
    """Test Redis connection for Celery"""
    try:
        from app.redis_client import get_redis

        redis = await get_redis()

        # Test set and get
        await redis.set("test_key", "test_value", ex=10)
        value = await redis.get("test_key")

        if value == "test_value":
            log_test(
                "Redis Connection",
                "PASS",
                "Redis connected and operations working"
            )
            return True
        else:
            log_test(
                "Redis Connection",
                "FAIL",
                error="Redis connected but operations not working correctly"
            )
            return False
    except Exception as e:
        log_test("Redis Connection", "FAIL", error=str(e))
        return False


async def test_api_endpoints():
    """Test main API endpoints"""
    try:
        import httpx

        base_url = "http://localhost:8000"

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test health endpoint
            try:
                response = await client.get(f"{base_url}/health")
                health_status = "available" if response.status_code == 200 else "unavailable"
            except:
                health_status = "not running"

            # Test hashtag trending endpoint (if API is running)
            if health_status == "available":
                try:
                    response = await client.get(
                        f"{base_url}/api/v1/social-media/hashtags/trending",
                        params={"limit": 5}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        hashtags = data.get("data", {}).get("trending_hashtags", [])
                        log_test(
                            "API Endpoints",
                            "PASS",
                            f"API is running. Trending endpoint returned {len(hashtags)} hashtags"
                        )
                        return True
                    else:
                        log_test(
                            "API Endpoints",
                            "WARN",
                            f"API running but endpoint returned status {response.status_code}"
                        )
                        return False
                except Exception as e:
                    log_test(
                        "API Endpoints",
                        "WARN",
                        f"API running but endpoint test failed: {str(e)[:100]}"
                    )
                    return False
            else:
                log_test(
                    "API Endpoints",
                    "SKIP",
                    "API server not running. Start with: uvicorn app.main:app --reload"
                )
                return None
    except Exception as e:
        log_test("API Endpoints", "FAIL", error=str(e))
        return False


async def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 70)
    print("COMPREHENSIVE FUNCTIONALITY TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.utcnow().isoformat()}")
    print("=" * 70)

    # Run tests
    await test_database_connection()
    await asyncio.sleep(1)

    await test_redis_connection()
    await asyncio.sleep(1)

    await test_google_trends()
    await asyncio.sleep(2)

    await test_tiktok_service()
    await asyncio.sleep(2)

    await test_facebook_service()
    await asyncio.sleep(2)

    await test_apify_service()
    await asyncio.sleep(2)

    await test_hashtag_discovery()
    await asyncio.sleep(1)

    await test_api_endpoints()

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total = len(test_results["tests"])
    passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
    failed = sum(1 for t in test_results["tests"] if t["status"] == "FAIL")
    warned = sum(1 for t in test_results["tests"] if t["status"] == "WARN")
    skipped = sum(1 for t in test_results["tests"] if t["status"] == "SKIP")

    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warned}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"\nSuccess Rate: {(passed/total*100):.1f}%")
    print("=" * 70)

    # Save results to file
    import json
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print(f"\nDetailed results saved to: test_results.json")

    return passed, failed, warned


if __name__ == "__main__":
    asyncio.run(run_all_tests())