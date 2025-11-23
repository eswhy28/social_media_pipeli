# Social Media Analytics Pipeline

A comprehensive social media monitoring and analytics platform for tracking Nigerian social media conversations with AI-powered sentiment analysis, location extraction, and real-time insights.

## 🎯 Overview

This platform provides:
- **Multi-Source Data Collection**: Twitter/X, TikTok, Facebook, Google Trends
- **AI-Powered Analysis**: Sentiment analysis, location extraction, entity recognition
- **Real-Time Insights**: Engagement metrics, trending topics, geographic analysis
- **Smart Processing**: Automatic de-duplication, incremental updates, batch processing
- **RESTful API**: Clean, well-documented endpoints for frontend integration

## 🏗️ Architecture

```
Data Sources → Scrapers → Database → AI Processing → API → Frontend
    ↓             ↓          ↓            ↓          ↓
Twitter      Apify      PostgreSQL   TextBlob    FastAPI
TikTok       Playwright               spaCy       React
Facebook     Google API                          (your choice)
```

### Technology Stack

- **Backend**: Python 3.13, FastAPI
- **Database**: PostgreSQL with AsyncPG
- **AI/ML**: TextBlob (sentiment), spaCy (NER), HuggingFace (future)
- **Scraping**: Apify, Playwright, BeautifulSoup
- **Caching**: Redis
- **Geo-coding**: Custom Nigerian location database

## 📦 Installation

### Prerequisites
- Python 3.13+
- PostgreSQL 14+
- Redis (optional, for caching)

### Setup

1. **Clone the repository**
```bash
git clone <your-repo>
cd social_media_pipeli
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL
# - APIFY_API_TOKEN (optional)
# - Other API keys as needed
```

5. **Initialize database**
```bash
python scripts/create_ai_tables.py
```

6. **Import data** (if you have JSON files)
```bash
python scripts/import_data.py
```

7. **Run the server**
```bash
# Option 1: Using uvicorn directly (recommended)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the start script
./start.sh

# Option 3: Using Python module
python -m uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`  
Documentation at: `http://localhost:8000/docs`

## 📊 Database Schema

### Core Tables

#### `apify_scraped_data`
Stores raw scraped social media data with full metadata
- Media URLs, engagement metrics, hashtags, mentions
- Author information and locations
- Platform-specific identifiers for de-duplication

#### `apify_sentiment_analysis`
AI-generated sentiment analysis results
- Positive/negative/neutral classification
- Confidence scores and polarity values
- Model tracking (TextBlob, RoBERTa, etc.)

#### `apify_location_extractions`
Extracted and geocoded locations from posts
- Location text and type (City, State, Region)
- Coordinates (latitude, longitude)
- Regional classification (Nigerian geopolitical zones)

#### `apify_data_processing_status`
Tracks which records have been processed to prevent duplication
- Per-service processing flags (sentiment, location, entity, keyword)
- Processing timestamps and error tracking
- Ensures incremental, efficient processing

## 🚀 API Endpoints

### ⭐ **PRIMARY INTELLIGENCE ENDPOINT** (Recommended)

#### **Intelligence Report** - Complete Social Media Intelligence
```http
GET /api/v1/social-media/intelligence/report
```
**The main endpoint for intelligence analysts and monitoring dashboards.**

**Query Parameters:**
- `limit` - Number of posts (default: 50, max: 500)
- `hours_back` - Time range in hours (default: 24, max: 720)
- `sentiment_filter` - Filter by sentiment: `positive`, `negative`, `neutral`
- `has_media` - Filter posts with/without images/videos: `true`/`false`
- `min_engagement` - Minimum total engagement (likes + retweets + replies)
- `include_ai_analysis` - Include AI results: `true`/`false` (default: true)

**Returns:**
- ✅ Complete post content and author info
- ✅ All media URLs (images/videos) ready for display
- ✅ AI sentiment analysis linked to each post
- ✅ Location extraction with coordinates
- ✅ Full engagement metrics
- ✅ Hashtags and mentions
- ✅ Post URLs for verification
- ✅ Summary statistics

**Examples:**
```bash
# Get posts with images only
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?has_media=true&limit=50'

# Get negative sentiment posts
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?sentiment_filter=negative'

# High engagement posts with media
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?has_media=true&min_engagement=1000'

# Last 48 hours with full analysis
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?hours_back=48&include_ai_analysis=true'
```

### Data Retrieval Endpoints

#### Get Scraped Posts
```http
GET /api/v1/social-media/data/scraped
```
**Query Parameters:**
- `platform` - Filter by platform (twitter, facebook, tiktok)
- `limit` - Number of records (default: 50, max: 500)
- `offset` - Pagination offset
- `hours_back` - Filter by time (1-720 hours)
- `has_media` - Filter posts with/without images
- `hashtag` - Filter by specific hashtag
- `location` - Filter by location

#### Geographic Analysis
```http
GET /api/v1/social-media/data/geo-analysis
```
**Query Parameters:**
- `hours_back` - Time range (default: 24)
- `platform` - Filter by platform

**Returns:** Posts grouped by location with engagement metrics, top hashtags, and coordinates.

#### Engagement Analysis
```http
GET /api/v1/social-media/data/engagement-analysis
```
**Query Parameters:**
- `hours_back` - Time range (default: 24)
- `platform` - Filter by platform
- `group_by` - Group by: `hour`, `day`, `author`, `hashtag`

**Returns:** Aggregated engagement metrics.

#### Overall Statistics
```http
GET /api/v1/social-media/data/stats
```
**Returns:** Total posts, media percentage, platform distribution, top authors, and hashtags.

### AI Processing Endpoints

#### Process Sentiment Analysis
```http
POST /api/v1/social-media/ai/process-sentiment
```
**Query Parameters:**
- `limit` - Max records to process (optional, processes all if not specified)

**Behavior:** Automatically skips already-processed records.

#### Process Location Extraction
```http
POST /api/v1/social-media/ai/process-locations
```
**Query Parameters:**
- `limit` - Max records to process (optional)

**Behavior:** Extracts and geocodes locations. Skips already-processed records.

#### Get Processing Statistics
```http
GET /api/v1/social-media/ai/processing-stats
```
**Returns:** Processing progress, total records, processed counts, unprocessed counts.

#### Get Sentiment Results
```http
GET /api/v1/social-media/ai/sentiment-results
```
**Query Parameters:**
- `limit` - Number of results (default: 50, max: 500)
- `sentiment_label` - Filter by: `positive`, `negative`, `neutral`
- `min_confidence` - Minimum confidence (0.0 to 1.0)

**Returns:** Sentiment analysis results with original posts.

#### Get Location Results
```http
GET /api/v1/social-media/ai/location-results
```
**Query Parameters:**
- `limit` - Number of results (default: 50, max: 500)
- `location_type` - Filter by type: `GPE`, `LOC`, etc.

**Returns:** Extracted locations with coordinates and regional data.

### Social Media Scraping Endpoints

#### Google Trends
```http
GET /api/v1/social-media/trends/trending
POST /api/v1/social-media/trends/analyze
GET /api/v1/social-media/trends/suggestions
```

#### TikTok
```http
POST /api/v1/social-media/tiktok/hashtag
GET /api/v1/social-media/tiktok/monitor
GET /api/v1/social-media/tiktok/analytics/{hashtag}
```

#### Facebook
```http
POST /api/v1/social-media/facebook/page
GET /api/v1/social-media/facebook/monitor
GET /api/v1/social-media/facebook/analytics/{page_name}
```

#### Apify Integration
```http
POST /api/v1/social-media/apify/scrape
GET /api/v1/social-media/apify/comprehensive
```

#### Hashtag Discovery
```http
GET /api/v1/social-media/hashtags/trending
GET /api/v1/social-media/hashtags/category/{category}
GET /api/v1/social-media/hashtags/engagement/{hashtag}
GET /api/v1/social-media/hashtags/collected-trends
POST /api/v1/social-media/hashtags/update-cache
```

### Other Endpoints

#### Authentication
```http
POST /api/v1/auth/token
GET /api/v1/auth/users/me
```

#### Reports
```http
POST /api/v1/reports/generate
GET /api/v1/reports/{report_id}/status
GET /api/v1/reports/
DELETE /api/v1/reports/{report_id}
```

#### Admin
```http
GET /api/v1/admin/alert-rules
POST /api/v1/admin/alert-rules
PUT /api/v1/admin/alert-rules/{id}
DELETE /api/v1/admin/alert-rules/{id}
GET /api/v1/admin/connectors
```

## 🎯 Quick Start Guide

### Step 1: Setup Database and Process AI
```bash
# Run the all-in-one setup script
python scripts/setup_intelligence_system.py
```

This script will:
1. Create all AI analysis tables
2. Process sentiment for all posts
3. Extract and geocode locations
4. Verify the system is ready
5. Show you test examples

### Step 2: Start the Server
```bash
uvicorn app.main:app --reload
```

### Step 3: Test the Intelligence Endpoint
```bash
# Test in browser
http://localhost:8000/docs

# Or use curl
curl 'http://localhost:8000/api/v1/social-media/intelligence/report?limit=10'
```

## 🔄 Data Processing Workflow

### 1. Data Collection
```bash
# Option A: Import from JSON files
python scripts/import_data.py

# Option B: Scrape via API
curl -X POST http://localhost:8000/api/v1/social-media/apify/scrape \
  -H "Content-Type: application/json" \
  -d '{"platform": "twitter", "target": "#Nigeria", "limit": 100}'
```

### 2. AI Processing (First Time)
```bash
# Process sentiment for all data
curl -X POST http://localhost:8000/api/v1/social-media/ai/process-sentiment

# Extract and geocode locations
curl -X POST http://localhost:8000/api/v1/social-media/ai/process-locations
```

### 3. Incremental Updates (Automatic)
```bash
# Add new data
python scripts/import_data.py  # New tweets imported

# Process only new data (automatically skips processed)
curl -X POST http://localhost:8000/api/v1/social-media/ai/process-sentiment
# Response: "Processed 50 new records, skipped 139 already processed"
```

### 4. Frontend Integration
```javascript
// Fetch posts with filters
const posts = await fetch(
  '/api/v1/social-media/data/scraped?has_media=true&limit=20'
);

// Display with images
posts.data.posts.forEach(post => {
  if (post.media.has_media) {
    displayPostWithImage(post.content, post.media.urls[0]);
  }
});

// Plot on map
const geoData = await fetch('/api/v1/social-media/data/geo-analysis');
geoData.data.geo_analysis.forEach(loc => {
  if (loc.location.coordinates) {
    addMapMarker(loc.location.coordinates.lat, loc.location.coordinates.lon);
  }
});
```

## 🛡️ De-duplication Strategy

The system prevents data duplication at three levels:

### 1. Import Level
- Checks `source_id` + `platform` before inserting
- Skips duplicates automatically
- **Result**: No duplicate tweets in database

### 2. Processing Level
- Tracks processing status per record
- Only processes unprocessed records
- Marks as processed after completion
- **Result**: Never reprocesses same data

### 3. Retrieval Level
- Frontend reads pre-processed data from database
- No on-the-fly processing
- **Result**: Fast, consistent responses

## 📁 Project Structure

```
social_media_pipeli/
├── app/
│   ├── api/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── social_media.py      # Main data & AI endpoints
│   │   ├── admin.py             # Admin endpoints
│   │   ├── reports.py           # Report generation
│   │   └── ingestion.py         # Data ingestion
│   ├── models/
│   │   ├── __init__.py          # Legacy models
│   │   ├── social_media_sources.py  # ApifyScrapedData model
│   │   └── ai_analysis.py       # AI processing models
│   ├── services/
│   │   ├── apify_service.py     # Apify integration
│   │   ├── ai_processing_service.py  # AI processing logic
│   │   ├── geocoding_service.py # Location geocoding
│   │   ├── google_trends_service.py
│   │   ├── tiktok_service.py
│   │   └── facebook_service.py
│   ├── database.py              # Database connection
│   └── main.py                  # FastAPI app
├── scripts/
│   ├── import_data.py           # Import JSON data
│   ├── create_ai_tables.py      # Create database tables
│   ├── check_db.py              # Verify database
│   └── verify_*.py              # Verification scripts
├── data/                        # JSON data files
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# API Keys (optional)
APIFY_API_TOKEN=your_apify_token

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Application
APP_NAME=Social Media Pipeline
ENVIRONMENT=development
DEBUG=True
```

## 📈 Features

### ✅ Implemented
- Multi-source data collection (Twitter, TikTok, Facebook, Google Trends)
- Comprehensive data import with de-duplication
- AI-powered sentiment analysis
- Location extraction and geocoding
- Geographic analysis with Nigerian state/region support
- Engagement metrics and trending analysis
- RESTful API with automatic documentation
- Smart incremental processing (no reprocessing)
- Batch job tracking and monitoring

### 🚧 Planned
- Advanced NER with HuggingFace models
- Topic modeling and clustering
- Influencer identification
- Automated alerts and anomaly detection
- Real-time streaming data
- Custom dashboard templates

## 🧪 Testing

```bash
# Verify data import
python scripts/verify_frontend_ready.py

# Verify AI system
python scripts/verify_ai_system.py

# Check database contents
python scripts/check_db.py

# Run all tests
pytest
```

## 📊 Performance

- **Data Import**: ~1000 tweets/second
- **Sentiment Analysis**: ~100 posts/second (TextBlob)
- **Location Geocoding**: ~500 lookups/second (cached)
- **API Response Time**: <100ms (database queries)
- **De-duplication Check**: O(1) (indexed queries)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Apify for social media scraping infrastructure
- TextBlob for sentiment analysis
- spaCy for NLP processing
- FastAPI for the excellent web framework
- PostgreSQL for reliable data storage

## 📞 Support

For issues, questions, or contributions:
- Open an issue in the GitHub repository
- Check the API documentation at `/docs` endpoint
- Review the verification scripts in `scripts/`

---

**Built with ❤️ for Nigerian Social Media Analytics**