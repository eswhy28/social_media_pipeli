"""
Test Google Trends - direct import to avoid package conflicts
"""

import asyncio
import sys
sys.path.insert(0, '.')

# Direct import to avoid transformers conflict
from app.services.google_trends_service import GoogleTrendsService

async def test_google_trends():
    """Test all Google Trends methods"""
    
    print("=" * 70)
    print("🔍 TESTING COMPREHENSIVE GOOGLE TRENDS")
    print("=" * 70)
    
    trends_service = GoogleTrendsService()
    
    # Test: Get comprehensive trending searches
    print("\n📊 Getting comprehensive trending searches for Nigeria...")
    print("-" * 70)
    
    trending = await trends_service.get_trending_searches(region="NG", limit=20)
    
    print(f"\n✅ Retrieved {len(trending)} trending topics")
    print(f"📍 Sources used: {set(t['source'] for t in trending)}")
    print(f"🎯 Is fallback: {any(t.get(' is_fallback') for t in trending)}")
    print("\n🔥 TOP TRENDING TOPICS:\n")
    
    for i, trend in enumerate(trending[:20], 1):
        source_emoji = {
            "realtime_stories": "📰",
            "rising_queries": "📈",
            "top_queries": "⭐",
            "traditional_api": "🔍",
            "suggestions": "💡"
        }.get(trend['source'], "❓")
        
        print(f"{i:2d}. {source_emoji} {trend['term']}")
        
        if trend.get('growth'):
            growth_val = trend['growth']
            if isinstance(growth_val, (int, float)):
                print(f"      Growth: +{growth_val:,}%")
            else:
                print(f"      Growth: {growth_val}")
        elif trend.get('relevance'):
            print(f"      Relevance: {trend['relevance']}")
        
        if trend.get('parent_keyword'):
            print(f"      Related to: {trend['parent_keyword']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    by_source = {}
    for t in trending:
        source = t['source']
        by_source[source] = by_source.get(source, 0) + 1
    
    print(f"Total Topics: {len(trending)}")
    print(f"\nBreakdown by source:")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {source}: {count}")
    
    print(f"\nUsing Real Data: {'✅ YES' if not any(t.get('is_fallback') for t in trending) else '❌ NO (Fallback)'}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_google_trends())
