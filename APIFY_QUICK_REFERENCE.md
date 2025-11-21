# Quick Reference: Updated Apify Service

## 🎯 Supported Platforms
- ✅ **Twitter (X)** - via `apidojo/tweet-scraper`
- ✅ **Facebook** - via `apify/facebook-posts-scraper`
- ❌ Instagram (removed)
- ❌ TikTok (removed)

---

## 📖 Method Reference

### Twitter Methods

#### 1. Search Twitter
```python
from app.services.apify_service import get_apify_service

apify_service = get_apify_service()
result = await apify_service.scrape_twitter_search(
    search_queries=["#Nigeria", "#Lagos"],  # Array of hashtags/keywords
    max_tweets=50                            # Max tweets to return
)
```

**Returns:**
```python
{
    "platform": "twitter",
    "success": True,
    "queries": ["#Nigeria", "#Lagos"],
    "tweets": [...],
    "total_tweets": 50,
    "timestamp": "2025-11-21T22:26:55+01:00"
}
```

#### 2. Scrape Twitter Profile
```python
result = await apify_service.scrape_twitter_profile(
    username="NigeriaStories",  # Without @ symbol
    tweets_limit=50              # Max tweets to return
)
```

**Returns:**
```python
{
    "platform": "twitter",
    "username": "NigeriaStories",
    "tweets": [...],
    "total_tweets": 50,
    "timestamp": "2025-11-21T22:26:55+01:00"
}
```

### Facebook Methods

#### 3. Scrape Facebook Page
```python
result = await apify_service.scrape_facebook_page(
    page_url="https://www.facebook.com/legit.ng",
    posts_limit=50
)
```

**Returns:**
```python
{
    "platform": "facebook",
    "page_url": "https://www.facebook.com/legit.ng",
    "posts": [...],
    "total_posts": 50,
    "timestamp": "2025-11-21T22:26:55+01:00"
}
```

### Comprehensive Scraping

#### 4. Scrape Nigerian Content (Both Platforms)
```python
result = await apify_service.scrape_nigerian_social_media(
    platforms=["twitter", "facebook"],  # Both platforms
    items_per_platform=30
)
```

**Returns:**
```python
{
    "platforms": {
        "twitter": { "tweets": [...], "total_tweets": 30 },
        "facebook": { "posts": [...], "total_posts": 30 }
    },
    "region": "Nigeria",
    "timestamp": "2025-11-21T22:26:55+01:00"
}
```

---

## 🌐 API Endpoints

### 1. Scrape via Apify
```http
POST /api/social-media/apify/scrape
Content-Type: application/json

{
  "platform": "twitter",      // "twitter" or "facebook"
  "target": "NigeriaStories", // Username or page URL
  "limit": 50                 // 10-100
}
```

### 2. Comprehensive Scraping
```http
GET /api/social-media/apify/comprehensive?platforms=twitter,facebook&items_per_platform=50
```

---

## 📊 Data Structure

### Twitter Tweet Object
```python
{
    "source": "twitter",
    "source_id": "1234567890",
    "author": "username",
    "author_name": "Display Name",
    "content": "Tweet text...",
    "metrics": {
        "likes": 100,
        "retweets": 50,
        "replies": 25,
        "views": 1000
    },
    "hashtags": ["Nigeria", "Lagos"],
    "mentions": ["username1", "username2"],
    "posted_at": "2025-11-21T12:00:00Z",
    "url": "https://twitter.com/username/status/1234567890",
    "is_retweet": False,
    "is_quote": False,
    "language": "en",
    "geo_location": "Nigeria"
}
```

### Facebook Post Object
```python
{
    "source": "facebook",
    "source_id": "post_id",
    "page": "Page Name",
    "author": "Author Name",
    "content": "Post text...",
    "metrics": {
        "likes": 500,
        "comments": 100,
        "shares": 50,
        "reactions": 600
    },
    "media_type": "image",  // "video", "image", "text"
    "has_video": False,
    "has_image": True,
    "images": ["url1", "url2"],
    "video_url": None,
    "posted_at": "2025-11-21T12:00:00Z",
    "url": "https://facebook.com/...",
    "geo_location": "Nigeria"
}
```

---

## ⚙️ Input Parameters

### Twitter Scraper (apidojo/tweet-scraper)
```python
{
    "searchTerms": ["#Nigeria"],     # Array of search terms/hashtags
    "maxItems": 50,                  # Max tweets (10-100)
    "sort": "Latest"                 # Sort order
}

# OR for profiles:
{
    "twitterHandles": ["username"],  # Array of handles (no @)
    "maxItems": 50,
    "sort": "Latest"
}
```

### Facebook Scraper (apify/facebook-posts-scraper)
```python
{
    "startUrls": [{"url": "https://facebook.com/page"}],
    "resultsLimit": 50,              # Max posts (10-100)
    "proxy": {
        "useApifyProxy": True
    }
}
```

---

## 🗄️ Database Storage

### Twitter Data
**Table**: `apify_scraped_data`
**Fields**:
- platform = "twitter"
- source_id (tweet ID)
- author (username)
- content (tweet text)
- metrics_json (engagement metrics)
- hashtags (array)
- mentions (array)
- posted_at
- collected_at

### Facebook Data
**Table**: `facebook_content`
**Fields**:
- id (post ID)
- page_name
- text (post content)
- likes, comments, shares
- total_engagement
- posted_at
- collected_at

---

## 🚨 Error Handling

### Common Errors

**1. Unsupported Platform**
```python
HTTP 400: "Unsupported platform: instagram. Only 'twitter' and 'facebook' are supported."
```

**2. Invalid Target**
```python
{
    "platform": "twitter",
    "username": "invalid_user",
    "error": "User not found or private account"
}
```

**3. Rate Limit**
```python
{
    "error": "Apify rate limit exceeded. Try again later."
}
```

---

## 💡 Best Practices

1. **Rate Limiting**: Add delays between requests
   ```python
   await asyncio.sleep(5)  # 5 second delay
   ```

2. **Error Handling**: Always check for errors
   ```python
   if result.get('error'):
       logger.error(f"Scraping failed: {result['error']}")
   ```

3. **Data Validation**: Verify data before storage
   ```python
   if result.get('tweets') and len(result['tweets']) > 0:
       # Process and store data
   ```

4. **Monitoring**: Log all scraping activities
   ```python
   logger.info(f"Scraped {len(tweets)} tweets for #{hashtag}")
   ```

---

## 📝 Example Usage Script

```python
import asyncio
from app.services.apify_service import get_apify_service

async def scrape_nigerian_content():
    """Example: Scrape Nigerian content from Twitter and Facebook"""
    
    apify_service = get_apify_service()
    
    # 1. Twitter hashtag search
    twitter_result = await apify_service.scrape_twitter_search(
        search_queries=["#Nigeria", "#Lagos"],
        max_tweets=20
    )
    print(f"Twitter: {twitter_result.get('total_tweets', 0)} tweets")
    
    # 2. Facebook page scraping
    fb_result = await apify_service.scrape_facebook_page(
        page_url="https://www.facebook.com/legit.ng",
        posts_limit=20
    )
    print(f"Facebook: {fb_result.get('total_posts', 0)} posts")
    
    # 3. Comprehensive scraping
    comprehensive = await apify_service.scrape_nigerian_social_media(
        platforms=["twitter", "facebook"],
        items_per_platform=10
    )
    print(f"Platforms scraped: {list(comprehensive['platforms'].keys())}")

if __name__ == "__main__":
    asyncio.run(scrape_nigerian_content())
```

---

## 🔗 Useful Links

- [Tweet Scraper V2 Docs](https://apify.com/apidojo/tweet-scraper)
- [Facebook Posts Scraper Docs](https://apify.com/apify/facebook-posts-scraper)
- [Apify Platform](https://console.apify.com/)
- [Apify Python Client](https://docs.apify.com/api/client/python)

---

**Last Updated**: 2025-11-21T22:26:55+01:00
