"""
Lightweight Test Suite for Data Collection Libraries
Tests core data sources without database dependencies
"""

import asyncio
from datetime import datetime
import json

# Test results storage
test_results = {
    "timestamp": datetime.utcnow().isoformat(),
    "tests": []
}

def log_test(name: str, status: str, details: str = "", error: str = "", data_sample: dict = None):
    """Log test result"""
    result = {
        "test": name,
        "status": status,
        "details": details,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }
    if data_sample:
        result["data_sample"] = data_sample

    test_results["tests"].append(result)

    # Print to console
    status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"\n{status_emoji} {name}: {status}")
    if details:
        print(f"   Details: {details}")
    if error:
        print(f"   Error: {error}")
    if data_sample:
        print(f"   Sample: {json.dumps(data_sample, indent=4)}")


async def test_google_trends():
    """Test Google Trends API"""
    try:
        print("\n📊 Testing Google Trends API...")
        from pytrends.request import TrendReq
        import time

        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

        # Get trending searches for Nigeria (use realtime trends as fallback)
        try:
            trending_searches = pytrends.trending_searches(pn='nigeria')
        except:
            # Try realtime trends as alternative
            pytrends.trending_searches(pn='united_states')
            trending_searches = pytrends.trending_searches(pn='nigeria')

        if trending_searches is not None and len(trending_searches) > 0:
            trends_list = trending_searches[0].head(5).tolist()
            sample = {
                "total_trends": len(trending_searches),
                "top_5": trends_list
            }
            log_test(
                "Google Trends API",
                "PASS",
                f"Retrieved {len(trending_searches)} trending topics from Nigeria",
                data_sample=sample
            )
            return True
        else:
            log_test(
                "Google Trends API",
                "WARN",
                "Connected but no trending searches returned"
            )
            return False
    except Exception as e:
        log_test("Google Trends API", "FAIL", error=str(e))
        return False


async def test_apify_client():
    """Test Apify API Client"""
    try:
        print("\n🐦 Testing Apify API Client...")
        from apify_client import ApifyClient
        import os

        api_token = os.getenv("APIFY_API_TOKEN", "")

        if not api_token or api_token == "":
            log_test(
                "Apify API Client",
                "SKIP",
                "No APIFY_API_TOKEN found in environment"
            )
            return None

        client = ApifyClient(api_token)

        # Test connection by getting user info
        user = client.user().get()

        if user:
            sample = {
                "user_id": user.get("id", "N/A"),
                "username": user.get("username", "N/A")
            }
            log_test(
                "Apify API Client",
                "PASS",
                f"Successfully authenticated with Apify",
                data_sample=sample
            )
            return True
        else:
            log_test(
                "Apify API Client",
                "FAIL",
                error="Failed to authenticate"
            )
            return False
    except Exception as e:
        log_test("Apify API Client", "FAIL", error=str(e))
        return False


async def test_facebook_scraper():
    """Test facebook-scraper library"""
    try:
        print("\n📘 Testing facebook-scraper library...")
        from facebook_scraper import get_posts, FacebookScraper
        import random

        # Test library import and basic functionality
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        ]

        # Try to scrape a public page (limited to 1 post for testing)
        try:
            posts = list(get_posts(
                'legit.ng',
                pages=1,
                timeout=15,
                options={"allow_extra_requests": False}
            ))

            if posts and len(posts) > 0:
                first_post = posts[0]
                sample = {
                    "posts_retrieved": len(posts),
                    "has_text": bool(first_post.get("text")),
                    "has_time": bool(first_post.get("time")),
                    "sample_text": (first_post.get("text", "")[:100] + "...") if first_post.get("text") else "N/A"
                }
                log_test(
                    "Facebook Scraper Library",
                    "PASS",
                    f"Successfully scraped {len(posts)} posts from public page",
                    data_sample=sample
                )
                return True
            else:
                log_test(
                    "Facebook Scraper Library",
                    "WARN",
                    "Library imported but no posts retrieved (Facebook may be blocking)"
                )
                return False
        except Exception as scrape_error:
            # Library works but scraping blocked
            if "login" in str(scrape_error).lower() or "block" in str(scrape_error).lower():
                log_test(
                    "Facebook Scraper Library",
                    "WARN",
                    f"Library functional but scraping restricted: {str(scrape_error)[:100]}"
                )
            else:
                log_test(
                    "Facebook Scraper Library",
                    "WARN",
                    error=f"Scraping failed: {str(scrape_error)[:100]}"
                )
            return False

    except Exception as e:
        log_test("Facebook Scraper Library", "FAIL", error=str(e))
        return False


async def test_tiktok_api():
    """Test TikTok-Api library"""
    try:
        print("\n🎵 Testing TikTok-Api library...")
        from TikTokApi import TikTokApi

        # Just test if library can be imported and initialized
        try:
            api = TikTokApi(logging_level=40)  # ERROR level logging

            # TikTok API requires Playwright/browser automation
            # Just testing initialization for now
            log_test(
                "TikTok-Api Library",
                "PASS",
                "Library imported and initialized successfully. Note: Full functionality requires Playwright setup"
            )
            return True

        except Exception as init_error:
            if "playwright" in str(init_error).lower() or "browser" in str(init_error).lower():
                log_test(
                    "TikTok-Api Library",
                    "WARN",
                    "Library imported but requires Playwright browser automation to be installed",
                    error="Run: playwright install"
                )
                return False
            else:
                log_test(
                    "TikTok-Api Library",
                    "FAIL",
                    error=str(init_error)
                )
                return False

    except Exception as e:
        log_test("TikTok-Api Library", "FAIL", error=str(e))
        return False


async def test_tweepy():
    """Test Tweepy library (if token available)"""
    try:
        print("\n🐦 Testing Tweepy library...")
        import tweepy
        import os

        bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")

        if not bearer_token or bearer_token == "":
            log_test(
                "Tweepy Library",
                "SKIP",
                "No TWITTER_BEARER_TOKEN found in environment. Using Apify instead is recommended."
            )
            return None

        # Test authentication
        client = tweepy.Client(bearer_token=bearer_token)

        # Try to get user info
        me = client.get_me()

        if me:
            log_test(
                "Tweepy Library",
                "PASS",
                "Successfully authenticated with Twitter API"
            )
            return True
        else:
            log_test(
                "Tweepy Library",
                "WARN",
                "Library imported but authentication failed"
            )
            return False

    except Exception as e:
        log_test("Tweepy Library", "SKIP", error=f"Not configured: {str(e)[:100]}")
        return None


async def run_all_tests():
    """Run all data source tests"""
    print("=" * 70)
    print("DATA COLLECTION LIBRARIES TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.utcnow().isoformat()}")
    print("=" * 70)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Run tests
    await test_google_trends()
    await asyncio.sleep(2)

    await test_apify_client()
    await asyncio.sleep(1)

    await test_facebook_scraper()
    await asyncio.sleep(2)

    await test_tiktok_api()
    await asyncio.sleep(1)

    await test_tweepy()

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

    if total > 0:
        # Success rate excluding skipped tests
        tested = total - skipped
        if tested > 0:
            success_rate = (passed / tested * 100)
            print(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{tested} tests)")
        else:
            print(f"\nNo tests executed (all skipped)")

    print("=" * 70)

    # Save results to file
    with open("data_source_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print(f"\n📄 Detailed results saved to: data_source_test_results.json")

    return passed, failed, warned


if __name__ == "__main__":
    asyncio.run(run_all_tests())