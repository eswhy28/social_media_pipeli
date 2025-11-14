# 🇳🇬 Nigerian Data Collection - Quick Start Guide

## Overview

This guide shows you how to collect Nigerian trending content and populate your database for AI analysis.

---

## 🎯 What Gets Collected

### Data Sources
1. **Google Trends** - Trending searches in Nigeria
2. **TikTok** - Nigerian hashtags (#nigeria, #naija, #lagos, etc.)
3. **Facebook** - Nigerian news pages (legit.ng, lindaikejisblog, etc.)
4. **Twitter** - Nigerian news accounts (via Apify)

### Topics Covered
- **Politics** - Elections, government, policies
- **Economy** - Naira rate, fuel prices, inflation
- **Security** - Safety, crime, military
- **Sports** - Super Eagles, AFCON, athletes
- **Entertainment** - Nollywood, Afrobeats, BBNaija
- **Technology** - Startups, fintech, innovation
- **Health** - Healthcare, outbreaks, medical news
- **Education** - ASUU strikes, JAMB, universities
- **Social** - Youth movements, EndSARS, activism

---

## 🚀 Method 1: Manual Collection (Quick Test)

### Step 1: Start the API Server
```bash
# Terminal 1 - Start API
cd /home/mukhtar/Documents/social_media_pipeli
source venv/bin/activate
uvicorn app.main:app --reload
```

### Step 2: Run Data Collection Script
```bash
# Terminal 2 - Run collector
source venv/bin/activate
python collect_nigerian_data.py
```

**What it does:**
- Collects Google Trends for Nigeria
- Analyzes trending keywords
- Scrapes TikTok Nigerian content
- Scrapes Facebook Nigerian pages
- Optionally scrapes Twitter (if Apify configured)
- Runs AI analysis on collected content

**Expected Output:**
```
🇳🇬 NIGERIAN DATA COLLECTION PIPELINE
=====================================
📊 Collecting Google Trends data...
   ✅ Collected 20 trending searches
🔍 Analyzing trending keywords...
   ✅ Analyzed 5 keywords
🎵 Collecting TikTok Nigerian content...
   ✅ Collected 15 TikTok videos
📘 Collecting Facebook Nigerian pages...
   ✅ Collected 25 Facebook posts
🐦 Collecting Twitter data via Apify...
   ✅ Collected 10 tweets
🤖 Running AI analysis on collected content...
   ✅ Analyzed 5 text samples

📊 COLLECTION SUMMARY
================================
Google Trends: 25
TikTok Videos: 15
Facebook Posts: 25
Twitter Tweets: 10
Total Items: 75
================================
```

---

## ⚙️ Method 2: Automated Collection (Background Tasks)

### Step 1: Start Redis
```bash
# Terminal 1 - Redis
redis-server
```

### Step 2: Start Celery Worker
```bash
# Terminal 2 - Celery Worker
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

### Step 3: Start Celery Beat (Scheduler)
```bash
# Terminal 3 - Celery Beat
source venv/bin/activate
celery -A app.celery_app beat --loglevel=info
```

### Step 4: Start API
```bash
# Terminal 4 - API Server
source venv/bin/activate
uvicorn app.main:app --reload
```

**What happens:**
- Data collection runs automatically at scheduled intervals:
  - **Google Trends**: Every hour
  - **TikTok**: Every 2 hours
  - **Facebook**: Every 3 hours
  - **Analytics**: Every hour
  - **Counter Reset**: Daily at midnight

**Monitor logs** to see collection happening in real-time!

---

## 📊 Method 3: Use API Endpoints Directly

### Collect Google Trends
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/trends/trending?region=NG"
```

### Analyze Keywords
```bash
curl -X POST "http://localhost:8000/api/v1/social-media/trends/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["Tinubu", "Naira", "Nigeria"],
    "timeframe": "today 3-m",
    "include_related": true
  }'
```

### Collect TikTok Nigerian Content
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/tiktok/monitor?max_videos=20"
```

### Collect Facebook Nigerian Pages
```bash
curl -X GET "http://localhost:8000/api/v1/social-media/facebook/monitor?pages_per_source=2"
```

### Twitter via Apify (if configured)
```bash
curl -X POST "http://localhost:8000/api/v1/social-media/apify/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "target": "NigeriaStories",
    "limit": 20
  }'
```

---

## 🤖 AI Analysis on Collected Data

### Run Comprehensive Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/ai/analyze/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "President Tinubu announced new economic policies in Lagos. Nigerian citizens react positively to infrastructure investments."
  }'
```

**Features:**
- Sentiment analysis (positive/negative/neutral)
- Location extraction (Lagos, Abuja, etc.)
- Entity recognition (people, organizations)
- Keyword extraction

---

## 🔍 Verify Data Collection

### Check Database
```bash
sqlite3 social_media.db <<EOF
SELECT COUNT(*) as google_trends FROM google_trends_data;
SELECT COUNT(*) as tiktok FROM tiktok_content;
SELECT COUNT(*) as facebook FROM facebook_content;
SELECT COUNT(*) as apify FROM apify_scraped_data;
EOF
```

### Check via API
```bash
# Get recent posts
curl "http://localhost:8000/api/v1/data/posts/recent?limit=10"

# Get trending hashtags
curl "http://localhost:8000/api/v1/data/hashtags/trending?limit=20"

# Get platform stats
curl "http://localhost:8000/api/v1/data/stats"
```

### Check Health
```bash
curl "http://localhost:8000/health"
```

---

## 📋 Nigerian Topics Configuration

The system automatically focuses on:

### Categories (9)
1. Politics (Tinubu, INEC, elections)
2. Economy (Naira, CBN, fuel prices)
3. Security (Boko Haram, kidnapping)
4. Sports (Super Eagles, Osimhen)
5. Entertainment (Nollywood, Afrobeats)
6. Technology (Startups, fintech)
7. Education (ASUU, JAMB)
8. Health (NCDC, healthcare)
9. Social (EndSARS, youth movements)

### Locations (52)
- **36 States** + FCT
- **15 Major Cities** (Lagos, Abuja, Kano, etc.)
- **6 Regions** (South West, North East, etc.)

### Sources
- **12 Twitter Accounts** (NigeriaStories, ChannelsTV, etc.)
- **8 Facebook Pages** (legit.ng, lindaikejisblog, etc.)
- **100+ Keywords** across all categories
- **50+ Hashtags** for tracking

---

## 🎯 Priority Topics by Time

The system automatically adjusts collection priorities:

**Morning (6 AM - 12 PM)**: Politics, Economy, Security
**Afternoon (12 PM - 6 PM)**: Economy, Technology, Education
**Evening (6 PM - 11 PM)**: Entertainment, Sports, Social
**Night (11 PM - 6 AM)**: Security, Social

---

## 📈 Expected Data Volume

### Per Collection Run
- Google Trends: 15-20 items
- TikTok: 10-30 videos
- Facebook: 20-40 posts
- Twitter: 10-20 tweets (if Apify configured)

### Daily (with automation)
- ~500-800 items collected
- ~50-100 AI analyses
- ~200-300 hashtags tracked
- ~100-150 locations identified

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
APIFY_API_TOKEN=your_token_here  # For Twitter scraping

# Optional (other services work without API keys)
TWITTER_BEARER_TOKEN=
GOOGLE_TRENDS_TIMEOUT=30
GOOGLE_TRENDS_RETRIES=3

# Redis (for background tasks)
REDIS_HOST=localhost
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Nigerian Topics Config
Edit `app/nigerian_topics_config.py` to:
- Add/remove keywords
- Change collection priorities
- Add new Twitter accounts
- Add new Facebook pages
- Adjust time-based priorities

---

## 🚨 Troubleshooting

### No Data Collected
**Problem**: Collection script returns 0 items
**Solutions**:
1. Check API server is running: `curl http://localhost:8000/health`
2. Check network connection
3. Verify services are configured correctly
4. Check logs for errors

### Twitter Not Working
**Problem**: Twitter collection fails
**Solution**: Twitter requires Apify token. Add to `.env`:
```bash
APIFY_API_TOKEN=your_token_here
```

### Celery Tasks Not Running
**Problem**: Automated collection not working
**Solutions**:
1. Start Redis: `redis-server`
2. Start Celery worker: `celery -A app.celery_app worker`
3. Start Celery beat: `celery -A app.celery_app beat`
4. Check Redis is accessible

### Database Errors
**Problem**: Database write errors
**Solutions**:
1. Run migrations: `alembic upgrade head`
2. Check database file permissions
3. Verify tables exist: `sqlite3 social_media.db ".tables"`

---

## 📚 Additional Resources

### API Documentation
- Interactive: http://localhost:8000/docs
- Alternative: http://localhost:8000/redoc

### Project Documentation
- **IMPLEMENTATION_SUMMARY.md** - Full architecture
- **API_TESTING_GUIDE.md** - All API endpoints
- **APIFY_SETUP_COMPLETE.md** - Apify configuration
- **SETUP_COMPLETE.md** - Complete setup guide

### Configuration Files
- **app/nigerian_topics_config.py** - Topics & keywords
- **app/tasks/social_media_collection.py** - Background tasks
- **collect_nigerian_data.py** - Manual collection script

---

## ✅ Quick Checklist

Before starting collection, ensure:

- [ ] API server is running (`uvicorn app.main:app --reload`)
- [ ] Database migrations complete (`alembic upgrade head`)
- [ ] Redis running (for background tasks)
- [ ] Apify token configured (for Twitter)
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## 🎯 Success Metrics

After running collection, you should see:

- ✅ Data in database tables
- ✅ API endpoints returning data
- ✅ AI analysis results
- ✅ Trending hashtags identified
- ✅ Locations extracted
- ✅ Sentiment scores calculated

---

**Your Nigerian data collection pipeline is ready! 🇳🇬 🚀**

Run `python collect_nigerian_data.py` to start collecting now!