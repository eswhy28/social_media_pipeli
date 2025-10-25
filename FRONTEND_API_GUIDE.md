# API Integration Guide for Frontend Developers

## Base URL
```
http://localhost:8000
```

## Authentication

### Step 1: Get Access Token

**Endpoint:** `POST /api/v1/auth/token`

**Request:**
```javascript
const formData = new URLSearchParams();
formData.append('username', 'demo');
formData.append('password', 'demo123');

const response = await fetch('http://localhost:8000/api/v1/auth/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: formData
});

const { access_token } = await response.json();
```

### Step 2: Use Token in Requests

Include the token in the Authorization header:
```javascript
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};
```

## API Response Format

All endpoints return data in this format:
```json
{
  "success": true,
  "data": { /* your data here */ },
  "error": null
}
```

## Quick Start Examples

### 1. Dashboard Overview

```javascript
const overview = await fetch(
  'http://localhost:8000/api/v1/data/overview?range=Last 7 Days',
  { headers }
).then(r => r.json());

console.log(overview.data);
// {
//   "sentiment": { "positive": 190, "neutral": 542, "negative": 68 },
//   "total_posts": 800,
//   "total_engagement": 14152214,
//   "unique_users": 34
// }
```

### 2. Live Sentiment Score

```javascript
const sentiment = await fetch(
  'http://localhost:8000/api/v1/data/sentiment/live',
  { headers }
).then(r => r.json());

console.log(sentiment.data.sentiment_score); // -100 to +100
```

### 3. Recent Posts

```javascript
const posts = await fetch(
  'http://localhost:8000/api/v1/data/posts/recent?limit=20',
  { headers }
).then(r => r.json());

console.log(posts.data.posts); // Array of post objects
```

### 4. Trending Hashtags

```javascript
const hashtags = await fetch(
  'http://localhost:8000/api/v1/data/hashtags/trending?limit=10',
  { headers }
).then(r => r.json());

console.log(hashtags.data.hashtags);
// [{ "tag": "#Nigeria", "count": 631 }, ...]
```

### 5. Search Posts

```javascript
const searchResults = await fetch(
  'http://localhost:8000/api/v1/data/posts/search?q=Nigeria&limit=20',
  { headers }
).then(r => r.json());

console.log(searchResults.data);
// {
//   "posts": [...],
//   "pagination": { "total": 150, "has_more": true }
// }
```

### 6. Top Posts by Engagement

```javascript
const topPosts = await fetch(
  'http://localhost:8000/api/v1/data/posts/top?limit=10&min_engagement=1000',
  { headers }
).then(r => r.json());

console.log(topPosts.data); // Array of top posts
```

### 7. Sentiment Time Series

```javascript
const series = await fetch(
  'http://localhost:8000/api/v1/data/sentiment/series?granularity=day',
  { headers }
).then(r => r.json());

console.log(series.data.series);
// [{ "name": "Mon", "pos": 35, "neg": 20, "neu": 5 }, ...]
```

### 8. Hashtag Details

```javascript
const hashtagDetail = await fetch(
  'http://localhost:8000/api/v1/data/hashtags/Nigeria',
  { headers }
).then(r => r.json());

console.log(hashtagDetail.data);
// {
//   "title": "#Nigeria",
//   "mentions": 631,
//   "sentiment": { "pos": 300, "neg": 100, "neu": 231 },
//   "top_posts": [...]
// }
```

### 9. Influencers

```javascript
const influencers = await fetch(
  'http://localhost:8000/api/v1/data/influencers?limit=20',
  { headers }
).then(r => r.json());

console.log(influencers.data);
// [{ "handle": "@ChannelsTV", "engagement": 10900, ... }]
```

### 10. Geographic Data

```javascript
const geoData = await fetch(
  'http://localhost:8000/api/v1/data/geographic/states?range=Last 7 Days',
  { headers }
).then(r => r.json());

console.log(geoData.data);
// [{ "state": "Lagos", "mentions": 125000, "percentage": 72, ... }]
```

### 11. Anomalies

```javascript
const anomalies = await fetch(
  'http://localhost:8000/api/v1/data/anomalies?severity=high',
  { headers }
).then(r => r.json());

console.log(anomalies.data);
// [{ "id": "a1", "title": "Sentiment Spike", "severity": "high", ... }]
```

### 12. Overall Statistics

```javascript
const stats = await fetch(
  'http://localhost:8000/api/v1/data/stats',
  { headers }
).then(r => r.json());

console.log(stats.data);
// {
//   "total_posts": 800,
//   "total_engagement": 14152214,
//   "unique_users": 34,
//   "sentiment": { "positive": 190, "neutral": 542, "negative": 68 }
// }
```

## Complete React/Vue Example

```javascript
import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

function Dashboard() {
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);

  // Login on mount
  useEffect(() => {
    async function login() {
      const formData = new URLSearchParams();
      formData.append('username', 'demo');
      formData.append('password', 'demo123');

      const response = await fetch(`${API_BASE}/api/v1/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      const { access_token } = await response.json();
      setToken(access_token);
    }

    login();
  }, []);

  // Fetch dashboard data
  useEffect(() => {
    if (!token) return;

    async function fetchData() {
      const headers = {
        'Authorization': `Bearer ${token}`
      };

      const [overview, sentiment, posts, hashtags] = await Promise.all([
        fetch(`${API_BASE}/api/v1/data/overview`, { headers }).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/data/sentiment/live`, { headers }).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/data/posts/recent?limit=10`, { headers }).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/data/hashtags/trending?limit=5`, { headers }).then(r => r.json())
      ]);

      setData({
        overview: overview.data,
        sentiment: sentiment.data,
        posts: posts.data.posts,
        hashtags: hashtags.data.hashtags
      });
    }

    fetchData();
  }, [token]);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>Social Media Dashboard</h1>
      
      <div className="sentiment-score">
        <h2>Sentiment: {data.sentiment.sentiment_score}</h2>
      </div>

      <div className="stats">
        <p>Total Posts: {data.overview.total_posts}</p>
        <p>Total Engagement: {data.overview.total_engagement}</p>
        <p>Unique Users: {data.overview.unique_users}</p>
      </div>

      <div className="trending-hashtags">
        <h3>Trending Hashtags</h3>
        {data.hashtags.map(tag => (
          <div key={tag.tag}>
            {tag.tag}: {tag.count} mentions
          </div>
        ))}
      </div>

      <div className="recent-posts">
        <h3>Recent Posts</h3>
        {data.posts.map(post => (
          <div key={post.id}>
            <strong>{post.handle}</strong>: {post.text}
            <br />
            <small>Sentiment: {post.sentiment} | Engagement: {post.engagement_total}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Query Parameters

### Date Ranges
- `range`: "Today" | "Last 7 Days" | "Last 30 Days" | "Last 90 Days" | "Custom"
- `start_date`: ISO date string (required if range=Custom)
- `end_date`: ISO date string (required if range=Custom)

### Pagination
- `limit`: Number of results (default: 10-50 depending on endpoint)
- `offset`: Skip N results (for pagination)

### Filtering
- `sentiment`: "positive" | "negative" | "neutral"
- `min_engagement`: Minimum engagement count
- `severity`: "low" | "medium" | "high" (for anomalies)

## Error Handling

```javascript
try {
  const response = await fetch(url, { headers });
  const result = await response.json();
  
  if (!result.success) {
    console.error('API Error:', result.error);
  } else {
    console.log('Data:', result.data);
  }
} catch (error) {
  console.error('Network Error:', error);
}
```

## Rate Limiting

- Standard endpoints: 1000 requests/hour
- All responses include rate limit headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## CORS Configuration

The API is configured to accept requests from any origin (`*`) in development.

For production, update the `CORS_ORIGINS` environment variable to your frontend domain.

## Testing the API

Use the interactive documentation:
```
http://localhost:8000/docs
```

This provides a complete Swagger UI where you can:
1. Authenticate with demo credentials
2. Test all endpoints interactively
3. See request/response examples
4. Download OpenAPI specification

## Support

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Redoc: http://localhost:8000/redoc

