#!/usr/bin/env python3
"""
Quick test script to verify Apify service is working correctly
"""

import asyncio
import sys
from app.config import settings
from app.services.apify_service import ApifyService


async def test_apify_connection():
    """Test Apify service initialization and connection"""
    print("=" * 60)
    print("🧪 Testing Apify Service Configuration")
    print("=" * 60)

    # Check if API token is configured
    print("\n1️⃣  Checking API Token Configuration...")
    if not settings.APIFY_API_TOKEN:
        print("   ❌ APIFY_API_TOKEN is not set in .env file!")
        print("   💡 Please add your Apify token to .env file:")
        print("   APIFY_API_TOKEN=your_apify_token_here")
        return False

    print(f"   ✅ API Token found: {settings.APIFY_API_TOKEN[:15]}...")

    # Initialize Apify service
    print("\n2️⃣  Initializing Apify Service...")
    try:
        apify_service = ApifyService()
        if apify_service.client is None:
            print("   ❌ Apify client failed to initialize!")
            return False
        print("   ✅ Apify service initialized successfully")
    except Exception as e:
        print(f"   ❌ Error initializing Apify service: {e}")
        return False

    # Test API connection with a simple actor call
    print("\n3️⃣  Testing API Connection...")
    print("   📡 Attempting to list available actors...")

    try:
        # Try to list actors to verify API connection
        # Using the synchronous client for testing
        from apify_client import ApifyClient
        test_client = ApifyClient(settings.APIFY_API_TOKEN)

        # Get user info to verify token
        user = test_client.user().get()

        if user:
            print(f"   ✅ Successfully connected to Apify!")
            print(f"   👤 User: {user.get('username', 'Unknown')}")
            print(f"   📧 Email: {user.get('email', 'Unknown')}")

            # Check usage info if available
            if 'usage' in user:
                usage = user['usage']
                print(f"\n   📊 Account Usage:")
                if 'datasetReads' in usage:
                    print(f"      • Dataset Reads: {usage['datasetReads']}")
                if 'storageBytes' in usage:
                    storage_mb = usage['storageBytes'] / (1024 * 1024)
                    print(f"      • Storage Used: {storage_mb:.2f} MB")

            return True
        else:
            print("   ❌ Could not retrieve user information")
            return False

    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        print(f"\n   💡 Troubleshooting tips:")
        print(f"      1. Verify your token is correct")
        print(f"      2. Check your internet connection")
        print(f"      3. Visit https://console.apify.com/account/integrations")
        return False


async def test_instagram_scraper_availability():
    """Test if Instagram scraper actor is available"""
    print("\n4️⃣  Checking Instagram Scraper Actor...")

    try:
        from apify_client import ApifyClient
        client = ApifyClient(settings.APIFY_API_TOKEN)

        # Common Instagram scraper actors
        actor_ids = [
            "apify/instagram-scraper",
            "apify/instagram-profile-scraper"
        ]

        for actor_id in actor_ids:
            try:
                actor = client.actor(actor_id).get()
                if actor:
                    print(f"   ✅ Found actor: {actor_id}")
                    print(f"      Name: {actor.get('name', 'Unknown')}")
                    print(f"      Title: {actor.get('title', 'Unknown')}")
                    return True
            except:
                continue

        print("   ⚠️  Instagram scrapers not found (this is okay)")
        print("   💡 You can still use Apify for other platforms")
        return True

    except Exception as e:
        print(f"   ⚠️  Could not check actors: {e}")
        return True  # Non-critical


async def main():
    """Main test function"""
    print("\n🚀 Starting Apify Service Tests...\n")

    # Run tests
    connection_ok = await test_apify_connection()

    if connection_ok:
        await test_instagram_scraper_availability()

        print("\n" + "=" * 60)
        print("✅ All Apify Tests Completed Successfully!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("   1. Your Apify service is ready to use")
        print("   2. Start the application: uvicorn app.main:app --reload")
        print("   3. Test the API endpoints at: http://localhost:8000/docs")
        print("\n🎯 Available Apify Endpoints:")
        print("   • POST /api/v1/social-media/apify/scrape")
        print("   • GET  /api/v1/social-media/apify/comprehensive")
        print()
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Apify Tests Failed")
        print("=" * 60)
        print("\n🔧 Please fix the issues above and try again\n")
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
        sys.exit(1)