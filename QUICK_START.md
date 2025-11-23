# 🚀 QUICK START - Test Your Intelligence System

## Step 1: Run the Setup Script (ONE Command)

```bash
python scripts/setup_intelligence_system.py
```

This single script will:
1. ✅ Create all AI tables
2. ✅ Process sentiment analysis (if not done)
3. ✅ Extract locations (if not done)
4. ✅ Verify everything is working
5. ✅ Show you test examples

**Expected output:**
- Creates 6 AI analysis tables
- Processes 139 posts for sentiment
- Extracts locations from posts
- Displays sample intelligence report
- Shows API endpoint examples

## Step 2: Start the Server

```bash
uvicorn app.main:app --reload
```

Server will be available at: `http://localhost:8000`

## Step 3: Test the Intelligence Endpoint

### Option A: Interactive API Docs (Easiest)
1. Open browser: `http://localhost:8000/docs`
2. Find "Social Media" section
3. Look for `GET /intelligence/report`
4. Click "Try it out"
5. Set parameters and click "Execute"

### Option B: Using curl

```bash
# Basic intelligence report
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?limit=10'

# Posts with images only
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?has_media=true&limit=20'

# Negative sentiment posts
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?sentiment_filter=negative&limit=10'

# High engagement posts
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?min_engagement=1000'

# Full intelligence report (last 48 hours)
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?hours_back=48&include_ai_analysis=true&limit=100'
```

### Option C: Using Python Requests

```python
import requests

# Get intelligence report
response = requests.get(
    'http://localhost:8000/api/v1/social-media/intelligence/report',
    params={
        'limit': 20,
        'has_media': True,
        'include_ai_analysis': True
    }
)

data = response.json()

# Display results
for report in data['data']['reports']:
    print(f"Author: @{report['author']['username']}")
    print(f"Content: {report['content']['text'][:100]}...")
    print(f"Sentiment: {report['ai_analysis']['sentiment']['label']}")
    print(f"Engagement: {report['engagement']['total']}")
    print(f"Media: {len(report['media']['urls'])} images/videos")
    print("---")
```

## 📊 What You'll See

### Summary Statistics
```json
{
  "summary": {
    "total_posts": 50,
    "posts_with_media": 20,
    "total_engagement": 125430,
    "sentiment_distribution": {
      "positive": 18,
      "negative": 22,
      "neutral": 10
    }
  }
}
```

### Each Post Contains
```json
{
  "author": {"username": "...", "location": "..."},
  "content": {"text": "...", "url": "..."},
  "media": {"urls": ["image1.jpg", "image2.jpg"]},
  "engagement": {"likes": 52, "retweets": 42, "views": 3320},
  "ai_analysis": {
    "sentiment": {"label": "negative", "confidence": 0.78},
    "locations": [{"text": "Lagos", "coordinates": {...}}]
  }
}
```

## 🎯 All Available Endpoints (From README.md)

See `README.md` for complete list. Main endpoints:

### Intelligence (Recommended)
- `GET /intelligence/report` - Complete intelligence data

### Data Retrieval
- `GET /data/scraped` - Raw scraped data
- `GET /data/geo-analysis` - Geographic analysis
- `GET /data/engagement-analysis` - Engagement metrics
- `GET /data/stats` - Overall statistics

### AI Processing
- `POST /ai/process-sentiment` - Run sentiment analysis
- `POST /ai/process-locations` - Extract locations
- `GET /ai/processing-stats` - Check processing status
- `GET /ai/sentiment-results` - View sentiment results
- `GET /ai/location-results` - View location results

## ✅ System is Ready When

- ✅ Setup script completes without errors
- ✅ Server starts at http://localhost:8000
- ✅ `/docs` page shows all endpoints
- ✅ Intelligence endpoint returns data with sentiment and locations

## 🆘 If Something Goes Wrong

1. **Database connection error**
   - Check `.env` file has correct `DATABASE_URL`
   - Verify PostgreSQL is running

2. **No data returned**
   - Run: `python scripts/check_db.py`
   - Should show 139 posts

3. **No AI analysis**
   - Run: `python scripts/setup_intelligence_system.py`
   - This will process everything

4. **Server won't start**
   - Check port 8000 is not in use
   - Activate virtual environment: `source venv/bin/activate`

## 🎉 Success Criteria

Your system is working perfectly when:
1. ✅ Setup script shows "SETUP COMPLETE"
2. ✅ Server runs at http://localhost:8000
3. ✅ Intelligence endpoint returns posts with:
   - Author information ✅
   - Post content ✅
   - Media URLs (if has_media=true) ✅
   - Sentiment analysis results ✅
   - Location extractions ✅
   - Engagement metrics ✅

---

**You're ready to build your intelligence dashboard!** 🚀
