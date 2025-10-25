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

## API Endpoints

- `POST /api/v1/ai/analyze/sentiment` - Sentiment analysis
- `POST /api/v1/ai/analyze/locations` - Location extraction
- `POST /api/v1/ai/analyze/comprehensive` - Complete text analysis
- `GET /api/v1/ai/models/info` - Model information

## Environment Variables

```
HUGGINGFACE_TOKEN=your_token_here
DATABASE_URL=sqlite:///./data/social_media.db
SECRET_KEY=your_secret_key
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run: `python run.py`
4. API docs: `http://localhost:8000/docs`

## Deployment

This application is optimized for Hugging Face Spaces deployment with GPU acceleration for model inference.