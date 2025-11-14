#!/usr/bin/env python3
"""
Quick test to verify Google Trends collection and database storage
"""

import asyncio
import httpx
import sys
sys.path.insert(0, '.')

from app.database import AsyncSessionLocal
from sqlalchemy import text

async def test_google_trends():
    """Test Google Trends data collection"""
    print("=" * 60)
    print("🧪 Testing Google Trends Collection & Database Storage")
    print("=" * 60)

    # Test 1: API endpoint
    print("\n1️⃣ Testing Google Trends API endpoint...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/social-media/trends/analyze",
                json={
                    "keywords": ["Tinubu", "Nigeria"],
                    "timeframe": "today 3-m",
                    "include_related": True,
                    "include_regional": True
                }
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ API endpoint working")

                result = data.get("data", {})
                interest = result.get("interest_over_time", [])
                regional = result.get("regional_interest", {})
                related = result.get("related_queries", {})

                print(f"   📊 Interest over time: {len(interest)} data points")
                print(f"   📊 Regional data: {len(regional)} regions")
                print(f"   📊 Related queries: {len(related)} keywords")

                if len(interest) > 0:
                    print(f"\n   Sample data point: {interest[0]}")

            else:
                print(f"   ❌ API failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Test 2: Check database
    print("\n2️⃣ Checking database storage...")

    try:
        async with AsyncSessionLocal() as db:
            # Count records
            result = await db.execute(text("SELECT COUNT(*) FROM google_trends_data"))
            count = result.scalar()

            print(f"   📊 Total records in database: {count}")

            if count > 0:
                # Get recent records
                result = await db.execute(
                    text("SELECT keyword, trend_date, interest_value FROM google_trends_data ORDER BY created_at DESC LIMIT 5")
                )
                records = result.fetchall()

                print(f"\n   📝 Recent records:")
                for record in records:
                    print(f"      • {record[0]}: {record[2]} ({record[1]})")

                return True
            else:
                print("   ⚠️ No data in database yet")
                print("   💡 Data should be stored automatically by the API")
                return False

    except Exception as e:
        print(f"   ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("\n🚀 Starting Google Trends Test...\n")

    success = await test_google_trends()

    print("\n" + "=" * 60)
    if success:
        print("✅ Test PASSED - Data is being collected and stored")
    else:
        print("❌ Test FAILED - See errors above")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)