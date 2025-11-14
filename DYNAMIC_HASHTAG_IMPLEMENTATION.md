# Dynamic Hashtag Discovery Implementation

## Overview

Successfully implemented a **dynamic hashtag discovery system** that automatically identifies and tracks trending Nigerian content in real-time. This replaces the previous static hashtag lists with an intelligent, adaptive system.

## What Was Implemented

### 1. HashtagDiscoveryService (`app/services/hashtag_discovery_service.py`)

A comprehensive service that discovers trending hashtags from multiple sources:

**Key Features:**
- **Google Trends Integration**: Fetches trending searches for Nigeria in real-time
- **Content Analysis**: Analyzes recently collected tweets, TikToks, and Facebook posts
- **Engagement Tracking**: Calculates engagement metrics (likes, comments, shares, views)
- **Trend Scoring**: Combines frequency and engagement to rank hashtags
- **Category Filtering**: Supports category-specific hashtags (politics, entertainment, sports, etc.)

**Main Methods:**
```python
# Get trending topics from Google Trends
get_trending_google_topics(region='NG', limit=20)

# Extract trending hashtags from collected content
get_trending_from_collected_content(hours_back=24, min_occurrences=5, limit=50)

# Discover all trending Nigerian hashtags
discover_nigerian_hashtags(include_google_trends=True, include_collected=True, limit=50)

# Get hashtags by category
get_hashtags_by_category(category='politics', limit=20)

# Get engagement metrics for specific hashtag
get_engagement_metrics_for_hashtag(hashtag='nigeria', hours_back=24)
```

### 2. API Endpoints (`app/api/social_media.py`)

Added 5 new endpoints for hashtag discovery:

#### **GET /api/v1/social-media/hashtags/trending**
Get currently trending Nigerian hashtags from all sources.

**Query Parameters:**
- `include_google_trends` (bool): Include Google Trends data
- `include_collected` (bool): Include analysis of collected content
- `limit` (int): Maximum hashtags to return (10-100)

**Response:**
```json
{
  "success": true,
  "data": {
    "trending_hashtags": ["nigeria", "lagos", "elections2024", ...],
    "count": 50,
    "sources": {
      "google_trends": true,
      "collected_content": true
    },
    "timestamp": "2025-11-12T10:30:00Z"
  }
}
```

#### **GET /api/v1/social-media/hashtags/category/{category}**
Get trending hashtags for specific categories.

**Categories:** politics, entertainment, sports, economy, tech, security, education

#### **GET /api/v1/social-media/hashtags/engagement/{hashtag}**
Get detailed engagement metrics for a specific hashtag.

**Response:**
```json
{
  "success": true,
  "data": {
    "hashtag": "nigeria",
    "time_period_hours": 24,
    "metrics": {
      "likes": 15420,
      "comments": 3200,
      "shares": 890,
      "views": 125000,
      "posts_count": 45,
      "platforms": ["twitter", "tiktok", "facebook"],
      "total_engagement": 19510,
      "engagement_rate": 15.6
    }
  }
}
```

#### **GET /api/v1/social-media/hashtags/collected-trends**
Get trending hashtags from collected content with detailed engagement data.

#### **POST /api/v1/social-media/hashtags/update-cache**
Manually trigger hashtag cache update (runs in background).

### 3. Dynamic Collection Script (`collect_dynamic_hashtags.py`)

A new collection script that demonstrates the dynamic hashtag system:

**Features:**
- Automatically discovers trending hashtags before collection
- Tracks engagement metrics for each hashtag
- Focuses on Twitter collection via Apify (per user requirement)
- Updates hashtag cache after collection for future runs

**Usage:**
```bash
python collect_dynamic_hashtags.py
```

**Workflow:**
1. Calls `/hashtags/trending` API to get current trending hashtags
2. Collects tweets for top 10 trending hashtags
3. Retrieves engagement metrics for each hashtag
4. Stores all data in database
5. Triggers cache update for next run
6. Displays detailed performance report

## How It Works

### Trend Discovery Algorithm

1. **Google Trends Analysis**
   - Fetches trending searches for Nigeria
   - Converts search terms to hashtag format
   - Assigns high weight (100 points) to Google Trends data

2. **Content Analysis**
   - Analyzes last 24 hours of collected content
   - Extracts and counts hashtag occurrences
   - Calculates engagement per hashtag (likes + comments + shares + views/100)
   - Computes trend score: `(count × 10) + (engagement / 1000)`

3. **Core Hashtags**
   - Always includes essential Nigerian hashtags
   - Ensures baseline coverage: nigeria, naija, lagos, abuja, etc.

4. **Ranking & Filtering**
   - Combines scores from all sources
   - Sorts by total score
   - Returns top N hashtags

### Engagement Tracking

For each hashtag, the system tracks:
- **Likes**: Total likes across all posts
- **Comments**: Total comments
- **Shares**: Total shares/retweets
- **Views**: Total views (scaled down by /100)
- **Post Count**: Number of posts using this hashtag
- **Platforms**: Which platforms it's trending on
- **Engagement Rate**: (total_engagement / views) × 100

## Benefits Over Static Hashtags

### Before (Static)
- Fixed list of hashtags that never changed
- No adaptation to current events
- Missed emerging trends
- No engagement tracking

### After (Dynamic)
- ✅ Real-time trending topic discovery
- ✅ Adapts to current Nigerian events
- ✅ Captures viral content as it emerges
- ✅ Detailed engagement metrics
- ✅ Category-specific filtering
- ✅ Combines multiple data sources
- ✅ Automated cache updates

## Integration with Existing System

### Database Schema
Uses existing `ApifyScrapedData` table:
- `hashtags` field: Array of hashtags
- `metrics_json` field: Engagement metrics
- `collected_at` field: Timestamp for trend analysis

### No Breaking Changes
- Existing collection scripts still work
- New endpoints are additive
- Old static lists can be used as fallback

## Usage Examples

### 1. Get Trending Hashtags
```python
import httpx

response = httpx.get(
    "http://localhost:8000/api/v1/social-media/hashtags/trending",
    params={"limit": 20}
)
trending = response.json()["data"]["trending_hashtags"]
```

### 2. Get Political Hashtags
```python
response = httpx.get(
    "http://localhost:8000/api/v1/social-media/hashtags/category/politics",
    params={"limit": 10}
)
```

### 3. Check Hashtag Performance
```python
response = httpx.get(
    "http://localhost:8000/api/v1/social-media/hashtags/engagement/nigeria",
    params={"hours_back": 48}
)
metrics = response.json()["data"]["metrics"]
print(f"Total engagement: {metrics['total_engagement']}")
```

### 4. Run Dynamic Collection
```bash
# Start API server first
uvicorn main:app --reload

# In another terminal
python collect_dynamic_hashtags.py
```

## Performance Considerations

### Rate Limiting
- Google Trends: Built-in retry logic, 3 seconds between requests
- Apify: 3 seconds between hashtag collections
- Adjustable limits per endpoint

### Caching
- Cache trending hashtags for efficiency
- Manual cache update endpoint available
- Automatic cache update after each collection

### Scalability
- Async operations throughout
- Background task processing
- Database-backed with PostgreSQL

## Next Steps

### Recommended Enhancements
1. **Scheduled Cache Updates**: Set up Celery task to update cache every hour
2. **TikTok Direct Integration**: Implement TikTok-Api library usage (per user request)
3. **Facebook Direct Integration**: Implement facebook-scraper usage (per user request)
4. **Historical Trending**: Track hashtag performance over time
5. **Predictive Analytics**: ML model to predict emerging trends
6. **Real-time Websocket**: Push notifications for sudden trend spikes

### User Requirements Status
- ✅ **Dynamic hashtags**: Implemented with Google Trends + content analysis
- ✅ **Engagement tracking**: Full metrics (likes, comments, shares, views)
- ✅ **Apify for Twitter only**: Collection script uses Apify only for Twitter
- 🔄 **PostgreSQL migration**: .env updated, need to run migrations
- 🔄 **Direct TikTok library**: Planned, not yet implemented
- 🔄 **Direct Facebook library**: Planned, not yet implemented

## Files Modified/Created

### Created
- `app/services/hashtag_discovery_service.py` - Core hashtag discovery service
- `collect_dynamic_hashtags.py` - Dynamic collection script
- `DYNAMIC_HASHTAG_IMPLEMENTATION.md` - This document

### Modified
- `app/api/social_media.py` - Added 5 new hashtag endpoints
- `.env` - Updated to use PostgreSQL
- `requirements.txt` - Added asyncpg for PostgreSQL support

## Testing

To test the dynamic hashtag system:

1. **Start the API server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Test trending endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/social-media/hashtags/trending?limit=10
   ```

3. **Run dynamic collection:**
   ```bash
   python collect_dynamic_hashtags.py
   ```

4. **Check engagement for specific hashtag:**
   ```bash
   curl http://localhost:8000/api/v1/social-media/hashtags/engagement/nigeria
   ```

## Conclusion

The dynamic hashtag discovery system provides a sophisticated, real-time approach to identifying and tracking trending Nigerian content. By combining Google Trends data with analysis of collected content and engagement metrics, the system automatically adapts to current events and user interests, ensuring maximum relevance and reach.