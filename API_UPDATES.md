# API Updates Summary

## Changes Made (2025-11-25)

### 1. Extended Time Ranges for Downloaded Data ✅
**Changed:** All `hours_back` parameters now support up to **8760 hours (1 year)**

**Affected Endpoints:**
- `/social-media/data/scraped` - Now supports up to 1 year
- `/social-media/data/geo-analysis` - Now supports up to 1 year
- `/social-media/data/engagement-analysis` - Now supports up to 1 year
- `/social-media/ai/location-results` - Now supports up to 1 year
- `/social-media/intelligence/report` - Now supports up to 1 year
- `/social-media/hashtags/engagement/{hashtag}` - Now supports up to 1 year
- `/social-media/hashtags/collected-trends` - Now supports up to 1 year

**Reason:** Since you're using downloaded/historical data rather than real-time scraping, you need access to longer time ranges.

---

### 2. Enhanced Location Results Endpoint ✅
**Endpoint:** `GET /api/v1/social-media/ai/location-results`

**What Changed:**
- Now returns **FULL POST DATA** alongside location information
- Added `hours_back` parameter for time filtering
- Includes media URLs, author info, engagement metrics

**New Response Format:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "location": {
          "text": "Lagos",
          "type": "GPE",
          "confidence": 0.95,
          "coordinates": {"lat": 6.5244, "lon": 3.3792},
          "region": "South West",
          "state_province": "Lagos",
          "city": "Lagos",
          "country": "Nigeria"
        },
        "post": {
          "id": "post123",
          "source_id": "1234567890",
          "platform": "twitter",
          "content": "Great event happening in Lagos!",
          "author": {
            "username": "johndoe",
            "account_name": "John Doe"
          },
          "media": {
            "urls": ["https://example.com/image1.jpg"],
            "count": 1,
            "has_media": true
          },
          "engagement": {
            "likes": 150,
            "retweets": 30,
            "replies": 10
          },
          "hashtags": ["#Lagos", "#Nigeria"],
          "posted_at": "2025-11-25T10:00:00Z",
          "url": "https://twitter.com/johndoe/status/1234567890"
        }
      }
    ],
    "count": 1,
    "filters": {
      "location_type": null,
      "hours_back": null
    }
  }
}
```

---

### 3. NEW: Posts With Media Endpoint ✅
**Endpoint:** `GET /api/v1/social-media/data/with-media`

**Purpose:** Dedicated endpoint for retrieving posts that contain images or videos.

**Query Parameters:**
- `media_type` (optional): Filter by "image", "video", or leave empty for all
- `platform` (optional): Filter by platform
- `limit` (default: 50, max: 500): Number of posts
- `offset` (default: 0): Pagination
- `hours_back` (optional, max: 8760): Time range in hours

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "post123",
        "source_id": "1234567890",
        "platform": "twitter",
        "author": {
          "username": "johndoe",
          "account_name": "John Doe"
        },
        "content": "Check out this amazing photo!",
        "content_type": "tweet",
        "media": {
          "all_urls": [
            "https://pbs.twimg.com/media/image1.jpg",
            "https://pbs.twimg.com/media/video1.mp4"
          ],
          "images": ["https://pbs.twimg.com/media/image1.jpg"],
          "videos": ["https://pbs.twimg.com/media/video1.mp4"],
          "total_count": 2,
          "image_count": 1,
          "video_count": 1,
          "has_images": true,
          "has_videos": true,
          "primary_url": "https://pbs.twimg.com/media/image1.jpg",
          "primary_type": "image"
        },
        "engagement": {
          "likes": 200,
          "retweets": 50,
          "replies": 15,
          "views": 5000
        },
        "hashtags": ["#Photography", "#Nigeria"],
        "mentions": ["@user2"],
        "location": "Lagos",
        "posted_at": "2025-11-25T10:00:00Z",
        "url": "https://twitter.com/johndoe/status/1234567890"
      }
    ],
    "count": 1,
    "limit": 50,
    "offset": 0,
    "filters": {
      "media_type": "image",
      "platform": "twitter",
      "hours_back": 168
    },
    "summary": {
      "total_media_items": 2,
      "total_images": 1,
      "total_videos": 1
    },
    "timestamp": "2025-11-25T22:40:00Z"
  }
}
```

**Features:**
- ✅ Only returns posts WITH media (images or videos)
- ✅ Categorizes media into images and videos
- ✅ Provides direct URLs to all media files
- ✅ Includes primary media URL for thumbnails
- ✅ Full post content and engagement metrics
- ✅ Supports filtering by media type
- ✅ Pagination support
- ✅ Summary statistics (total media items, images, videos)

---

## Usage Examples

### 1. Get All Posts with Images
```bash
curl "http://localhost:8000/api/v1/social-media/data/with-media?media_type=image&limit=20"
```

### 2. Get Recent Video Posts
```bash
curl "http://localhost:8000/api/v1/social-media/data/with-media?media_type=video&hours_back=168"
```

### 3. Get All Media Posts from Twitter
```bash
curl "http://localhost:8000/api/v1/social-media/data/with-media?platform=twitter&limit=50"
```

### 4. Get Location Results with Post Data (1 week)
```bash
curl "http://localhost:8000/api/v1/social-media/ai/location-results?hours_back=168&limit=100"
```

### 5. Get Data from Last Year
```bash
curl "http://localhost:8000/api/v1/social-media/data/scraped?hours_back=8760&has_media=true&limit=100"
```

---

## Frontend Integration

### Display Posts with Images

```javascript
// Fetch posts with images
const response = await fetch(
  '/api/v1/social-media/data/with-media?media_type=image&limit=20'
);
const data = await response.json();

// Display posts
data.data.posts.forEach(post => {
  const imageUrl = post.media.primary_url;
  const content = post.content;
  const author = post.author.username;
  
  // Your rendering logic here
  displayPost(imageUrl, content, author);
});
```

### Display Location Map with Posts

```javascript
// Fetch locations with full post data
const response = await fetch(
  '/api/v1/social-media/ai/location-results?hours_back=168&limit=100'
);
const data = await response.json();

// Plot on map with post previews
data.data.results.forEach(item => {
  const coords = item.location.coordinates;
  const post = item.post;
  
  if (coords) {
    addMapMarker({
      lat: coords.lat,
      lon: coords.lon,
      popup: {
        content: post.content,
        author: post.author.username,
        media: post.media.urls[0],  // Show first image
        engagement: post.engagement.likes
      }
    });
  }
});
```

---

## Summary

✅ **Time Ranges:** Extended to 8760 hours (1 year) for all data endpoints  
✅ **Location Results:** Now includes full post data (content, media, author, engagement)  
✅ **New Media Endpoint:** `/data/with-media` for easy media retrieval  
✅ **Media Categorization:** Automatic image/video detection and categorization  
✅ **Frontend Ready:** All endpoints optimized for frontend consumption  

---

**Updated:** 2025-11-25  
**API Version:** 0.1.0  
**Database:** PostgreSQL
