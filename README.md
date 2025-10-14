# Social Media Monitoring API - Backend MVP

A comprehensive backend API for social media monitoring, sentiment analysis, and reporting capabilities.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **Social Media Data Ingestion**: Real-time data collection from X (Twitter) and other platforms
- **Sentiment Analysis**: AI-powered sentiment analysis and trend detection
- **Anomaly Detection**: Automated alert system for unusual patterns
- **Geographic Analysis**: Location-based insights and visualizations
- **Influencer Tracking**: Monitor and analyze influential accounts
- **Report Generation**: Automated PDF/Excel report generation
- **Rate Limiting**: Configurable rate limits per user and endpoint
- **Caching**: Redis-based caching for optimal performance
- **Background Tasks**: Celery-based task queue for heavy operations

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Task Queue**: Celery
- **AI/ML**: OpenAI GPT-4, Transformers, NLTK
- **Authentication**: JWT (python-jose)
- **Social Media APIs**: Tweepy (Twitter/X)

## Project Structure

```
social_media_pipeline/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── api/                    # API routes
│   │   ├── auth.py
│   │   ├── data.py
│   │   ├── reports.py
│   │   └── webhooks.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── sentiment_service.py
│   │   ├── social_media_service.py
│   │   └── ai_service.py
│   ├── tasks/                  # Celery tasks
│   ├── utils/                  # Utilities
│   └── middleware/             # Custom middleware
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── logs/                       # Application logs
├── reports/                    # Generated reports
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd social_media_pipeline
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your credentials

4. Start services with Docker Compose:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

6. Access the API:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development (Without Docker)

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start PostgreSQL and Redis locally

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the API server:
```bash
uvicorn app.main:app --reload
```

6. Start Celery worker (in another terminal):
```bash
celery -A app.celery_app worker --loglevel=info
```

7. Start Celery beat (in another terminal):
```bash
celery -A app.celery_app beat --loglevel=info
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints Overview

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

### Data
- `GET /api/v1/data/overview` - Dashboard overview
- `GET /api/v1/data/sentiment/live` - Live sentiment gauge
- `GET /api/v1/data/sentiment/series` - Sentiment time series
- `GET /api/v1/data/hashtags/trending` - Trending hashtags
- `GET /api/v1/data/influencers` - Influential accounts
- `GET /api/v1/data/geographic/states` - Geographic analysis

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/{id}/status` - Check report status
- `GET /api/v1/reports/{id}/download` - Download report

### AI
- `POST /api/v1/ai/generate/summary` - Generate AI summary
- `POST /api/v1/ai/generate/insights` - Generate insights

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Deployment

### Production Checklist

1. Update `.env` with production values
2. Set `DEBUG=False`
3. Use strong `SECRET_KEY`
4. Configure proper CORS origins
5. Set up SSL/TLS certificates
6. Configure proper logging
7. Set up monitoring (Prometheus, Grafana)
8. Configure backup strategy
9. Set up CI/CD pipeline

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

- Health check endpoint: `GET /health`
- Metrics endpoint: `GET /metrics` (Prometheus format)

## Security

- JWT-based authentication
- Rate limiting per user/endpoint
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Password hashing with bcrypt

## Rate Limits

- Standard endpoints: 1000 req/hour
- AI generation: 100 req/hour
- Report generation: 10 req/hour
- Data export: 50 req/hour

## Data Retention

- Raw data: 90 days
- Aggregated data: 2 years
- User data: Until account deletion

## Support

For issues and questions, please open an issue on GitHub.

## License

MIT License
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
bcrypt==4.1.1

# Redis Cache
redis==5.0.1
hiredis==2.2.3

# Background Tasks
celery==5.3.4
kombu==5.3.4

# Data Processing
pandas==2.1.3
numpy==1.26.2

# AI & NLP
openai==1.3.7
transformers==4.35.2
torch==2.1.1
nltk==3.8.1
textblob==0.17.1

# Social Media APIs
tweepy==4.14.0
requests==2.31.0

# HTTP Client
httpx==0.25.2
aiohttp==3.9.1

# Monitoring & Logging
prometheus-client==0.19.0
python-json-logger==2.0.7

# Utilities
python-dotenv==1.0.0
pytz==2023.3
python-dateutil==2.8.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
faker==20.1.0

# Email
python-smtp==1.0.0
aiosmtplib==3.0.1

# Export
reportlab==4.0.7
openpyxl==3.1.2

# Validation
email-validator==2.1.0

