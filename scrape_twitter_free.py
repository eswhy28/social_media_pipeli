"""
FREE Twitter Scraper - No Apify Required
Uses snscrape library to scrape Twitter without any costs
"""

import subprocess
import sys
import json
from datetime import datetime, timedelta

def install_snscrape():
    """Install snscrape if not available"""
    try:
        import snscrape
        print("✅ snscrape already installed")
    except ImportError:
        print("📦 Installing snscrape...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "snscrape"])
        print("✅ snscrape installed successfully")

def scrape_twitter_free(hashtag, limit=1000):
    """
    Scrape Twitter using snscrape (completely free)
    
    Args:
        hashtag: Hashtag to search (with or without #)
        limit: Number of tweets to scrape
    """
    from snscrape.modules import twitter
    
    # Remove # if present
    clean_hashtag = hashtag.lstrip('#')
    
    print(f"\n🐦 Scraping Twitter for #{clean_hashtag}")
    print(f"Target: {limit} tweets")
    print(f"Method: FREE (snscrape)")
    print("="*60)
    
    tweets = []
    query = f"#{clean_hashtag} lang:en min_faves:5"
    
    try:
        for i, tweet in enumerate(twitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
            
            tweets.append({
                "id": tweet.id,
                "date": tweet.date.isoformat(),
                "content": tweet.rawContent,
                "user": tweet.user.username,
                "user_name": tweet.user.displayname,
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "replies": tweet.replyCount,
                "views": tweet.viewCount if hasattr(tweet, 'viewCount') else 0,
                "url": tweet.url,
                "hashtags": tweet.hashtags if hasattr(tweet, 'hashtags') else [],
                "language": tweet.lang
            })
            
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1} tweets scraped...")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n✅ Scraped {len(tweets)} tweets")
    print(f"💰 Cost: $0.00 (FREE!)")
    
    return tweets

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  FREE TWITTER SCRAPER - NO COSTS                         ║
    ║  Uses snscrape (open source)                             ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Install snscrape
    install_snscrape()
    
    # Nigerian hashtags
    hashtags = ["Nigeria", "NigeriaNews", "Lagos", "Naija"]
    
    all_tweets = []
    for hashtag in hashtags:
        tweets = scrape_twitter_free(hashtag, limit=250)
        all_tweets.extend(tweets)
    
    print(f"\n" + "="*60)
    print(f"📊 TOTAL SCRAPED: {len(all_tweets)} tweets")
    print(f"💰 TOTAL COST: $0.00")
    print("="*60)
    
    # Save to JSON
    filename = f"nigerian_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_tweets, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to: {filename}")
    
    if all_tweets:
        print(f"\n📝 Sample tweet:")
        sample = all_tweets[0]
        print(f"   @{sample['user']}: {sample['content'][:100]}...")
        print(f"   Likes: {sample['likes']} | Retweets: {sample['retweets']}")

if __name__ == "__main__":
    main()
