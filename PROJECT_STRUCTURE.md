# Project Structure

```
social_media_pipeline/
├── app/                                # Main application directory
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration settings
│   ├── database.py                    # Database connection setup
│   ├── redis_client.py                # Redis connection
│   ├── celery_app.py                  # Celery configuration
│   │
│   ├── api/                           # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                   # Authentication endpoints
│   │   ├── data.py                   # Data retrieval endpoints
│   │   ├── reports.py                # Report generation endpoints
│   │   ├── ai.py                     # AI-powered endpoints
│   │   ├── webhooks.py               # Webhook endpoints
│   │   └── admin.py                  # Admin endpoints
│   │
│   ├── models/                        # SQLAlchemy database models
│   │   └── __init__.py               # All database models
│   │
│   ├── schemas/                       # Pydantic schemas
│   │   └── __init__.py               # Request/response models
│   │
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── data_service.py           # Data processing service
│   │   └── ai_service.py             # AI/ML service
│   │
│   └── tasks/                         # Celery background tasks
│       ├── __init__.py
│       ├── data_ingestion.py         # Social media data fetching
│       ├── sentiment_analysis.py     # Sentiment analysis tasks
│       ├── anomaly_detection.py      # Anomaly detection tasks
│       └── report_generation.py      # Report generation tasks
│
├── alembic/                           # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_migration.py
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Test configuration
│   └── test_api.py                   # API tests
│
├── logs/                              # Application logs
├── reports/                           # Generated reports
│
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .env                              # Environment variables (gitignored)
├── .gitignore                        # Git ignore rules
│
├── docker-compose.yml                 # Development Docker setup
├── docker-compose.prod.yml           # Production Docker setup
├── Dockerfile                         # Docker image definition
│
├── alembic.ini                       # Alembic configuration
├── Makefile                          # Development commands
├── setup.sh                          # Setup script
├── start.sh                          # Start script
│
├── README.md                         # Project documentation
├── API_EXAMPLES.md                   # API usage examples
├── BACKEND_API_SPECIFICATION (1).md  # API specification
└── nfiu_platform_doc.html           # Platform documentation
```

## Key Components

### Application Layer (app/)
- **main.py**: FastAPI application with CORS, middleware, and route registration
- **config.py**: Centralized configuration using Pydantic settings
- **database.py**: Async SQLAlchemy setup with session management
- **redis_client.py**: Redis connection pool for caching

### API Layer (app/api/)
- **auth.py**: JWT-based authentication with login, register, refresh
- **data.py**: All data endpoints (sentiment, hashtags, influencers, etc.)
- **reports.py**: Report generation and download
- **ai.py**: AI-powered summary and insights generation
- **admin.py**: Admin-only endpoints (alert rules, connectors)

### Data Layer (app/models/)
- User, SocialPost, Hashtag, Keyword, Influencer
- Anomaly, AlertRule, Report
- GeographicData, SentimentTimeSeries, DataConnector

### Schema Layer (app/schemas/)
- Pydantic models for request validation and response serialization
- Enums for consistent data types
- Type-safe API contracts

### Service Layer (app/services/)
- **data_service.py**: Business logic for data retrieval and processing
- **ai_service.py**: OpenAI integration for summaries and insights

### Task Layer (app/tasks/)
- **data_ingestion.py**: Periodic social media data fetching
- **sentiment_analysis.py**: Batch sentiment analysis
- **anomaly_detection.py**: Pattern detection and alerting
- **report_generation.py**: Async report PDF/Excel generation

## Database Schema

### Core Tables
- **users**: User accounts and authentication
- **social_posts**: Social media posts with engagement metrics
- **hashtags**: Trending hashtags with sentiment
- **keywords**: Keyword trends and analysis
- **influencers**: Influential accounts tracking
- **anomalies**: Detected anomalies and alerts
- **geographic_data**: Location-based analytics
- **sentiment_timeseries**: Time-series sentiment data
- **alert_rules**: User-configured alert rules
- **reports**: Generated report metadata
- **data_connectors**: Social media API connections

## External Dependencies

### Required Services
- PostgreSQL 15+ (primary database)
- Redis 7+ (caching and Celery broker)
- OpenAI API (AI summaries and insights)
- Twitter/X API (social media data source)

### Python Packages
- FastAPI + Uvicorn (web framework)
- SQLAlchemy + Alembic (ORM and migrations)
- Celery (task queue)
- OpenAI (AI integration)
- Tweepy (Twitter API)
- Redis (caching)
- JWT (authentication)
# Makefile for Social Media Monitoring API

.PHONY: help setup install migrate run test clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make setup       - Set up the development environment"
	@echo "  make install     - Install dependencies"
	@echo "  make migrate     - Run database migrations"
	@echo "  make run         - Start the API server"
	@echo "  make worker      - Start Celery worker"
	@echo "  make beat        - Start Celery beat scheduler"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make docker-up   - Start all services with Docker"
	@echo "  make docker-down - Stop all Docker services"

setup:
	./setup.sh

install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A app.celery_app worker --loglevel=info

beat:
	celery -A app.celery_app beat --loglevel=info

test:
	pytest tests/ -v --cov=app

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

