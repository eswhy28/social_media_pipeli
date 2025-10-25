
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
HUGGINGFACE_TOKEN=your_token_here
DATABASE_URL=sqlite:///./data/social_media.db
SECRET_KEY=your_secret_key_here
```

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

### Local Docker
```bash
docker build -t social-media-ai .
docker run -p 8000:8000 social-media-ai
```

### Hugging Face Spaces
- Ready for deployment with `Dockerfile` and `app.py`
- Optimized for AI model inference
- Public API endpoint for frontend consumption

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
```

## 🤝 Support

- Check `/docs` for interactive API documentation
- Run health checks at `/health`
- View model status at `/api/v1/ai/models/info`
- Generate fresh test data with `python generate_1000_tweets.py`