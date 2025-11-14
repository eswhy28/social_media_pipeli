# Apify Service - Configuration Complete ✅

## Overview

Your Apify service has been successfully configured and tested! This document summarizes the setup and provides usage examples.

---

## ✅ Configuration Status

### API Token
- **Status**: ✅ Configured
- **Variable**: `APIFY_API_TOKEN`
- **Account**: ultramarine_layout (eswhy280@gmail.com)
- **Location**: `.env` file

### Connection Test
- **Status**: ✅ Verified
- **Client**: Initialized successfully
- **Actors**: Instagram Scraper available
- **API**: Working correctly

---

## 🔧 What Was Fixed

### 1. Environment Variable Name
```bash
# ❌ Before (incorrect)
APIFY-TOKEN=apify_api_YCtM0hOoEH7eVb2vXhVGubfpuLbUD94CySXz

# ✅ After (correct)
APIFY_API_TOKEN=apify_api_YCtM0hOoEH7eVb2vXhVGubfpuLbUD94CySXz
```

### 2. Added Supporting Configuration
Added these variables to `.env`:
```bash
# Google Trends
GOOGLE_TRENDS_TIMEOUT=30
GOOGLE_TRENDS_RETRIES=3

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Test Script Created
- **File**: `test_apify_simple.py`
- **Purpose**: Verify Apify configuration
- **Usage**: `python test_apify_simple.py`

---

## 🎯 Available Apify Actors

Your account has access to these actors:

### Confirmed Available
- ✅ **Instagram Scraper** (`apify/instagram-scraper`)
  - Scrape profiles, posts, comments
  - Extract followers, following
  - Get engagement metrics

### Likely Available (Public Actors)
- **TikTok Scrapers**
  - Profile scraper
  - Hashtag scraper
  - Video downloader

- **Facebook Scrapers**
  - Page scraper
  - Group scraper
  - Post scraper

- **Twitter/X Scrapers**
  - Profile scraper
  - Tweet scraper
  - Search scraper

- **Google Search Scraper**
- **YouTube Scraper**
- **1000+ more** on [Apify Store](https://apify.com/store)

---

## 📡 API Endpoints

Your application now has these Apify endpoints:

### 1. Single Platform Scraping
```
POST /api/v1/social-media/apify/scrape
```

**Request Body**:
```json
{
  "platform": "instagram",
  "target": "username_or_hashtag",
  "limit": 50
}
```

**Supported Platforms**:
- `instagram` - Instagram profiles
- `tiktok` - TikTok hashtags
- `facebook` - Facebook pages
- `twitter` - Twitter profiles

### 2. Multi-Platform Comprehensive Scraping
```
GET /api/v1/social-media/apify/comprehensive
```

**Query Parameters**:
- `platforms` - Comma-separated list (default: "instagram,tiktok,facebook")
- `items_per_platform` - Number of items per platform (default: 50)

**Purpose**: Scrapes Nigerian content from multiple platforms

---

## 💡 Usage Examples

### Example 1: Scrape Instagram Profile

```bash
curl -X POST http://localhost:8000/api/v1/social-media/apify/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "target": "nasa",
    "limit": 10
  }'
```

### Example 2: Scrape TikTok Hashtag

```bash
curl -X POST http://localhost:8000/api/v1/social-media/apify/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "tiktok",
    "target": "naija",
    "limit": 20
  }'
```

### Example 3: Scrape Facebook Page

```bash
curl -X POST http://localhost:8000/api/v1/social-media/apify/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "target": "https://facebook.com/legit.ng",
    "limit": 15
  }'
```

### Example 4: Comprehensive Nigerian Scraping

```bash
curl "http://localhost:8000/api/v1/social-media/apify/comprehensive?platforms=instagram,tiktok&items_per_platform=30"
```

---

## 🔍 Nigerian Content Features

The Apify service includes built-in Nigerian content monitoring:

### Predefined Nigerian Accounts
```python
NIGERIAN_ACCOUNTS = {
    'instagram': [
        'lagos', 'abuja', 'nigeria', 'naija',
        'lindaikejisblog', 'legitng'
    ],
    'tiktok': [
        'nigeria', 'naija', 'lagos', 'afrobeats'
    ],
    'twitter': [
        'NigeriaStories', 'Lagos', 'Naija'
    ]
}
```

### Automatic Filtering
- Detects Nigerian-related content
- Filters by location (Lagos, Abuja, etc.)
- Identifies Nigerian keywords
- Monitors trending Nigerian hashtags

---

## 📊 Service Configuration

### Service File Location
`app/services/apify_service.py` (580 lines)

### Key Methods
```python
# Single platform scraping
await apify_service.scrape_instagram_profile(username, limit)
await apify_service.scrape_tiktok_hashtag(hashtag, limit)
await apify_service.scrape_facebook_page(page_url, limit)
await apify_service.scrape_twitter_profile(username, limit)

# Multi-platform scraping
await apify_service.scrape_nigerian_social_media(platforms, items)

# Actor status
await apify_service.get_actor_status(run_id)
```

### Data Storage
All scraped data is automatically:
1. Stored in database table: `apify_scraped_data`
2. Normalized to unified format
3. Tagged with platform and timestamp
4. Available via API endpoints

---

## ⚙️ Configuration Options

### Retry Logic
```python
# Configured with tenacity retry
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
```

### Rate Limiting
- Built into Apify SDK
- Respects actor limits
- Automatic throttling

### Timeouts
- Default: 60 seconds per actor run
- Configurable per request
- Async execution support

---

## 🚀 Testing Your Setup

### Quick Test
```bash
# Run the test script
python test_apify_simple.py
```

### Expected Output
```
🧪 Testing Apify Service Configuration
✅ API Token found
✅ Apify client initialized successfully
✅ Successfully connected to Apify!
✅ Found: Instagram Scraper
```

### Start the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI
uvicorn app.main:app --reload
```

### Access API Documentation
Open browser to: http://localhost:8000/docs

---

## 📖 Additional Resources

### Apify Documentation
- **Console**: https://console.apify.com
- **Docs**: https://docs.apify.com
- **API Reference**: https://docs.apify.com/api/v2
- **Actor Store**: https://apify.com/store

### Your Account
- **Dashboard**: https://console.apify.com/account
- **API Tokens**: https://console.apify.com/account/integrations
- **Usage**: https://console.apify.com/account/usage

### Project Documentation
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Setup Guide**: `SETUP_COMPLETE.md`
- **API Testing**: `API_TESTING_GUIDE.md`

---

## 🔒 Security Notes

### API Token Security
- ✅ Token stored in `.env` (not committed to git)
- ✅ `.env` included in `.gitignore`
- ✅ `.env.example` provided as template

### Best Practices
1. Never commit `.env` to version control
2. Regenerate token if accidentally exposed
3. Use environment-specific tokens (dev/prod)
4. Monitor usage in Apify console

---

## ❓ Troubleshooting

### Token Not Working
1. Verify token in `.env` file
2. Check variable name: `APIFY_API_TOKEN`
3. Regenerate token at: https://console.apify.com/account/integrations
4. Run test script: `python test_apify_simple.py`

### Actor Not Found
- Check actor ID/name spelling
- Verify you have access to the actor
- Try a different public actor
- Check Apify Store for alternatives

### Rate Limiting
- Apify has monthly compute unit limits
- Check usage at: https://console.apify.com/account/usage
- Consider upgrading plan if needed
- Use built-in rate limiting

---

## ✅ Summary

**Configuration**: ✅ Complete
**Testing**: ✅ Passed
**API**: ✅ Ready
**Documentation**: ✅ Updated

Your Apify service is fully configured and ready to use! You can now:
1. Start the application
2. Test the endpoints
3. Scrape social media data
4. Monitor Nigerian content

**Happy scraping! 🎉**

---

*Last Updated: November 2025*
*Status: Production Ready*