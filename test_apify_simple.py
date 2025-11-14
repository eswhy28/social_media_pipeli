#!/usr/bin/env python3
"""
Simple Apify test script - minimal dependencies
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_apify():
    """Test Apify service configuration"""
    print("=" * 60)
    print("🧪 Testing Apify Service Configuration")
    print("=" * 60)

    # Check if API token is configured
    print("\n1️⃣  Checking API Token Configuration...")
    apify_token = os.getenv('APIFY_API_TOKEN')

    if not apify_token:
        print("   ❌ APIFY_API_TOKEN is not set in .env file!")
        print("   💡 Please add your Apify token to .env file:")
        print("   APIFY_API_TOKEN=your_apify_token_here")
        return False

    print(f"   ✅ API Token found: {apify_token[:15]}...")

    # Test Apify client
    print("\n2️⃣  Initializing Apify Client...")
    try:
        from apify_client import ApifyClient
        client = ApifyClient(apify_token)

        print("   ✅ Apify client initialized successfully")
    except ImportError:
        print("   ❌ apify-client not installed!")
        print("   💡 Install with: pip install apify-client")
        return False
    except Exception as e:
        print(f"   ❌ Error initializing client: {e}")
        return False

    # Test API connection
    print("\n3️⃣  Testing API Connection...")
    print("   📡 Retrieving user information...")

    try:
        user = client.user().get()

        if user:
            print(f"   ✅ Successfully connected to Apify!")
            print(f"\n   📋 Account Details:")
            print(f"      • User ID: {user.get('id', 'Unknown')}")
            print(f"      • Username: {user.get('username', 'Unknown')}")
            print(f"      • Email: {user.get('email', 'Unknown')}")

            # Check plan info
            if 'plan' in user:
                plan = user['plan']
                print(f"\n   💎 Plan Information:")
                print(f"      • Plan: {plan.get('name', 'Unknown')}")
                if 'monthlyActorComputeUnits' in plan:
                    print(f"      • Monthly Compute Units: {plan['monthlyActorComputeUnits']}")

            # Check usage if available
            if 'usage' in user:
                usage = user['usage']
                print(f"\n   📊 Current Usage:")
                if 'actorComputeUnits' in usage:
                    print(f"      • Compute Units Used: {usage['actorComputeUnits']}")
                if 'dataRetentionDays' in usage:
                    print(f"      • Data Retention: {usage['dataRetentionDays']} days")

            return True
        else:
            print("   ❌ Could not retrieve user information")
            return False

    except Exception as e:
        print(f"   ❌ API connection failed: {str(e)}")
        print(f"\n   💡 Troubleshooting tips:")
        print(f"      1. Verify your token is correct in .env")
        print(f"      2. Check your internet connection")
        print(f"      3. Generate new token at: https://console.apify.com/account/integrations")
        return False


def test_actor_availability():
    """Test if common actors are accessible"""
    print("\n4️⃣  Checking Available Actors...")

    apify_token = os.getenv('APIFY_API_TOKEN')
    if not apify_token:
        return False

    try:
        from apify_client import ApifyClient
        client = ApifyClient(apify_token)

        # Test accessing a public actor
        popular_actors = [
            ("apify/instagram-scraper", "Instagram Scraper"),
            ("apify/web-scraper", "Web Scraper"),
            ("apify/google-search-scraper", "Google Search Scraper"),
        ]

        found_any = False
        for actor_id, name in popular_actors:
            try:
                actor = client.actor(actor_id).get()
                if actor:
                    print(f"   ✅ Found: {name}")
                    found_any = True
                    break
            except:
                continue

        if found_any:
            print(f"\n   🎯 You can use Apify actors in your application!")
        else:
            print(f"\n   ⚠️  No public actors found (this is okay)")
            print(f"   💡 You may need to run actors you own or have access to")

        return True

    except Exception as e:
        print(f"   ⚠️  Could not check actors: {e}")
        return True  # Non-critical


def main():
    """Main test function"""
    print("\n🚀 Starting Apify Service Tests...\n")

    # Run tests
    connection_ok = test_apify()

    if connection_ok:
        test_actor_availability()

        print("\n" + "=" * 60)
        print("✅ Apify Configuration Test Completed Successfully!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("   1. Your Apify service is ready to use")
        print("   2. Start the application:")
        print("      uvicorn app.main:app --reload")
        print("   3. Test the API at: http://localhost:8000/docs")
        print("\n🎯 Available Apify Endpoints:")
        print("   • POST /api/v1/social-media/apify/scrape")
        print("   • GET  /api/v1/social-media/apify/comprehensive")
        print("\n💡 Example Usage:")
        print("   curl -X POST http://localhost:8000/api/v1/social-media/apify/scrape \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"platform\":\"instagram\",\"target\":\"nasa\",\"limit\":10}'")
        print()
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Apify Configuration Test Failed")
        print("=" * 60)
        print("\n🔧 Please fix the issues above and try again\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)