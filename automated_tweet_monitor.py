#!/usr/bin/env python3
"""
Automated Twitter Monitoring Script
Fetches 100 tweets every 15 minutes = 9,600 tweets/day for FREE!

This script runs continuously and:
- Fetches tweets every 15 minutes
- Rotates through multiple topics
- Performs sentiment analysis automatically
- Stores everything in the database
- Logs all activity

Perfect for 24/7 monitoring of Nigeria-related topics!
"""

import requests
import time
import schedule
import logging
from datetime import datetime
from typing import List, Dict
import json
import os
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'tweet_monitor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Authentication credentials
USERNAME = "demo"
PASSWORD = "demo123"

# Query topics to rotate through (customize these for your needs!)
QUERY_TOPICS = [
    {
        "name": "Nigeria FIFA & Sports",
        "query": "Nigeria FIFA OR #SuperEagles OR #AFCON OR Nigeria Football",
        "max_results": 100,
        "days_back": 1
    },
    {
        "name": "Nigerian Politics",
        "query": "Nigeria Politics OR #NigerianPolitics OR Nigeria Election",
        "max_results": 100,
        "days_back": 1
    },
    {
        "name": "Lagos & Nigerian Economy",
        "query": "Lagos Nigeria OR Nigerian Economy OR Nigeria Business",
        "max_results": 100,
        "days_back": 1
    },
    {
        "name": "Nigerian Entertainment",
        "query": "Nollywood OR #Afrobeats OR Nigeria Music OR Nigeria Entertainment",
        "max_results": 100,
        "days_back": 1
    },
]

# Track current topic index
current_topic_index = 0
token = None
token_expires_at = 0

# Statistics tracking
stats = {
    "total_fetches": 0,
    "total_tweets_fetched": 0,
    "total_tweets_stored": 0,
    "successful_fetches": 0,
    "failed_fetches": 0,
    "started_at": datetime.now().isoformat()
}


def get_auth_token() -> str:
    """Authenticate and get access token"""
    global token, token_expires_at
    
    # Check if token is still valid (with 5-minute buffer)
    if token and time.time() < (token_expires_at - 300):
        return token
    
    logger.info("🔐 Authenticating with API...")
    try:
        response = requests.post(
            f"{API_V1}/auth/token",
            data={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            # Token expires in 60 minutes by default
            token_expires_at = time.time() + 3600
            logger.info("✅ Authentication successful")
            return token
        else:
            logger.error(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Authentication error: {str(e)}")
        return None


def fetch_tweets():
    """Main function to fetch tweets - runs every 15 minutes"""
    global current_topic_index, stats
    
    stats["total_fetches"] += 1
    
    # Get authentication token
    auth_token = get_auth_token()
    if not auth_token:
        logger.error("Cannot fetch tweets without authentication")
        stats["failed_fetches"] += 1
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get current topic (rotate through topics)
    topic = QUERY_TOPICS[current_topic_index]
    current_topic_index = (current_topic_index + 1) % len(QUERY_TOPICS)
    
    logger.info("=" * 80)
    logger.info(f"📥 FETCHING TWEETS - Topic {current_topic_index + 1}/{len(QUERY_TOPICS)}")
    logger.info(f"   Topic: {topic['name']}")
    logger.info(f"   Query: {topic['query']}")
    logger.info(f"   Max Results: {topic['max_results']}")
    logger.info("=" * 80)
    
    # Prepare request
    fetch_payload = {
        "query": topic["query"],
        "max_results": topic["max_results"],
        "days_back": topic["days_back"],
        "focus_on_engagement": True
    }
    
    try:
        # Make the API request
        start_time = time.time()
        response = requests.post(
            f"{API_V1}/ingestion/fetch-tweets",
            headers=headers,
            json=fetch_payload,
            timeout=60
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            
            tweets_fetched = data.get("tweets_fetched", 0)
            tweets_stored = data.get("tweets_stored", 0)
            duplicates = data.get("duplicates_skipped", 0)
            
            # Update statistics
            stats["total_tweets_fetched"] += tweets_fetched
            stats["total_tweets_stored"] += tweets_stored
            stats["successful_fetches"] += 1
            
            logger.info(f"✅ SUCCESS! Fetched in {elapsed_time:.2f}s")
            logger.info(f"   Tweets Fetched: {tweets_fetched}")
            logger.info(f"   New Tweets Stored: {tweets_stored}")
            logger.info(f"   Duplicates Skipped: {duplicates}")
            
            # Log analytics if available
            analytics = data.get("analytics", {})
            if analytics:
                sentiment = analytics.get("sentiment_breakdown", {})
                logger.info(f"   Sentiment: +{sentiment.get('positive', 0)} "
                          f"~{sentiment.get('neutral', 0)} "
                          f"-{sentiment.get('negative', 0)}")
                
                avg_engagement = analytics.get("avg_engagement", 0)
                logger.info(f"   Avg Engagement: {avg_engagement:.1f}")
            
            # Log overall statistics
            logger.info("")
            logger.info(f"📊 OVERALL STATS:")
            logger.info(f"   Total Fetches: {stats['total_fetches']}")
            logger.info(f"   Success Rate: {stats['successful_fetches']}/{stats['total_fetches']} "
                       f"({100*stats['successful_fetches']/stats['total_fetches']:.1f}%)")
            logger.info(f"   Total Tweets: {stats['total_tweets_fetched']} fetched, "
                       f"{stats['total_tweets_stored']} stored")
            logger.info(f"   Running Since: {stats['started_at']}")
            
        else:
            logger.error(f"❌ FAILED: HTTP {response.status_code}")
            logger.error(f"   Response: {response.text[:200]}")
            stats["failed_fetches"] += 1
            
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out (60s)")
        logger.info("   Possible causes: API rate limit, slow network, or server issue")
        stats["failed_fetches"] += 1
    except Exception as e:
        logger.error(f"❌ Error fetching tweets: {str(e)}")
        stats["failed_fetches"] += 1
    
    # Log next fetch time
    next_fetch = datetime.now().timestamp() + 900  # 15 minutes from now
    next_fetch_time = datetime.fromtimestamp(next_fetch).strftime("%H:%M:%S")
    logger.info(f"⏰ Next fetch at: {next_fetch_time} (in 15 minutes)")
    logger.info("")


def get_database_stats():
    """Get and log database statistics - runs hourly"""
    auth_token = get_auth_token()
    if not auth_token:
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_V1}/ingestion/fetch-stats", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            
            logger.info("=" * 80)
            logger.info("📊 DATABASE STATISTICS")
            logger.info("=" * 80)
            logger.info(f"Total Posts: {data.get('total_posts', 0):,}")
            
            sentiment_dist = data.get('sentiment_distribution', {})
            total_analyzed = sum(sentiment_dist.values())
            if total_analyzed > 0:
                logger.info(f"Sentiment Distribution:")
                for sentiment, count in sentiment_dist.items():
                    percentage = (count / total_analyzed) * 100
                    logger.info(f"   {sentiment.capitalize()}: {count:,} ({percentage:.1f}%)")
            
            engagement = data.get('engagement', {})
            logger.info(f"Engagement:")
            logger.info(f"   Total: {engagement.get('total', 0):,}")
            logger.info(f"   Average: {engagement.get('average', 0):.1f}")
            logger.info(f"   Max: {engagement.get('max', 0):,}")
            
            hashtags = data.get('top_hashtags', [])
            if hashtags:
                logger.info(f"Top 5 Hashtags:")
                for i, ht in enumerate(hashtags[:5], 1):
                    logger.info(f"   {i}. #{ht['tag']}: {ht['count']} mentions")
            
            logger.info("=" * 80)
            logger.info("")
            
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")


def save_stats():
    """Save statistics to file - runs every hour"""
    try:
        stats_file = log_dir / f"monitor_stats_{datetime.now().strftime('%Y%m%d')}.json"
        stats["last_updated"] = datetime.now().isoformat()
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"💾 Statistics saved to {stats_file}")
    except Exception as e:
        logger.error(f"Error saving statistics: {str(e)}")


def main():
    """Main function to set up and run the scheduler"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("🚀 AUTOMATED TWITTER MONITOR - STARTING UP")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Target: 9,600 tweets/day (100 tweets every 15 minutes)")
    logger.info(f"Topics: {len(QUERY_TOPICS)} rotating topics")
    logger.info("")
    logger.info("Monitoring Topics:")
    for i, topic in enumerate(QUERY_TOPICS, 1):
        logger.info(f"   {i}. {topic['name']}")
        logger.info(f"      Query: {topic['query']}")
    logger.info("")
    logger.info("Schedule:")
    logger.info("   • Fetch tweets: Every 15 minutes")
    logger.info("   • Database stats: Every hour")
    logger.info("   • Save stats: Every hour")
    logger.info("")
    logger.info("💡 TIP: Let this run 24/7 for maximum data collection!")
    logger.info("   Press Ctrl+C to stop")
    logger.info("=" * 80)
    logger.info("")
    
    # Test authentication
    if not get_auth_token():
        logger.error("❌ Failed to authenticate. Please check your credentials.")
        logger.error("   Ensure the API server is running: python run.py")
        return
    
    # Schedule tasks
    schedule.every(15).minutes.do(fetch_tweets)  # Main task: fetch tweets
    schedule.every(1).hours.do(get_database_stats)  # Hourly: log database stats
    schedule.every(1).hours.do(save_stats)  # Hourly: save statistics
    
    # Run the first fetch immediately
    logger.info("🎬 Running first fetch immediately...")
    fetch_tweets()
    
    # Also get initial database stats
    get_database_stats()
    
    # Run the scheduler
    logger.info("⏰ Scheduler started. Waiting for next scheduled task...")
    logger.info("")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("⚠️  SHUTTING DOWN - User interrupted")
        logger.info("=" * 80)
        logger.info("Final Statistics:")
        logger.info(f"   Total Fetches: {stats['total_fetches']}")
        logger.info(f"   Successful: {stats['successful_fetches']}")
        logger.info(f"   Failed: {stats['failed_fetches']}")
        logger.info(f"   Total Tweets Fetched: {stats['total_tweets_fetched']:,}")
        logger.info(f"   Total Tweets Stored: {stats['total_tweets_stored']:,}")
        logger.info(f"   Runtime: {datetime.now()} - {stats['started_at']}")
        logger.info("")
        logger.info("💾 Saving final statistics...")
        save_stats()
        logger.info("✅ Shutdown complete. Goodbye!")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()

