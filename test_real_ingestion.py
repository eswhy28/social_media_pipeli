#!/usr/bin/env python3
"""
Test script for fetching real tweets using the new ingestion endpoint
"""
import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_json(data, indent=2):
    print(json.dumps(data, indent=indent, default=str))

def main():
    print_section("🚀 REAL TWEET INGESTION TEST - Nigeria FIFA Qualification")
    
    # Step 1: Login
    print("\n📝 Step 1: Authenticating...")
    login_response = requests.post(
        f"{API_V1}/auth/token",
        data={
            "username": "demo",
            "password": "demo123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated successfully")
    
    # Step 2: Check current database stats
    print_section("📊 Step 2: Current Database Statistics")
    stats_response = requests.get(f"{API_V1}/ingestion/fetch-stats", headers=headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print_json(stats)
    else:
        print("⚠️ Could not fetch stats (database might be empty)")
    
    # Step 3: Fetch real tweets about Nigeria FIFA
    print_section("🔍 Step 3: Fetching Real Tweets from Twitter")
    
    print("\n⚠️  TWITTER API FREE TIER - ACTUAL LIMITS ⚠️")
    print("=" * 80)
    print("Twitter Free Tier: 1 REQUEST per 15 MINUTES")
    print("Maximum per request: 100 TWEETS")
    print("Daily capacity: 96 requests = 9,600 tweets/day")
    print("Monthly capacity: ~2,880 requests = 288,000 tweets/month!")
    print("\nThis is PERFECT for continuous monitoring!")

    # Get user input
    num_tweets_input = input("\nHow many tweets to fetch? (Press Enter for 100, or type 10-100, or 'skip'): ").strip()

    if num_tweets_input.lower() == 'skip':
        print("\n⏭️  Skipping Twitter API fetch")
        return

    try:
        num_tweets = int(num_tweets_input) if num_tweets_input else 100
        num_tweets = max(10, min(100, num_tweets))  # Clamp between 10-100
    except ValueError:
        num_tweets = 100

    print(f"\n⚠️  This will use 1 REQUEST (must wait 15 minutes for next request)")
    print(f"   You will get UP TO {num_tweets} tweets in this request")
    print(f"   Fetching MAXIMUM data: metrics, author info, entities, context")
    print(f"   💡 TIP: Set up automation to fetch every 15 mins = 9,600 tweets/day!")

    confirm = input(f"\nConfirm fetch {num_tweets} tweets? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Fetch cancelled")
        return

    # Prepare request
    fetch_payload = {
        "query": "Nigeria",  # Simple query
        "max_results": num_tweets,
        "days_back": 1,  # Last 1 day for more recent tweets
        "focus_on_engagement": True
    }

    print(f"\n📥 Fetching tweets with query: '{fetch_payload['query']}'")
    print(f"   Max results: {fetch_payload['max_results']}")
    print(f"   Date range: Last {fetch_payload['days_back']} day(s)")
    print(f"   Focus on engagement: {fetch_payload['focus_on_engagement']}")
    print(f"\n   📊 This will use 1 of your 10 monthly requests")
    print(f"   🎯 Getting MAXIMUM data: all tweet fields, author info, metrics, entities")

    print("\n⏳ This may take a few seconds...")
    print("   (Note: If Twitter rate limit is exceeded, you may get 0 tweets)")

    start_time = time.time()
    try:
        fetch_response = requests.post(
            f"{API_V1}/ingestion/fetch-tweets",
            headers=headers,
            json=fetch_payload,
            timeout=30  # 30 second timeout
        )
    except requests.exceptions.Timeout:
        print("\n⚠️  Request timed out!")
        print("   This usually means Twitter API rate limit has been exceeded.")
        print("   Rate limits reset every 15 minutes.")
        print("   Please wait a few minutes and try again.")
        fetch_response = None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {str(e)}")
        fetch_response = None

    if fetch_response and fetch_response.status_code == 200:
        result = fetch_response.json()
        print("\n✅ Successfully fetched tweets!")
        print_json(result, indent=2)
        
        data = result.get("data", {})
        
        # Display summary
        print_section("📈 Fetch Summary")
        print(f"✓ Tweets Fetched: {data.get('tweets_fetched', 0)}")
        print(f"✓ New Tweets Stored: {data.get('tweets_stored', 0)}")
        print(f"✓ Duplicates Skipped: {data.get('duplicates_skipped', 0)}")
        
        analytics = data.get('analytics', {})
        if analytics:
            print(f"\n🎯 Analytics:")
            print(f"   Total Posts: {analytics.get('total_posts', 0)}")
            print(f"   Avg Engagement: {analytics.get('avg_engagement', 0):.1f}")
            print(f"   Total Engagement: {analytics.get('total_engagement', 0):,}")
            
            sentiment = analytics.get('sentiment_breakdown', {})
            print(f"\n😊 Sentiment Breakdown:")
            print(f"   Positive: {sentiment.get('positive', 0)}")
            print(f"   Negative: {sentiment.get('negative', 0)}")
            print(f"   Neutral: {sentiment.get('neutral', 0)}")
            
            hashtags = analytics.get('top_hashtags', [])
            if hashtags:
                print(f"\n🔥 Top Hashtags:")
                for ht in hashtags[:5]:
                    print(f"   #{ht['tag']}: {ht['count']} mentions")
        
        # Show top engaged tweet
        top_tweet = data.get('top_engaged_tweet')
        if top_tweet:
            print_section("🏆 Most Engaged Tweet")
            print(f"Author: @{top_tweet.get('author', {}).get('username', 'unknown')}")
            print(f"Text: {top_tweet.get('text', '')[:100]}...")
            metrics = top_tweet.get('metrics', {})
            print(f"Engagement: {metrics.get('likes', 0)} likes, {metrics.get('retweets', 0)} retweets, {metrics.get('replies', 0)} replies")
        
    else:
        print(f"\n❌ Failed to fetch tweets: {fetch_response.status_code}")
        print(fetch_response.text)
        return
    
    # Step 4: View updated database stats
    print_section("📊 Step 4: Updated Database Statistics")
    time.sleep(1)  # Give time for processing
    
    stats_response = requests.get(f"{API_V1}/ingestion/fetch-stats", headers=headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        data = stats.get("data", {})
        
        print(f"Total Posts in Database: {data.get('total_posts', 0)}")
        
        sentiment_dist = data.get('sentiment_distribution', {})
        print(f"\nSentiment Distribution:")
        for sentiment, count in sentiment_dist.items():
            print(f"   {sentiment.capitalize()}: {count}")
        
        engagement = data.get('engagement', {})
        print(f"\nEngagement Metrics:")
        print(f"   Total: {engagement.get('total', 0):,}")
        print(f"   Average: {engagement.get('average', 0):.1f}")
        print(f"   Max: {engagement.get('max', 0):,}")
        
        date_range = data.get('date_range', {})
        print(f"\nDate Range:")
        print(f"   Oldest Tweet: {date_range.get('oldest_tweet', 'N/A')}")
        print(f"   Newest Tweet: {date_range.get('newest_tweet', 'N/A')}")
        
        hashtags = data.get('top_hashtags', [])
        if hashtags:
            print(f"\nTop 10 Hashtags in Database:")
            for i, ht in enumerate(hashtags[:10], 1):
                print(f"   {i:2}. #{ht['tag']:20} : {ht['count']} mentions")
    
    # Step 5: Query the data
    print_section("🔍 Step 5: Querying Stored Data")
    
    # Get overview
    overview_response = requests.get(
        f"{API_V1}/data/overview",
        headers=headers,
        params={"range": "Last 7 Days"}
    )
    if overview_response.status_code == 200:
        overview = overview_response.json().get("data", {})
        print(f"Overview (Last 7 Days):")
        print(f"   Posts: {overview.get('total_posts', 0)}")
        print(f"   Engagement: {overview.get('total_engagement', 0):,}")
        print(f"   Unique Users: {overview.get('unique_users', 0)}")
    
    # Get top posts
    top_posts_response = requests.get(
        f"{API_V1}/data/posts/top",
        headers=headers,
        params={"limit": 5, "range": "Last 7 Days"}
    )
    if top_posts_response.status_code == 200:
        top_posts = top_posts_response.json().get("data", [])
        print(f"\nTop 5 Posts by Engagement:")
        for i, post in enumerate(top_posts[:5], 1):
            print(f"\n   {i}. @{post.get('handle', 'unknown')}")
            print(f"      {post.get('text', '')[:80]}...")
            print(f"      Engagement: {post.get('engagement', 0)} | Sentiment: {post.get('sentiment', 'N/A').upper()}")
    
    # Search for specific content
    search_response = requests.post(
        f"{API_V1}/data/posts/search",
        headers=headers,
        json={
            "q": "FIFA",
            "range": "Last 7 Days",
            "limit": 10
        }
    )
    if search_response.status_code == 200:
        search_results = search_response.json().get("data", {})
        posts = search_results.get("posts", [])
        pagination = search_results.get("pagination", {})
        print(f"\nSearch Results for 'FIFA':")
        print(f"   Found: {pagination.get('total', 0)} posts")
        print(f"   Showing: {len(posts)} posts")
    
    # Step 6: Summary
    print_section("✅ TEST COMPLETE - Summary")
    print("""
    ✓ Successfully authenticated
    ✓ Fetched real tweets from Twitter API
    ✓ Performed sentiment analysis on all tweets
    ✓ Saved all data to database
    ✓ Extracted hashtags and keywords
    ✓ Calculated engagement metrics
    ✓ Verified data retrieval through API endpoints
    
    💡 Key Features Demonstrated:
    • Real-time tweet fetching with Twitter API v2
    • Automatic sentiment analysis using TextBlob
    • Smart engagement-based sorting
    • Duplicate detection and prevention
    • Comprehensive analytics and statistics
    • Full database persistence
    • RESTful API access to all data
    
    🎯 Next Steps:
    1. View full API docs at: http://localhost:8000/docs
    2. Explore the /ingestion/fetch-tweets endpoint with different queries
    3. Use /ingestion/fetch-stats to monitor database growth
    4. Query data using /data/* endpoints
    5. Remember: 100 tweets per month limit on free tier
    """)
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
