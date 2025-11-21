"""
Test Google Trends with improved methods
This will try multiple APIs to get real Nigerian trending topics
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.services.google_trends_service import get_google_trends_service

async def test_google_trends():
    """Test all Google Trends methods"""
    
    print("=" * 70)
    print("🔍 TESTING GOOGLE TRENDS - IMPROVED METHODS")
    print("=" * 70)
    
    trends_service = get_google_trends_service()
    
    # Test 1: Get trending searches
    print("\n📊 Test 1: Getting trending searches for Nigeria...")
    print("-" * 70)
    
    trending = await trends_service.get_trending_searches(region="NG", limit=10)
    
    print(f"\n✅ Retrieved {len(trending)} trending topics:")
    print(f"Source: {trending[0]['source'] if trending else 'Unknown'}")
    print(f"Is Fallback: {trending[0].get('is_fallback', False) if trending else 'Unknown'}")
    print()
    
    for i, trend in enumerate(trending, 1):
        print(f"{i}. {trend['term']}")
        if trend.get('traffic'):
            print(f"   Traffic: {trend['traffic']}")
        if trend.get('growth'):
            print(f"   Growth: {trend['growth']}")
        if trend.get('article_url'):
            print(f"   URL: {trend['article_url'][:60]}...")
    
    # Test 2: Get related queries for a Nigerian topic
    print("\n\n📈 Test 2: Getting related queries for 'Nigeria'...")
    print("-" * 70)
    
    related = await trends_service.get_related_queries("Nigeria", geo="NG")
    
    if related.get('rising_queries'):
        print(f"\n✅ Rising queries ({len(related['rising_queries'])}):")
        for query in related['rising_queries'][:5]:
            print(f"  - {query['query']} (Growth: {query['value']})")
    
    if related.get('top_queries'):
        print(f"\n✅ Top queries ({len(related['top_queries'])}):")
        for query in related['top_queries'][:5]:
            print(f"  - {query['query']} (Score: {query['value']})")
    
    # Test 3: Get suggestions
    print("\n\n💡 Test 3: Getting suggestions for 'Nigerian'...")
    print("-" * 70)
    
    suggestions = await trends_service.get_suggestions("Nigerian")
    
    if suggestions:
        print(f"\n✅ Retrieved {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"{i}. {suggestion}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Trending Topics: {len(trending)}")
    print(f"Source: {trending[0]['source'] if trending else 'None'}")
    print(f"Using Real Data: {'❌ NO (Fallback)' if trending[0].get('is_fallback') else '✅ YES (Real Google Trends)'}")
    print(f"Related Queries (Rising): {len(related.get('rising_queries', []))}")
    print(f"Related Queries (Top): {len(related.get('top_queries', []))}")
    print(f"Suggestions: {len(suggestions)}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_google_trends())
