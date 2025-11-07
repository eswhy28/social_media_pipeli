# Social Media API Guide

Complete guide for the new social media data collection and analytics endpoints.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Google Trends Endpoints](#google-trends-endpoints)
4. [TikTok Endpoints](#tiktok-endpoints)
5. [Facebook Endpoints](#facebook-endpoints)
6. [Apify Endpoints](#apify-endpoints)
7. [Cross-Platform Analytics](#cross-platform-analytics)
8. [Monitoring](#monitoring)
9. [Background Tasks](#background-tasks)

## Overview

The Social Media API provides comprehensive data collection and analytics across multiple platforms with a focus on Nigerian content. All endpoints are prefixed with `/api/v1/social-media`.

**Base URL**: `http://localhost:8000/api/v1/social-media`

## Authentication

Most endpoints support optional authentication. Include the JWT token in the Authorization header if you want to track usage:

```
Authorization: Bearer <your-jwt-token>
```

## Google Trends Endpoints

### GET /trends/trending

Get current trending searches in Nigeria.

**Query Parameters:**
- `region` (optional): Region code, default "NG"

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/trends/trending?region=NG"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "trending_searches": [
      {
        "term": "Nigeria Elections",
        "rank": 1,
        "timestamp": "2025-11-06T10:30:00Z",
        "region": "NG",
        "source": "google_trends"
      }
    ],
    "region": "NG",
    "count": 20,
    "timestamp": "2025-11-06T10:30:00Z"
  }
}
```

### POST /trends/analyze

Analyze specific keywords with comprehensive data.

**Request Body:**
```json
{
  "keywords": ["Nigeria", "Lagos", "Elections"],
  "timeframe": "today 3-m",
  "include_related": true,
  "include_regional": true
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/social-media/trends/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["Nigeria", "Lagos"],
    "timeframe": "today 3-m",
    "include_related": true,
    "include_regional": true
  }'
```

**Response:** Returns interest over time, related queries, and regional interest data.

### GET /trends/suggestions

Get keyword suggestions.

**Query Parameters:**
- `keyword` (required): Partial keyword for suggestions

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/trends/suggestions?keyword=nigeria"
```

## TikTok Endpoints

### POST /tiktok/hashtag

Scrape videos from a specific hashtag.

**Request Body:**
```json
{
  "hashtag": "nigeria",
  "count": 30
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/social-media/tiktok/hashtag" \
  -H "Content-Type: application/json" \
  -d '{
    "hashtag": "nigeria",
    "count": 30
  }'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "videos": [
      {
        "video_id": "7123456789",
        "author": {
          "username": "nigerianuser",
          "verified": false
        },
        "metrics": {
          "views": 10000,
          "likes": 500,
          "comments": 50,
          "shares": 20
        },
        "hashtags": ["nigeria", "naija"],
        "created_at": "2025-11-05T10:00:00Z"
      }
    ],
    "total_videos": 30,
    "stored_count": 25
  }
}
```

### GET /tiktok/monitor

Monitor Nigerian TikTok content across popular hashtags.

**Query Parameters:**
- `max_videos` (optional): Max videos per hashtag, default 20

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/tiktok/monitor?max_videos=20"
```

### GET /tiktok/analytics/{hashtag}

Get analytics for a specific hashtag.

**Path Parameters:**
- `hashtag`: Hashtag to analyze

**Query Parameters:**
- `days` (optional): Number of days to analyze, default 7

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/tiktok/analytics/nigeria?days=7"
```

## Facebook Endpoints

### POST /facebook/page

Scrape posts from a Facebook page.

**Request Body:**
```json
{
  "page_name": "legit.ng",
  "pages": 2
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/social-media/facebook/page" \
  -H "Content-Type: application/json" \
  -d '{
    "page_name": "legit.ng",
    "pages": 2
  }'
```

**Response:** Returns scraped posts with engagement metrics.

### GET /facebook/monitor

Monitor Nigerian Facebook pages.

**Query Parameters:**
- `pages_per_source` (optional): Pages to scrape per source, default 2

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/facebook/monitor?pages_per_source=2"
```

### GET /facebook/analytics/{page_name}

Get analytics for a specific page.

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/facebook/analytics/legit.ng?pages=5"
```

## Apify Endpoints

### POST /apify/scrape

Advanced scraping using Apify.

**Request Body:**
```json
{
  "platform": "instagram",
  "target": "lagosnigeria",
  "limit": 50
}
```

**Supported Platforms:**
- `instagram`
- `tiktok`
- `twitter`
- `facebook`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/social-media/apify/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "target": "lagosnigeria",
    "limit": 50
  }'
```

### GET /apify/comprehensive

Comprehensive scraping across multiple platforms.

**Query Parameters:**
- `platforms` (optional): Comma-separated platforms, default "instagram,tiktok,facebook"
- `items_per_platform` (optional): Items per platform, default 50

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/apify/comprehensive?platforms=instagram,tiktok&items_per_platform=50"
```

## Cross-Platform Analytics

### GET /analytics/summary

Get summary metrics across all platforms.

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/analytics/summary?start_date=2025-11-01T00:00:00Z"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2025-11-01T00:00:00Z",
      "end": "2025-11-06T10:30:00Z"
    },
    "platforms": {
      "google_trends": {
        "total_trends": 150
      },
      "tiktok": {
        "total_videos": 500,
        "total_views": 1000000,
        "total_likes": 50000
      },
      "facebook": {
        "total_posts": 300,
        "total_engagement": 25000
      }
    },
    "totals": {
      "total_content_items": 950,
      "total_engagement": 75000
    }
  }
}
```

### GET /analytics/trending-hashtags

Get trending hashtags across all platforms.

**Query Parameters:**
- `limit` (optional): Number of hashtags, default 20
- `days` (optional): Days to analyze, default 7

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/analytics/trending-hashtags?limit=20&days=7"
```

### GET /analytics/top-content

Get top content by engagement.

**Query Parameters:**
- `platform` (optional): Filter by platform
- `limit` (optional): Number of items, default 10
- `days` (optional): Days to analyze, default 7

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/analytics/top-content?platform=tiktok&limit=10"
```

### GET /analytics/platform-comparison

Compare metrics across platforms.

**Query Parameters:**
- `days` (optional): Days to analyze, default 7

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/analytics/platform-comparison?days=7"
```

## Monitoring

### GET /monitoring/health

Get overall health of all data sources.

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/monitoring/health"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "total_sources": 10,
    "active_sources": 9,
    "failed_sources": 1,
    "degraded_sources": 0,
    "timestamp": "2025-11-06T10:30:00Z"
  }
}
```

### GET /monitoring/sources

Get detailed status of all sources.

**Query Parameters:**
- `source_type` (optional): Filter by source type

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/monitoring/sources?source_type=tiktok"
```

## Background Tasks

Background tasks run automatically via Celery for data collection and analytics.

### Available Tasks:

1. **collect_google_trends** - Runs every hour
2. **collect_tiktok_content** - Runs every 2 hours
3. **collect_facebook_content** - Runs every 3 hours
4. **aggregate_analytics** - Runs every hour
5. **reset_daily_counters** - Runs daily at midnight
6. **comprehensive_collection** - Runs daily

### Running Tasks Manually:

```python
from app.tasks.social_media_collection import collect_google_trends_task

# Trigger task
collect_google_trends_task.delay()
```

## Rate Limits

- **Google Trends**: No hard limits, but respect rate limiting (3 seconds between requests)
- **TikTok**: Recommended 2 seconds between requests
- **Facebook**: Recommended 3 seconds between requests, use proxy rotation
- **Apify**: Based on your plan's compute units

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `500` - Internal Server Error

## Data Storage

All collected data is stored in the database with these tables:
- `google_trends_data`
- `tiktok_content`
- `facebook_content`
- `apify_scraped_data`
- `social_media_aggregation`
- `data_source_monitoring`

## Best Practices

1. **Use Background Tasks**: For regular collection, use Celery tasks instead of manual API calls
2. **Respect Rate Limits**: Don't overload APIs with rapid requests
3. **Monitor Health**: Check `/monitoring/health` regularly
4. **Cache Results**: Use Redis caching for frequently accessed data
5. **Filter Nigerian Content**: All services automatically filter for Nigerian relevance

## Interactive API Documentation

Visit the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For issues or questions, check:
- GitHub Issues: [Repository Link]
- Documentation: [Docs Link]
