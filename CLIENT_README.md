# Social Media Analytics Pipeline - Client Setup Guide

## Overview

This is a comprehensive social media monitoring and analytics platform designed for tracking Nigerian social media conversations with AI-powered analysis.

**Key Features:**
- Multi-platform data collection (Twitter/X, TikTok, Facebook, Google Trends)
- AI-powered sentiment analysis
- Location extraction and geocoding  
- Entity recognition and keyword extraction
- RESTful API for frontend integration
- Real-time analytics and reporting

---

## System Requirements

### Required Software
- **Python 3.10+** (Recommended: 3.13)
- **PostgreSQL 14+** 
- **Redis** (Optional, for caching - improves performance)
- **Git**

### Recommended Specifications
- **RAM:** 4GB minimum, 8GB+ recommended
- **Storage:** 10GB+ free space
- **OS:** Linux, macOS, or Windows (WSL2)

---

## Quick Setup (Automated)

Run the automated setup script:

```bash
./setup.sh
```

This will:
1. Check system requirements
2. Set up PostgreSQL database
3. Install Python dependencies
4. Configure environment variables  
5. Initialize database tables
6. Import sample data (if available)

---

##  Manual Setup

If you prefer manual setup or the automated script fails:

### 1. Database Setup

#### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

#### Create Database

```bash
# Create database and user
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE social_media_pipeline;
CREATE USER sa WITH PASSWORD 'Mercury1_2';
GRANT ALL PRIVILEGES ON DATABASE social_media_pipeline TO sa;
\q
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install SpaCy language model
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required** `.env` variables:
```
bash
# Database
DATABASE_URL=postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline

# API Keys (if using external services)
APIFY_API_TOKEN=your_token_here  # Optional
TWITTER_BEARER_TOKEN=your_token_here  # Optional

# Redis (if installed)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4. Database Initialization

```bash
# Create database tables
python scripts/create_ai_tables.py

# Import sample data (if JSON files exist)
python scripts/import_data.py
```

### 5. Start the Application

```bash
# Start the API server
./start_server.sh

# OR manually:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Verification

### Check Database Connection

```bash
# Test PostgreSQL connection
psql -h localhost -U sa -d social_media_pipeline -c "SELECT version();"
```

### Check API Status

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","environment":"development","version":"0.1.0","database":"PostgreSQL","cache":"Redis"}
```

### Access API Documentation

Open in browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Social Media Data

- `GET /api/v1/social-media/data/scraped` - Get scraped posts
- `GET /api/v1/social-media/data/geo-analysis` - Geographic analysis
- `GET /api/v1/social-media/data/stats` - Overall statistics

### AI Analysis

- `POST /api/v1/ai/sentiment/analyze` - Analyze sentiment
- `POST /api/v1/ai/locations/extract` - Extract locations
- `POST /api/v1/ai/analysis/comprehensive` - Complete analysis

### Data Collection

- `POST /api/v1/social-media/apify/scrape` - Scrape via Apify
- `GET /api/v1/social-media/google-trends/trending` - Google Trends
- `POST /api/v1/social-media/tiktok/hashtag` - TikTok hashtag search

**Complete API documentation:** See `/docs` endpoint or `API_ENDPOINTS.md`

---

## Data Import

### Import Tweet Data from JSON

If you have JSON data files in the `data/` directory:

```bash
python scripts/import_data.py
```

This will:
- Read all JSON files from `data/` directory
- Parse tweet/post data
- Import to PostgreSQL  
- Skip duplicates automatically

### Run AI Processing

After importing data, run AI analysis:

```bash
# Process all unprocessed posts
python scripts/setup_intelligence_system.py
```

This performs:
- Sentiment analysis
- Location extraction
- Entity recognition
- Keyword extraction

---

## Configuration

### Database Settings

Edit `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

### API Keys

If using external services, add to `.env`:
```bash
# Apify (for web scraping)
APIFY_API_TOKEN=your_token

# Twitter API
TWITTER_BEARER_TOKEN=your_token

# Hugging Face (for AI models)
HUGGINGFACE_TOKEN=your_token
```

### Redis Cache (Optional)

For improved performance:
```bash
# Install Redis
sudo apt install redis-server  # Ubuntu
brew install redis  # macOS

# Configure in .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Troubleshooting

### Database Connection Errors

**Issue:** `could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection settings in .env
psql -h localhost -U sa -d social_media_pipeline
```

### Import Errors

**Issue:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

**Issue:** Port 8000 already in use

**Solution:**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### SpaCy Model Not Found

**Issue:** `Can't find model 'en_core_web_sm'`

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

---

## Maintenance

### Database Backup

```bash
# Backup
pg_dump -h localhost -U sa social_media_pipeline > backup.sql

# Restore
psql -h localhost -U sa -d social_media_pipeline < backup.sql
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Clear Cache (if using Redis)

```bash
redis-cli FLUSHALL
```

---

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/
```

---

## Production Deployment

For production deployment:

1. **Update environment:**
   ```bash
   ENVIRONMENT=production
   DEBUG=False
   ```

2. **Use strong security keys:**
   ```bash
   SECRET_KEY=<generate-strong-random-key>
   ```

3. **Configure proper CORS:**
   ```bash
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

4. **Use HTTPS** and proper authentication

5. **Set up monitoring** and logging

6. **Configure database backups**

7. **Use production WSGI server:**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

---

## Support

### Documentation
- **API Docs:** http://localhost:8000/docs
- **API Endpoints:** `API_ENDPOINTS.md`
- **Quick Reference:** `QUICK_REFERENCE.md`

### Logs
- Check application logs in terminal
- PostgreSQL logs: `/var/log/postgresql/`

### Issues
- Check existing scripts in `scripts/` directory
- Review error messages carefully
- Ensure all dependencies are installed

---

## Architecture

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │
│  REST API   │
└──────┬──────┘
       │
       ├──→ PostgreSQL (Data Storage)
       ├──→ Redis (Caching)
       └──→ AI Models (Analysis)
```

### Tech Stack
- **Backend:** Python 3.13, FastAPI
- **Database:** PostgreSQL 14+
- **Cache:** Redis  
- **AI/ML:** spaCy, Transformers, TextBlob
- **Web Scraping:** Apify, Playwright

---

## Next Steps

1. **Verify Setup:** Run `./setup.sh` or follow manual steps
2. **Import Data:** Use `scripts/import_data.py` if you have JSON files
3. **Start Server:** Run `./start_server.sh`
4. **Test API:** Visit http://localhost:8000/docs
5. **Integrate Frontend:** Use API endpoints documented in `/docs`

---

## License

MIT License - See LICENSE file for details

---

**Last Updated:** 2025-11-25  
**Version:** 0.1.0  
**Contact:** [Your Contact Information]
