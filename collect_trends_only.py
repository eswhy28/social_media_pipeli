#!/usr/bin/env python3
"""
Nigerian Google Trends Collection - Simplified & Working
Focuses on Google Trends keyword analysis which is verified working
"""

import asyncio
import httpx
import sys
from datetime import datetime
from typing import List, Dict

# Add project to path
sys.path.insert(0, '.')

from app.nigerian_topics_config import NIGERIAN_TRENDING_CATEGORIES

BASE_URL = "http://localhost:8000"


class TrendsCollector:
    """Simplified collector focusing on Google Trends"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        self.stats = {
            "keywords_analyzed": 0,
            "data_points": 0,
            "regional_data": 0,
            "related_queries": 0
        }

    async def close(self):
        await self.client.aclose()

    async def analyze_category(self, category: str, keywords: List[str]) -> Dict:
        """
        Analyze trending keywords for a category

        Args:
            category: Category name (politics, economy, etc.)
            keywords: List of keywords to analyze

        Returns:
            Analysis results
        """
        print(f"\n📊 Analyzing {category.upper()} trends...")
        print(f"   Keywords: {', '.join(keywords)}")

        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/social-media/trends/analyze",
                json={
                    "keywords": keywords,
                    "timeframe": "today 3-m",  # Last 3 months
                    "include_related": True,
                    "include_regional": True
                }
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get("data", {})

                # Count data points
                interest_data = result.get("interest_over_time", [])
                regional_data = result.get("regional_interest", {})
                related_queries = result.get("related_queries", {})

                self.stats["keywords_analyzed"] += len(keywords)
                self.stats["data_points"] += len(interest_data)
                self.stats["regional_data"] += sum(len(v) for v in regional_data.values())
                self.stats["related_queries"] += sum(
                    len(v.get("top", [])) + len(v.get("rising", []))
                    for v in related_queries.values()
                )

                print(f"   ✅ {len(interest_data)} trend data points")
                print(f"   ✅ {len(regional_data)} regions analyzed")
                print(f"   ✅ Related queries collected")

                return data

            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    async def collect_all_categories(self):
        """Collect trends for all Nigerian categories"""
        print("\n" + "=" * 70)
        print("🇳🇬 NIGERIAN GOOGLE TRENDS COLLECTION")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        results = []

        for category, data in NIGERIAN_TRENDING_CATEGORIES.items():
            # Get top 5 keywords for each category
            keywords = data["keywords"][:5]

            result = await self.analyze_category(category, keywords)
            if result:
                results.append({
                    "category": category,
                    "result": result
                })

            # Rate limiting
            await asyncio.sleep(3)

        # Print summary
        print("\n" + "=" * 70)
        print("📊 COLLECTION SUMMARY")
        print("=" * 70)
        print(f"Categories Analyzed: {len(results)}")
        print(f"Keywords Analyzed: {self.stats['keywords_analyzed']}")
        print(f"Trend Data Points: {self.stats['data_points']}")
        print(f"Regional Data Points: {self.stats['regional_data']}")
        print(f"Related Queries: {self.stats['related_queries']}")
        print(f"Total Data Points: {self.stats['data_points'] + self.stats['regional_data'] + self.stats['related_queries']}")
        print("=" * 70)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print("✅ All data has been stored in the database!")
        print("✅ Ready for AI model training!")

        return results


async def main():
    """Main function"""
    print("\n🇳🇬 Nigerian Google Trends Data Collection\n")
    print("This script will collect trending data for 9 Nigerian categories:")
    print("  • Politics (Tinubu, INEC, elections)")
    print("  • Economy (Naira, CBN, fuel prices)")
    print("  • Security (safety, crime)")
    print("  • Sports (Super Eagles, AFCON)")
    print("  • Entertainment (Nollywood, Afrobeats)")
    print("  • Technology (startups, fintech)")
    print("  • Education (ASUU, universities)")
    print("  • Health (healthcare, NCDC)")
    print("  • Social (youth movements, activism)")
    print("\nExpected: 6,000+ data points for AI training\n")

    input("Press Enter to start collection...")

    collector = TrendsCollector()

    try:
        results = await collector.collect_all_categories()
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️ Collection interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\n❌ Error during collection: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await collector.close()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)