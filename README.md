
# Social Media AI Pipeline

Enterprise-grade social media analysis platform with advanced AI capabilities for sentiment analysis and location extraction.

## Features

- **Advanced Sentiment Analysis**: RoBERTa model with 98%+ accuracy
- **Location Extraction**: BERT NER + spaCy for geographical entity recognition
- **Comprehensive Text Analysis**: Keywords, entities, and content insights
- **Database Storage**: SQLAlchemy models for analysis results
- **RESTful API**: FastAPI with automatic documentation
- **Authentication**: JWT-based security system
- **Docker Support**: Containerized deployment ready

## AI Models

- **Sentiment**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **NER**: `dbmdz/bert-large-cased-finetuned-conll03-english`
- **spaCy**: `en_core_web_sm` for additional entity recognition

## Social Media Platform Support

### Current
- **Twitter/X**: Native API integration with tweepy

### Phase 1 - Newly Added
- **TikTok**: Content fetching via TikTok-Api
- **Facebook/Instagram**: Content scraping with facebook-scraper
- **Google Trends**: Trend analysis with pytrends (no API key required)
- **Web Scraping**: Apify platform integration for advanced scraping

### Phase 2 - Data Source Integration (✅ Implemented)
All new services are fully integrated with Nigerian content focus:
- **Google Trends Service**: Real-time trending searches, interest over time, regional analysis for Nigeria
- **TikTok Service**: Nigerian hashtag monitoring, video metrics, engagement analytics
- **Facebook Service**: Nigerian pages monitoring, post scraping, engagement collection
- **Apify Service**: Multi-platform scraping with actor-based architecture

## 🚀 Quick Start for Frontend Developers

### One-Command Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd social_media_pipeli

# Run the complete setup script
python setup_complete.py
```

This script will automatically:
- Install all dependencies
- Download AI models
- Create database and generate sample data
- Start the API server
- Open API documentation in your browser

### Manual Setup

#### 1. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Download AI models and data
python scripts/setup_models.py
```

#### 2. Environment Setup
Create a `.env` file in the project root:
```env
# Core Settings
HUGGINGFACE_TOKEN=your_token_here
DATABASE_URL=sqlite:///./data/social_media.db
SECRET_KEY=your_secret_key_here

# Social Media API Keys (Optional - Phase 1)
APIFY_API_TOKEN=your_apify_token
TIKTOK_API_KEY=your_tiktok_key
TIKTOK_API_SECRET=your_tiktok_secret
TIKTOK_ACCESS_TOKEN=your_tiktok_token
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
```

See `.env.example` for a complete list of configuration options.

#### 3. Initialize Database & Generate Sample Data
```bash
# Initialize database
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

# Generate sample data for testing
python generate_1000_tweets.py
```

#### 4. Start the Application
```bash
python run.py
```

The API will be available at:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📖 API Endpoints

### AI Analysis Endpoints
- `POST /api/v1/ai/analyze/sentiment` - Sentiment analysis
- `POST /api/v1/ai/analyze/locations` - Location extraction
- `POST /api/v1/ai/analyze/comprehensive` - Complete text analysis
- `GET /api/v1/ai/models/info` - Model information and status

### Data Endpoints
- `GET /api/v1/data/posts` - Get social media posts
- `POST /api/v1/data/posts` - Create new post
- `GET /api/v1/data/analytics` - Get analytics data

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

## 🔧 Frontend Integration Examples

### JavaScript/TypeScript
```javascript
// Analyze text sentiment
const analyzeText = async (text) => {
  const response = await fetch('http://localhost:8000/api/v1/ai/analyze/comprehensive', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text })
  });
  return await response.json();
};

// Get social media posts
const getPosts = async () => {
  const response = await fetch('http://localhost:8000/api/v1/data/posts');
  return await response.json();
};
```

### Phase 2 - Using New Data Sources

```python
# Google Trends - Get trending searches in Nigeria
from app.services import get_google_trends_service

trends_service = get_google_trends_service()
trending = await trends_service.get_trending_searches(region="NG")
print(f"Top trending: {trending[0]['term']}")

# Get interest over time for keywords
interest = await trends_service.get_interest_over_time(
    keywords=["naira", "fuel price", "election"],
    timeframe="today 3-m",
    geo="NG"
)

# TikTok - Monitor Nigerian hashtags
from app.services import get_tiktok_service

tiktok_service = get_tiktok_service()
videos = await tiktok_service.search_hashtag("nigeria", count=30)
print(f"Found {len(videos)} videos")

# Monitor multiple Nigerian hashtags
monitoring = await tiktok_service.monitor_nigerian_content(
    max_videos_per_hashtag=20
)

# Facebook - Scrape Nigerian pages
from app.services import get_facebook_service

fb_service = get_facebook_service()
posts = await fb_service.scrape_page_posts("legit.ng", pages=2)

# Monitor multiple Nigerian pages
monitoring = await fb_service.monitor_nigerian_pages(pages_per_source=2)

# Apify - Advanced scraping
from app.services import get_apify_service

apify_service = get_apify_service()

# Scrape Instagram profile
data = await apify_service.scrape_instagram_profile(
    username="lagosnigeria",
    results_limit=50
)

# Comprehensive multi-platform scraping
results = await apify_service.scrape_nigerian_social_media(
    platforms=["instagram", "tiktok", "facebook"],
    items_per_platform=50
)
```

### Python
```python
import requests

# Analyze sentiment
response = requests.post(
    'http://localhost:8000/api/v1/ai/analyze/sentiment',
    json={'text': 'I love this product!'}
)
result = response.json()
```

### cURL
```bash
# Test comprehensive analysis
curl -X POST "http://localhost:8000/api/v1/ai/analyze/comprehensive" \
     -H "Content-Type: application/json" \
     -d '{"text": "Amazing product! Works great in New York and Los Angeles."}'
```

## 🛠️ Development Scripts

- `python scripts/setup_models.py` - Download and verify AI models
- `python generate_1000_tweets.py` - Generate 1000 sample tweets for testing
- `python test_all_endpoints.py` - Test all API endpoints
- `python verify.sh` - Verify installation and setup

## 📊 Sample API Response

```json
{
  "success": true,
  "data": {
    "text": "I love this product! Works great in New York.",
    "sentiment": {
      "label": "positive",
      "score": 0.89,
      "confidence": 0.92,
      "model": "roberta"
    },
    "locations": [
      {
        "text": "New York",
        "label": "GPE",
        "confidence": 0.98,
        "source": "huggingface"
      }
    ],
    "keywords": ["product", "great"],
    "entities": [...],
    "analysis_timestamp": "2024-10-25T23:00:00Z"
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Models not loading**: Run `python scripts/setup_models.py`
2. **Database errors**: Delete `social_media.db` and run setup again
3. **Port conflicts**: Change port in `run.py` or use `python run.py --port 8001`
4. **Missing dependencies**: Run `pip install -r requirements.txt`

### Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Model Status Check
```bash
curl http://localhost:8000/api/v1/ai/models/info
# Should show loaded models and their status
```

## 🌐 Deployment

### Vercel (Recommended for Production)

Deploy to Vercel for serverless, scalable API with public access:

#### Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/social_media_pipeli)

#### Manual Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Configure Environment Variables** in Vercel Dashboard:
   - `ENVIRONMENT=production`
   - `SECRET_KEY=your-secret-key`
   - `HUGGINGFACE_TOKEN=hf_your_token`
   - `DATABASE_URL=sqlite+aiosqlite:///./data/social_media.db`

**Features:**
- ✅ Publicly accessible APIs
- ✅ Auto-scaling serverless functions
- ✅ CORS enabled for all origins
- ✅ Automatic HTTPS
- ✅ Free tier available
- ✅ Continuous deployment from GitHub

**📖 Full Guide**: See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

**API URL**: `https://your-project.vercel.app`

### Local Docker
```bash
docker build -t social-media-ai .
docker run -p 8000:8000 social-media-ai
```

### Hugging Face Spaces
- Ready for deployment with `Dockerfile` and `app.py`
- Optimized for AI model inference
- Alternative to Vercel deployment

## 📝 Environment Variables

```env
# Required
HUGGINGFACE_TOKEN=hf_your_token_here
SECRET_KEY=your-secret-key-here

# Optional
DATABASE_URL=sqlite:///./data/social_media.db
API_V1_STR=/api/v1
PROJECT_NAME=Social Media AI Pipeline
ENVIRONMENT=development

# Phase 1 - Social Media APIs (Optional)
APIFY_API_TOKEN=your_apify_token
TIKTOK_API_KEY=your_tiktok_key
TIKTOK_API_SECRET=your_tiktok_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

## 🔑 Getting API Keys

### Required for Core Functionality
- **HuggingFace**: Free account at https://huggingface.co/settings/tokens

### Optional - Phase 1 Social Media Platforms
- **Apify**: Sign up at https://console.apify.com/account/integrations (Free tier: 5 actors, $5 free credit)
- **TikTok**: Apply at https://developers.tiktok.com/ (requires business verification)
- **Facebook/Instagram**: Create app at https://developers.facebook.com/ (Free tier available)
- **Google Trends**: No API key required - uses pytrends library

## 🤝 Support

- Check `/docs` for interactive API documentation
- Run health checks at `/health`
- View model status at `/api/v1/ai/models/info`
- Generate fresh test data with `python generate_1000_tweets.py`