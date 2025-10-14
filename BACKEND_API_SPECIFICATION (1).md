# Backend API Specification


### Overview
This document outlines the complete API specification for the backend service that provides social media data, sentiment analysis, and monitoring capabilities for the monitoring platform.

---

## Base Configuration
- **Base URL**: `Please Provide Goyama`
- **Authentication**: Bearer Token (JWT)
- **Rate Limiting**: 1000 requests per hour per user
- **Response Format**: JSON
- **Error Format**: Standard HTTP status codes + JSON error response

---

## Authentication Endpoints

### POST /auth/login
**Description**: User authentication and login
**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": "user_123",
      "username": "string",
      "email": "string",
      "role": "user|admin",
      "permissions": ["read", "write", "admin"]
    }
  }
}
```

### POST /auth/refresh
**Description**: Refresh expired JWT token
**Headers**: `Authorization: Bearer <expired_token>`
**Response**:
```json
{
  "success": true,
  "data": {
    "token": "new_jwt_token_here"
  }
}
```

---

## Core Data Endpoints

### GET /data/overview
**Description**: Get overview dashboard data
**Query Parameters**:
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days, Custom)
- `start_date`: string (ISO date, required if range=Custom)
- `end_date`: string (ISO date, required if range=Custom)

**Response**:
```json
{
  "success": true,
  "data": {
    "sentiment": {
      "pos": 35,
      "neg": 40,
      "neu": 25
    },
    "metrics": {
      "total_mentions": 15800,
      "total_impressions": 1200000,
      "total_reach": 820000,
      "engagement_rate": 0.048
    },
    "anomalies": [
      {
        "id": "a1",
        "title": "Negative Sentiment Spike",
        "severity": "high",
        "detected_at": "2025-01-15T10:30:00Z",
        "summary": "Significant drop in sentiment over last 24h",
        "metric": "Sentiment",
        "delta": "-23%"
      }
    ],
    "trending_hashtags": [
      {
        "tag": "#Nigeria",
        "count": 12300,
        "change": 12
      }
    ],
    "trending_keywords": [
      {
        "keyword": "Inflation",
        "count": 9900,
        "change": 18
      }
    ]
  }
}
```

### GET /data/sentiment/live
**Description**: Get real-time sentiment gauge value
**Response**:
```json
{
  "success": true,
  "data": {
    "value": 62,
    "trend": "increasing",
    "confidence": 85,
    "last_updated": "2025-01-15T10:30:00Z"
  }
}
```

### GET /data/sentiment/series
**Description**: Get sentiment time series data
**Query Parameters**:
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days, Custom)
- `granularity`: string (hour, day, week, month)
- `start_date`: string (ISO date, required if range=Custom)
- `end_date`: string (ISO date, required if range=Custom)

**Response**:
```json
{
  "success": true,
  "data": {
    "series": [
      {
        "name": "Mon",
        "pos": 35,
        "neg": 20,
        "neu": 5
      }
    ],
    "summary": {
      "average_sentiment": 58,
      "trend": "increasing",
      "volatility": "low"
    }
  }
}
```

### GET /data/sentiment/categories
**Description**: Get sentiment breakdown by categories
**Query Parameters**:
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days, Custom)
- `start_date`: string (ISO date, required if range=Custom)
- `end_date`: string (ISO date, required if range=Custom)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "name": "Economy",
      "pos": 20,
      "neg": 15,
      "neu": 10
    }
  ]
}
```

---

## Hashtag & Keyword Analysis

### GET /data/hashtags/trending
**Description**: Get trending hashtags
**Query Parameters**:
- `limit`: number (default: 20)
- `min_mentions`: number (default: 100)
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "tag": "#Nigeria",
      "count": 12300,
      "change": 12,
      "sentiment": {
        "pos": 42,
        "neg": 30,
        "neu": 28
      },
      "top_posts": [
        {
          "handle": "@ChannelsTV",
          "text": "Parade recap highlights",
          "url": "https://x.com/e/4",
          "engagement": "6.1K"
        }
      ]
    }
  ]
}
```

### GET /data/keywords/trends
**Description**: Get keyword trends and analysis
**Query Parameters**:
- `limit`: number (default: 20)
- `category`: string (optional filter)
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "keyword": "Kano",
      "mentions": 245,
      "trend": 15,
      "split": {
        "pos": 40,
        "neg": 35,
        "neu": 25
      },
      "emotion": "Disbelief",
      "sample": "This is so unfair to Kano people...",
      "category": "Politics",
      "location_hint": "Kano",
      "score": 65
    }
  ]
}
```

### GET /data/hashtags/{tag}
**Description**: Get detailed hashtag analysis
**Path Parameters**:
- `tag`: string (hashtag without #)

**Response**:
```json
{
  "success": true,
  "data": {
    "title": "#Nigeria",
    "summary": "Mixed sentiment around governance, economy, and national events.",
    "mentions": 12300,
    "sentiment": {
      "pos": 42,
      "neu": 28,
      "neg": 30
    },
    "top_posts": [
      {
        "handle": "@ChannelsTV",
        "text": "Parade recap highlights",
        "url": "https://x.com/e/4",
        "engagement": "6.1K"
      }
    ],
    "geographic_distribution": [
      {
        "state": "Lagos",
        "mentions": 3800,
        "percentage": 31
      }
    ],
    "temporal_analysis": {
      "peak_hours": "2-4 PM",
      "weekend_drop": 25,
      "daily_pattern": "business_hours_peak"
    }
  }
}
```

---

## Influencer & Account Analysis

### GET /data/influencers
**Description**: Get influential accounts and their metrics
**Query Parameters**:
- `limit`: number (default: 20)
- `min_followers`: number (default: 100000)
- `verified_only`: boolean (default: false)
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "handle": "@ChannelsTV",
      "engagement": 10900,
      "followers_primary": 5200000,
      "following": 280,
      "verified": true,
      "avatar_url": "https://example.com/avatar.jpg",
      "engagement_rate": 0.002,
      "top_mentions": [
        {
          "keyword": "Politics",
          "count": 150
        }
      ]
    }
  ]
}
```

### GET /data/accounts/{handle}/analysis
**Description**: Get detailed account analysis
**Path Parameters**:
- `handle`: string (account handle without @)

**Response**:
```json
{
  "success": true,
  "data": {
    "handle": "@ChannelsTV",
    "profile": {
      "name": "Channels Television",
      "verified": true,
      "followers": 5200000,
      "following": 280,
      "created_at": "2009-01-01T00:00:00Z"
    },
    "engagement_metrics": {
      "total_engagement": 10900,
      "engagement_rate": 0.002,
      "avg_likes": 8500,
      "avg_retweets": 1200,
      "avg_replies": 1200
    },
    "content_analysis": {
      "top_topics": ["Politics", "News", "Economy"],
      "sentiment_distribution": {
        "pos": 45,
        "neg": 25,
        "neu": 30
      },
      "posting_frequency": "high",
      "peak_posting_hours": "2-4 PM"
    }
  }
}
```

---

## Geographic Analysis

### GET /data/geographic/states
**Description**: Get geographic distribution data for Nigeria states
**Query Parameters**:
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)
- `keyword`: string (optional filter)
- `hashtag`: string (optional filter)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "state": "Lagos",
      "mentions": 125000,
      "percentage": 72,
      "sentiment": {
        "pos": 45,
        "neg": 25,
        "neu": 30
      },
      "top_keywords": ["Economy", "Technology", "Entertainment"],
      "language_distribution": {
        "english": 85,
        "yoruba": 10,
        "pidgin": 5
      }
    }
  ]
}
```

### GET /data/geographic/coordinates
**Description**: Get geographic data with coordinates for mapping
**Query Parameters**:
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)
- `keyword`: string (optional filter)

**Response**:
```json
{
  "success": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [3.3792, 6.5244]
        },
        "properties": {
          "state": "Lagos",
          "mentions": 125000,
          "sentiment": "positive",
          "intensity": 0.8
        }
      }
    ]
  }
}
```

---

## Content & Post Analysis

### GET /data/posts/top
**Description**: Get top performing posts
**Query Parameters**:
- `limit`: number (default: 20)
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)
- `keyword`: string (optional filter)
- `hashtag`: string (optional filter)
- `min_engagement`: number (default: 100)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "post_123",
      "handle": "@ChannelsTV",
      "text": "Breaking: New policy announcement...",
      "url": "https://x.com/e/4",
      "engagement": "6.1K",
      "likes": 4500,
      "retweets": 1200,
      "replies": 400,
      "posted_at": "2025-01-15T10:30:00Z",
      "sentiment": "positive",
      "sentiment_score": 0.8,
      "topics": ["Politics", "Policy"],
      "language": "english"
    }
  ]
}
```

### GET /data/posts/search
**Description**: Search posts by content, keywords, or hashtags
**Query Parameters**:
- `q`: string (search query)
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)
- `limit`: number (default: 50)
- `offset`: number (default: 0)
- `sentiment`: string (positive, negative, neutral)
- `language`: string (english, hausa, yoruba, pidgin)

**Response**:
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "post_123",
        "handle": "@user123",
        "text": "Search result content...",
        "url": "https://x.com/e/4",
        "engagement": "1.2K",
        "posted_at": "2025-01-15T10:30:00Z",
        "sentiment": "positive",
        "relevance_score": 0.85
      }
    ],
    "pagination": {
      "total": 1250,
      "limit": 50,
      "offset": 0,
      "has_more": true
    }
  }
}
```

---

## Anomaly Detection & Alerts

### GET /data/anomalies
**Description**: Get detected anomalies and alerts
**Query Parameters**:
- `severity`: string (low, medium, high)
- `status`: string (new, acknowledged, resolved)
- `range`: string (Today, Last 7 Days, Last 30 Days, Last 90 Days)
- `limit`: number (default: 50)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "a1",
      "title": "Negative Sentiment Spike",
      "severity": "high",
      "detected_at": "2025-01-15T10:30:00Z",
      "summary": "Significant drop in sentiment over last 24h",
      "metric": "Sentiment",
      "delta": "-23%",
      "status": "new",
      "affected_keywords": ["politics", "economy"],
      "recommendations": [
        "Monitor closely for 24 hours",
        "Check for breaking news events"
      ]
    }
  ]
}
```

### GET /data/anomalies/{id}
**Description**: Get detailed anomaly information
**Path Parameters**:
- `id`: string (anomaly ID)

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "a1",
    "title": "Negative Sentiment Spike",
    "severity": "high",
    "detected_at": "2025-01-15T10:30:00Z",
    "summary": "Significant drop in sentiment over last 24h",
    "metric": "Sentiment",
    "delta": "-23%",
    "status": "new",
    "affected_keywords": ["politics", "economy"],
    "timeline": [
      {
        "timestamp": "2025-01-15T08:00:00Z",
        "value": 65,
        "baseline": 88
      }
    ],
    "related_posts": [
      {
        "handle": "@user123",
        "text": "Related post content...",
        "sentiment": "negative"
      }
    ],
    "recommendations": [
      "Monitor closely for 24 hours",
      "Check for breaking news events"
    ]
  }
}
```

---

## Alert Rules & Configuration

### GET /data/alert-rules
**Description**: Get configured alert rules
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "r1",
      "name": "Sentiment ≤ -15% day-over-day",
      "description": "Trigger when overall sentiment drops sharply in 24h",
      "enabled": true,
      "conditions": {
        "metric": "sentiment",
        "threshold": -15,
        "time_window": "24h",
        "comparison": "day_over_day"
      },
      "actions": ["email", "webhook"],
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### POST /data/alert-rules
**Description**: Create new alert rule
**Request Body**:
```json
{
  "name": "New Alert Rule",
  "description": "Rule description",
  "conditions": {
    "metric": "sentiment",
    "threshold": -15,
    "time_window": "24h",
    "comparison": "day_over_day"
  },
  "actions": ["email", "webhook"],
  "enabled": true
}
```

### PUT /data/alert-rules/{id}
**Description**: Update alert rule
**Path Parameters**:
- `id`: string (rule ID)

**Request Body**: Same as POST

### DELETE /data/alert-rules/{id}
**Description**: Delete alert rule
**Path Parameters**:
- `id`: string (rule ID)

---

## Data Source Management

### GET /data/connectors
**Description**: Get data source connectors and their status
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "x",
      "name": "X (Twitter) API",
      "description": "Search, filtered stream, historical backfill",
      "status": "connected",
      "last_sync": "2025-01-15T10:30:00Z",
      "config": {
        "api_version": "v2",
        "rate_limit_remaining": 450,
        "rate_limit_reset": "2025-01-15T11:00:00Z"
      },
      "metrics": {
        "total_posts": 1250000,
        "last_24h_posts": 45000,
        "sync_success_rate": 99.8
      }
    }
  ]
}
```

### POST /data/connectors/{id}/test
**Description**: Test data source connection
**Path Parameters**:
- `id`: string (connector ID)

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "response_time": 245,
    "last_sync": "2025-01-15T10:30:00Z",
    "errors": []
  }
}
```

### POST /data/connectors/{id}/connect
**Description**: Connect to data source
**Path Parameters**:
- `id`: string (connector ID)

**Request Body**:
```json
{
  "api_key": "string",
  "api_secret": "string",
  "access_token": "string",
  "access_token_secret": "string"
}
```

---

## AI Content Generation

### POST /ai/generate/summary
**Description**: Generate AI summary for report sections
**Request Body**:
```json
{
  "section": "overview|timeline|sentiment|narratives|geo|influencers|topPosts|claims|appendix",
  "subject": "string",
  "template": "hashtag|general|person|group",
  "range": "string",
  "context": {
    "mentions": 15000,
    "sentiment": {
      "pos": 35,
      "neg": 40,
      "neu": 25
    },
    "top_keywords": ["politics", "economy"],
    "geographic_focus": "Nigeria"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "summary": "The hashtag 'Nigeria' has generated significant online engagement over last 30 days...",
    "insights": {
      "content": "Data-driven insights for Nigeria overview show 15000 total mentions...",
      "data": {
        "totalMentions": 15000,
        "growthRate": 75,
        "peakHours": "2-4 PM",
        "avgMentionsPerHour": 150
      }
    },
    "confidence": 85,
    "generated_at": "2025-01-15T10:30:00Z"
  }
}
```

### POST /ai/generate/insights
**Description**: Generate detailed AI insights for report sections
**Request Body**: Same as summary endpoint

**Response**:
```json
{
  "success": true,
  "data": {
    "insights": {
      "content": "Detailed insights content...",
      "data": {
        "keyMetrics": ["metric1", "metric2"],
        "trends": ["trend1", "trend2"],
        "recommendations": ["rec1", "rec2"]
      }
    },
    "confidence": 90,
    "generated_at": "2025-01-15T10:30:00Z"
  }
}
```

---

## Report Generation

### POST /reports/generate
**Description**: Generate comprehensive report data
**Request Body**:
```json
{
  "template": "hashtag|general|person|group",
  "subject": "string",
  "range": "string",
  "start_date": "string (ISO date, optional)",
  "end_date": "string (ISO date, optional)",
  "sections": {
    "overview": true,
    "timeline": true,
    "sentiment": true,
    "narratives": true,
    "geo": true,
    "influencers": true,
    "topPosts": true,
    "claims": false,
    "appendix": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_123",
    "status": "generating",
    "estimated_completion": "2025-01-15T10:35:00Z",
    "progress": 25
  }
}
```

### GET /reports/{id}/status
**Description**: Check report generation status
**Path Parameters**:
- `id`: string (report ID)

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_123",
    "status": "completed",
    "progress": 100,
    "completed_at": "2025-01-15T10:35:00Z",
    "download_url": "https://api.socialmonitor.com/v1/reports/report_123/download"
  }
}
```

### GET /reports/{id}/download
**Description**: Download generated report
**Path Parameters**:
- `id`: string (report ID)

**Response**: PDF file download

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "range",
      "issue": "Invalid date range format"
    }
  }
}
```

**Common Error Codes**:
- `AUTHENTICATION_ERROR`: Invalid or expired token
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid request parameters
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `DATA_NOT_FOUND`: Requested data not available
- `INTERNAL_ERROR`: Server error

---

## Rate Limiting

- **Standard Endpoints**: 1000 requests/hour
- **AI Generation**: 100 requests/hour
- **Report Generation**: 10 requests/hour
- **Data Export**: 50 requests/hour

Rate limit headers included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 850
X-RateLimit-Reset: 1642233600
```

---

## Webhooks

### POST /webhooks/alerts
**Description**: Receive real-time alert notifications
**Headers**: `X-Webhook-Signature: <hmac_signature>`

**Request Body**:
```json
{
  "event": "anomaly_detected",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "anomaly_id": "a1",
    "severity": "high",
    "title": "Negative Sentiment Spike"
  }
}
```

---

## Data Retention & Privacy

- **Raw Data**: Retained for 90 days
- **Aggregated Data**: Retained for 2 years
- **User Data**: Retained until account deletion
- **Compliance**: GDPR compliant, data anonymization available

---

## Performance Requirements

- **Response Time**: < 200ms for data queries, < 2s for AI generation
- **Availability**: 99.9% uptime
- **Concurrent Users**: Support for 1000+ concurrent users
- **Data Freshness**: Real-time updates with < 5 minute delay

---

## Security Requirements

- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: AES-256 encryption at rest, TLS 1.3 in transit
- **API Security**: Rate limiting, input validation, SQL injection prevention
- **Audit Logging**: All API calls logged with user context
