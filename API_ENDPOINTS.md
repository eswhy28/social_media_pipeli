# Social Media Analytics API - Endpoints Documentation

**Base URL:** `http://localhost:8000/api/v1`  
**Version:** 0.1.0  
**Last Updated:** 2025-11-25

## Table of Contents
- [Authentication](#authentication)
- [Core Endpoints](#core-endpoints)
- [Data Retrieval](#data-retrieval)
- [Media Posts](#media-posts)
- [AI Analysis](#ai-analysis)
- [Social Media Scraping](#social-media-scraping)
- [Analytics](#analytics)
- [Error Responses](#error-responses)

---

## Authentication

**Status:** Disabled for POC  
All endpoints are publicly accessible for testing.

---

## Core Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0",
  "database": "PostgreSQL",
  "cache": "Redis"
}
```

### Root
```http
GET /
```

**Response:**
```json
{
  "name": "Social Media Pipeline POC",
  "version": "0.1.0",
  "status": "healthy",
  "docs": "/docs",
  "description": "Social Media Pipeline POC with Free-Tier Services"
}
```

---

## Data Retrieval

### Get Scraped Posts
```http
GET /social-media/data/scraped
```

**Query Parameters:**
- `platform` (optional): Filter by platform (twitter, facebook)
- `limit` (default: 50, max: 500): Number of posts
- `offset` (default: 0): Pagination offset
- `hours_back` (optional, max: 8760): Time range in hours (up to 1 year for downloaded data)
- `has_media` (optional): Filter posts with/without media (true/false)
- `hashtag` (optional): Filter by hashtag
- `location` (optional): Filter by location

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "post123",
      "platform": "twitter",
      "content": "This is a tweet about #Nigeria.",
      "author": "user1",
      "timestamp": "2025-11-25T10:00:00Z",
      "media_url": "http://example.com/image.jpg",
      "likes": 150,
      "retweets": 30
    }
  ],
  "total_results": 1,
  "limit": 50,
  "offset": 0
}
```

---

## Social Media Endpoints

### 1. Google Trends

#### Get Trending Searches
```http
GET /api/v1/social-media/google-trends/trending
```

**Query Parameters:**
- `region` (string, default: "NG") - Region code (NG for Nigeria)

**Response:**
```json
{
  "success": true,
  "data": {
    "trending_searches": [
      {
        "keyword": "Nigeria elections",
        "traffic": "200k+",
        "date": "2025-11-25"
      }
    ],
    "region": "NG",
    "timestamp": "2025-11-25T22:00:00Z"
  }
}
```

#### Analyze Keywords
```http
POST /api/v1/social-media/google-trends/analyze
```

**Request Body:**
```json
{
  "keywords": ["Nigeria", "Lagos"],
  "timeframe": "today 3-m",
  "include_related": true,
  "include_regional": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "interest_over_time": [...],
    "related_queries": [...],
    "regional_interest": [...]
  }
}
```

#### Get Keyword Suggestions
```http
GET /api/v1/social-media/google-trends/suggestions
```

**Query Parameters:**
- `keyword` (string, required) - Partial keyword

---

### 2. Twitter/X (via Apify)

#### Scrape Twitter with Apify
```http
POST /api/v1/social-media/apify/scrape
```

**Request Body:**
```json
{
  "platform": "twitter",
  "target": "#Nigeria",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "platform": "twitter",
    "items_scraped": 45,
    "items_saved": 43,
    "duplicates": 2,
    "run_id": "abc123",
    "message": "Successfully scraped 45 items"
  }
}
```

#### Get Twitter Analytics
```http
GET /api/v1/social-media/twitter/analytics
```

**Query Parameters:**
- `hashtag` (string) - Hashtag to analyze
- `days` (int, default: 7) - Number of days to analyze

---

### 3. TikTok

#### Scrape TikTok Hashtag
```http
POST /api/v1/social-media/tiktok/hashtag
```

**Request Body:**
```json
{
  "hashtag": "NigeriaNews",
  "count": 30
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hashtag": "NigeriaNews",
    "videos_scraped": 28,
    "videos_saved": 25,
    "total_views": 1500000,
    "total_likes": 85000
  }
}
```

#### Monitor Nigerian TikTok
```http
POST /api/v1/social-media/tiktok/monitor-nigerian
```

**Query Parameters:**
- `max_videos` (int, default: 20, max: 50) - Max videos per hashtag

---

### 4. Facebook

#### Scrape Facebook Page
```http
POST /api/v1/social-media/facebook/page
```

**Request Body:**
```json
{
  "page_name": "ChannelsTV",
  "pages": 2
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "page_name": "ChannelsTV",
    "posts_scraped": 15,
    "posts_saved": 14,
    "total_engagement": 25000
  }
}
```

#### Monitor Nigerian Facebook
```http
POST /api/v1/social-media/facebook/monitor-nigerian
```

**Query Parameters:**
- `pages_per_source` (int, default: 2, max: 5)

---

### 5. Cross-Platform Analytics

#### Get Aggregated Analytics
```http
GET /api/v1/social-media/analytics/aggregated
```

**Query Parameters:**
- `platform` (string, optional) - Filter by platform
- `days` (int, default: 7) - Time range in days
- `granularity` (string, default: "day") - hour/day/week

**Response:**
```json
{
  "success": true,
  "data": {
    "platforms": {
      "twitter": {
        "total_posts": 150,
        "total_engagement": 5000,
        "avg_sentiment": 0.25
      },
      "tiktok": {...},
      "facebook": {...}
    },
    "top_hashtags": [...],
    "trending_topics": [...]
  }
}
```

#### Get Platform Statistics
```http
GET /api/v1/social-media/analytics/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_records": 1250,
    "by_platform": {
      "twitter": 850,
      "tiktok": 200,
      "facebook": 200
    },
    "date_range": {
      "oldest": "2025-11-21",
      "newest": "2025-11-25"
    }
  }
}
```

---

## AI/Analysis Endpoints

### 1. Sentiment Analysis

#### Analyze Sentiment (Advanced)
```http
POST /api/v1/ai/sentiment/analyze
```

**Request Body:**
```json
{
  "text": "Nigeria is making great progress in technology!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "label": "positive",
    "score": 0.85,
    "confidence": 0.92,
    "all_scores": {
      "positive": 0.85,
      "neutral": 0.12,
      "negative": 0.03
    }
  }
}
```

### 2. Location Extraction

#### Extract Locations
```http
POST /api/v1/ai/locations/extract
```

**Request Body:**
```json
{
  "text": "Lagos and Abuja are major cities in Nigeria"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "locations": [
      {
        "text": "Lagos",
        "label": "GPE",
        "start": 0,
        "end": 5
      },
      {
        "text": "Abuja",
        "label": "GPE",
        "start": 10,
        "end": 15
      },
      {
        "text": "Nigeria",
        "label": "GPE",
        "start": 40,
        "end": 47
      }
    ]
  }
}
```

### 3. Comprehensive Analysis

#### Complete Text Analysis
```http
POST /api/v1/ai/analysis/comprehensive
```

**Request Body:**
```json
{
  "text": "President Tinubu visited Lagos to discuss economic reforms"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": {
      "label": "neutral",
      "score": 0.05
    },
    "locations": [
      {"text": "Lagos", "label": "GPE"}
    ],
    "entities": [
      {"text": "Tinubu", "label": "PERSON"},
      {"text": "Lagos", "label": "GPE"}
    ],
    "keywords": [
      {"text": "President", "score": 0.8},
      {"text": "economic reforms", "score": 0.75}
    ]
  }
}
```

### 4. Post Analysis

#### Analyze Specific Post
```http
POST /api/v1/ai/posts/{post_id}/analyze
```

**Query Parameters:**
- `save_to_db` (bool, default: true) - Save results to database

**Response:**
```json
{
  "success": true,
  "data": {
    "post_id": "tweet_123",
    "sentiment": {...},
    "locations": [...],
    "entities": [...],
    "keywords": [...]
  }
}
```

#### Get Post Analysis Results
```http
GET /api/v1/ai/posts/{post_id}/analysis
```

**Response:**
```json
{
  "success": true,
  "data": {
    "post": {...},
    "sentiment_analysis": {...},
    "locations": [...],
    "entities": [...],
    "keywords": [...]
  }
}
```

#### Batch Analyze Posts
```http
POST /api/v1/ai/posts/batch-analyze
```

**Request Body:**
```json
{
  "post_ids": ["tweet_1", "tweet_2", "tweet_3"],
  "save_to_db": true
}
```

### 5. Model Information

#### Get AI Model Info
```http
GET /api/v1/ai/models/info
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment_model": {
      "name": "cardiffnlp/twitter-roberta-base-sentiment",
      "loaded": true
    },
    "ner_model": {
      "name": "en_core_web_sm",
      "loaded": true
    }
  }
}
```

---

## Ingestion Endpoints

### 1. Fetch Tweets

#### Fetch and Analyze Tweets
```http
POST /api/v1/ingestion/fetch-tweets
```

**Request Body:**
```json
{
  "query": "Nigeria FIFA World Cup OR #SuperEagles",
  "max_results": 100,
  "days_back": 7,
  "focus_on_engagement": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tweets_fetched": 95,
    "tweets_stored": 87,
    "duplicates_skipped": 8,
    "query": "Nigeria FIFA World Cup OR #SuperEagles",
    "analytics": {
      "total_engagement": 15000,
      "avg_sentiment": 0.35,
      "top_hashtags": ["#SuperEagles", "#Nigeria"]
    }
  }
}
```

### 2. Fetch Statistics

#### Get Database Stats
```http
GET /api/v1/ingestion/fetch-stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_tweets": 1250,
    "by_sentiment": {
      "positive": 450,
      "neutral": 600,
      "negative": 200
    },
    "last_fetch": "2025-11-25T21:30:00Z",
    "top_hashtags": [...],
    "total_engagement": 250000
  }
}
```

### 3. Re-analyze Existing

#### Re-analyze Existing Tweets
```http
POST /api/v1/ingestion/analyze-existing
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Re-analysis started in background. This may take a few minutes."
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

For POC purposes, rate limiting is set to:
- **100 requests per minute** per endpoint

---

## Interactive Documentation

For interactive API testing, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Notes for POC

1. **Database:** All data is stored in SQLite (`social_media.db`)
2. **Authentication:** Disabled for POC (all endpoints are public)
3. **Background Tasks:** Some operations run asynchronously
4. **Data Source:** Uses JSON files from `/data` directory (migrated to SQLite)
5. **AI Processing:** Runs automatically on new data or can be triggered manually

---

## Quick Start for Testing

1. **Start the server:**
   ```bash
   ./start_server.sh
   ```

2. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Get statistics:**
   ```bash
   curl http://localhost:8000/api/v1/social-media/analytics/stats
   ```

4. **Analyze a post:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ai/sentiment/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Nigeria is amazing!"}'
   ```

---

**Last Updated:** 2025-11-25  
**POC Version:** 0.1.0
