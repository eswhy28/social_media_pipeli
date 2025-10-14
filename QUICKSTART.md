# 🚀 Quick Start Guide

## Option 1: Docker (Recommended for Quick Testing)

### Prerequisites
- Docker and Docker Compose installed

### Steps

1. **Navigate to project directory**
```bash
cd /home/mukhtar/Documents/social_media_pipeline
```

2. **Start all services**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- API server (port 8000)
- Celery worker
- Celery beat scheduler

3. **Check services are running**
```bash
docker-compose ps
```

4. **View logs**
```bash
docker-compose logs -f api
```

5. **Access the API**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

6. **Create your first user**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register?username=admin&email=admin@example.com&password=SecurePass123"
```

7. **Stop services**
```bash
docker-compose down
```

---

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Steps

1. **Run setup script**
```bash
./setup.sh
```

2. **Activate virtual environment**
```bash
source venv/bin/activate
```

3. **Configure environment**
Edit `.env` file with your database credentials and API keys

4. **Create database**
```bash
createdb social_monitor
```

5. **Run migrations**
```bash
alembic upgrade head
```

6. **Start the API (Terminal 1)**
```bash
uvicorn app.main:app --reload
```

7. **Start Celery worker (Terminal 2)**
```bash
celery -A app.celery_app worker --loglevel=info
```

8. **Start Celery beat (Terminal 3)**
```bash
celery -A app.celery_app beat --loglevel=info
```

9. **Access the API**
- http://localhost:8000/docs

---

## Using Makefile Commands

```bash
# Setup environment
make setup

# Install dependencies
make install

# Run migrations
make migrate

# Start API server
make run

# Start Celery worker (in new terminal)
make worker

# Start Celery beat (in new terminal)
make beat

# Run tests
make test

# Start with Docker
make docker-up

# Stop Docker services
make docker-down
```

---

## First API Calls

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register?username=testuser&email=test@example.com&password=TestPass123"
```

### 3. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123"}'
```

Save the token from the response!

### 4. Get Dashboard Data
```bash
curl -X GET "http://localhost:8000/api/v1/data/overview?range=Last%207%20Days" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Testing the API

### Interactive Documentation
Visit http://localhost:8000/docs for Swagger UI where you can:
- See all available endpoints
- Test endpoints directly in the browser
- View request/response schemas
- Authorize with your JWT token

### Programmatic Testing
See `API_EXAMPLES.md` for comprehensive examples in:
- cURL
- Python (requests)
- Python (httpx async)

---

## Next Steps

1. **Configure External APIs** (Optional)
   - Add Twitter/X API credentials to `.env`
   - Add OpenAI API key for AI summaries

2. **Customize**
   - Modify models in `app/models/`
   - Add new endpoints in `app/api/`
   - Customize business logic in `app/services/`

3. **Add Real Data**
   - Implement data ingestion in `app/tasks/data_ingestion.py`
   - Configure social media API connections

4. **Deploy to Production**
   - Use `docker-compose.prod.yml`
   - Set up proper SSL certificates
   - Configure production environment variables
   - Set up monitoring and logging

---

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `psql -l`

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping`
- Check Redis URL in `.env`

### Import Errors
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change PORT in `.env`
- Or kill process: `lsof -ti:8000 | xargs kill -9`

---

## Support & Documentation

- **API Specification**: `BACKEND_API_SPECIFICATION (1).md`
- **API Examples**: `API_EXAMPLES.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Interactive Docs**: http://localhost:8000/docs
# Application Settings
APP_NAME="Social Media Monitoring API"
APP_VERSION="1.0.0"
ENVIRONMENT=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://social_monitor:social_monitor_pass@localhost:5432/social_monitor
DB_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=change-this-to-a-very-secure-random-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_STANDARD=1000
RATE_LIMIT_AI=100
RATE_LIMIT_REPORTS=10
RATE_LIMIT_EXPORT=50

# OpenAI API (Optional - for AI summaries)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo-preview

# Twitter/X API (Optional - for data ingestion)
X_API_KEY=
X_API_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
X_BEARER_TOKEN=

# Email Settings (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@socialmonitor.com

# SMS Gateway (Optional)
SMS_GATEWAY_URL=
SMS_API_KEY=

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Monitoring
ENABLE_METRICS=True
LOG_LEVEL=INFO

# Data Retention
RAW_DATA_RETENTION_DAYS=90
AGGREGATED_DATA_RETENTION_DAYS=730

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080"]

