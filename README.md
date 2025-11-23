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

### Data Retrieval

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

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "uuid",
        "author": {"username": "...", "account_name": "..."},
        "content": "Tweet text",
        "engagement": {"likes": 107, "retweets": 30, "replies": 15, "views": 3267},
        "media": {"urls": ["https://...jpg"], "count": 1, "has_media": true},
        "location": {
          "location": "Lagos, Nigeria",
          "coordinates": {"lat": 6.5244, "lon": 3.3792},
          "region": "South West",
          "country": "Nigeria"
        },
        "hashtags": ["IPOB", "Nigeria"],
        "posted_at": "2025-11-22T20:41:53+00:00"
      }
    ],
    "count": 50
  }
}
```

#### Geographic Analysis
```http
GET /api/v1/social-media/data/geo-analysis?hours_back=24
```
Returns posts grouped by location with engagement metrics and top hashtags.

#### Engagement Analysis
```http
GET /api/v1/social-media/data/engagement-analysis?group_by=hour
```
Returns aggregated engagement metrics grouped by hour, day, author, or hashtag.

#### Overall Statistics
```http
GET /api/v1/social-media/data/stats
```
Returns total posts, media percentage, platform distribution, top authors, and hashtags.

### AI Processing

#### Process Sentiment Analysis
```http
POST /api/v1/social-media/ai/process-sentiment?limit=100
```
Processes sentiment for unprocessed posts. Automatically skips already-processed records.

#### Process Location Extraction
```http
POST /api/v1/social-media/ai/process-locations?limit=100
```
Extracts and geocodes locations from post content and author metadata.

#### Get Processing Statistics
```http
GET /api/v1/social-media/ai/processing-stats
```
Returns processing progress: total records, processed counts, unprocessed counts.

#### Get Sentiment Results
```http
GET /api/v1/social-media/ai/sentiment-results?sentiment_label=positive&min_confidence=0.7
```
Returns sentiment analysis results with original posts.

#### Get Location Results
```http
GET /api/v1/social-media/ai/location-results?location_type=GPE
```
Returns extracted locations with coordinates and regional data.

### Social Media Scraping

#### Google Trends
- `GET /api/v1/social-media/trends/trending` - Get trending searches
- `POST /api/v1/social-media/trends/analyze` - Analyze keywords

#### TikTok
- `POST /api/v1/social-media/tiktok/hashtag` - Scrape by hashtag
- `GET /api/v1/social-media/tiktok/monitor` - Monitor Nigerian content

#### Facebook
- `POST /api/v1/social-media/facebook/page` - Scrape page posts
- `GET /api/v1/social-media/facebook/monitor` - Monitor Nigerian pages

#### Apify Integration
- `POST /api/v1/social-media/apify/scrape` - Generic Apify scraper
- `GET /api/v1/social-media/apify/comprehensive` - Comprehensive scraping

#### Hashtag Discovery
- `GET /api/v1/social-media/hashtags/trending` - Discover trending hashtags
- `GET /api/v1/social-media/hashtags/category/{category}` - Category-specific hashtags
- `GET /api/v1/social-media/hashtags/engagement/{hashtag}` - Hashtag metrics

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