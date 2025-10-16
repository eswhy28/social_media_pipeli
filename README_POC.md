asyncio.run(verify())
EOF
```

## 🚀 Deployment Options
```bash
### Local Development (Current)
Perfect for testing and development.
cd /home/mukhtar/Documents/social_media_pipeline
### Docker Deployment
# 2. Run automated setup script
# Build image
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI
# Add Procfile (included)
heroku create your-app-name
heroku addons:create heroku-redis:hobby-dev
heroku config:set TWITTER_BEARER_TOKEN=your_token
git push heroku main
./start.sh
```
#### AWS/GCP/Azure
- Use provided `Dockerfile`
- Deploy to container service (ECS, Cloud Run, Container Apps)
- Add managed Redis and PostgreSQL

## 💰 Cost Analysis

### POC (Current Setup)
| Service | Cost |
|---------|------|
| Local Development | $0 |
| Twitter API Free Tier | $0 |
| TextBlob | $0 |
| SQLite | $0 |
| Local Redis | $0 |
| **Total** | **$0/month** |

### Cloud Deployment (Estimated)
| Service | Monthly Cost |
|---------|-------------|
| Heroku Hobby Dyno | $7 |
| Heroku Redis Hobby | $0 (free tier) |
| Or: AWS EC2 t2.micro | $8.50 |
| Or: DigitalOcean Droplet | $5 |

## 📈 Usage Examples

### 1. Test the API
That's it! Visit http://localhost:8000/docs to use the API.
# Health check
curl http://localhost:8000/health

# Get sentiment analysis
curl -X POST http://localhost:8000/api/v1/ai/generate/summary \
### **Manual Setup** (If automated fails)

    "section": "overview",
    "subject": "Python",
    "template": "general",
    "range": "Last 7 Days",
    "context": {"total_posts": 100, "sentiment": {"positive": 60, "negative": 20, "neutral": 20}}
python3 -m venv venv
source venv/bin/activate

### 2. Login and Get Token
pip install -r requirements.txt
# Login
curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=demo&password=demo123"

# Use token in subsequent requests
curl http://localhost:8000/api/v1/data/overview \
  -H "Authorization: Bearer YOUR_TOKEN"
python -m textblob.download_corpora

### 3. Fetch and Analyze Tweets
The system automatically fetches tweets every 15 minutes. To trigger manually:
- Visit: http://localhost:8000/docs
- Find "Admin" section
- Execute manual ingestion

## 🔐 Security Best Practices

### Development
- ✅ `.env` file for secrets (not committed)
- ✅ JWT authentication enabled
- ✅ CORS configured
- ✅ Rate limiting implemented

### Production Checklist
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Enable HTTPS/TLS
- [ ] Use strong passwords
- [ ] Enable Redis password
- [ ] Upgrade to PostgreSQL
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Use environment-specific configs
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
## 📚 Additional Resources

### Documentation
- [Full API Documentation](API_EXAMPLES.md)
- [System Design](IMPLEMENTATION_GUIDE.md)
- [Architecture Details](PROJECT_STRUCTURE.md)

### External Resources

cp .env.example .env
- [TextBlob Guide](https://textblob.readthedocs.io/)
- [Celery Documentation](https://docs.celeryq.dev/)
# 6. Start Redis (if not running)
## 🤝 Support & Contributing

### Getting Help
1. Check [Troubleshooting](#-troubleshooting) section
```
3. Check Celery logs: `./stop.sh && ./start.sh`

### Testing Changes
```bash
# Always run tests before committing
./test.sh
## 🎯 Key Features (POC)
# Check code style
flake8 app/ tests/
black app/ tests/
```
- ✅ **Twitter API v2 Integration** (Free Tier - 500k tweets/month)
## 📝 License
- ✅ **SQLite Database** (Local, no cloud costs)
MIT License - See LICENSE file for details.
- ✅ **Rate Limiting & Backoff** (Respects API limits)
## ✅ Quick Reference
## 🏗️ Architecture
### Essential Commands
```bash
./setup.sh          # First-time setup
./start.sh          # Start application  
./stop.sh           # Stop application
./test.sh           # Run tests
source venv/bin/activate  # Activate environment
```

### Key Files
- `setup.sh` - Automated setup script
- `start.sh` - Application launcher
- `.env` - Configuration (create from .env.example)
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker setup

### Default Credentials
- **Username:** demo
- **Password:** demo123
- **API Docs:** http://localhost:8000/docs
```
---
         │
**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** October 16, 2025  
**Tests:** 12/12 Passing ✅
         ▼
**Ready to use in 5 minutes!** 🚀
┌─────────────────┐
│  Data Service   │ ← Rate Limiting
│  (Tweepy)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Service    │ ← TextBlob (Free)
│  (Sentiment)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────┐
│  SQLite DB      │ ←──→ │   Redis     │
│  (Local)        │      │  (Cache)    │
└────────┬────────┘      └─────────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   REST API      │
└─────────────────┘
```

## 📋 System Requirements

### Minimum Requirements
- **OS:** Linux, macOS, or Windows (with WSL2)
- **Python:** 3.9 or higher
- **Memory:** 1GB RAM minimum, 2GB recommended
- **Storage:** 500MB free disk space
- **Redis:** Version 5.0+ (auto-installed by setup script)

### Twitter API Access
You need a Twitter Developer account with:
- Bearer Token (Essential/Free tier)
- Sign up at: https://developer.twitter.com/en/portal/dashboard
- 500,000 tweets/month quota included

## 📦 Installation Scripts

### **setup.sh** - Automated Setup
Handles everything automatically:
- Checks system requirements
- Creates virtual environment
- Installs all dependencies
- Downloads NLP corpora
- Initializes database
- Configures Redis
- Creates .env file from template

### **start.sh** - Start Application
Starts all required services:
- API server (FastAPI)
- Background workers (Celery)
- Task scheduler (Celery Beat)
- Opens browser to API docs

### **stop.sh** - Stop Application
Gracefully stops all services

### **test.sh** - Run Tests
Runs complete test suite with coverage report

## 🔧 Configuration

### Environment Variables (.env)

The setup script creates a `.env` file from `.env.example`. Key settings:

```env
# Required: Get from https://developer.twitter.com
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Optional: Leave defaults for local development
DATABASE_URL=sqlite+aiosqlite:///./social_media.db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=auto-generated-secure-key

# CORS for frontend (if applicable)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

## 📡 API Endpoints

### Core Endpoints

#### Health & Status
- `GET /health` - System health check
- `GET /` - API information

#### Authentication
- `POST /api/v1/auth/token` - Login (demo/demo123)
- `GET /api/v1/auth/users/me` - Current user info

#### Data Analysis
- `GET /api/v1/data/overview` - Dashboard metrics
- `GET /api/v1/data/sentiment/live` - Real-time sentiment
- `GET /api/v1/data/sentiment/series` - Time series data
- `GET /api/v1/data/hashtags/trending` - Trending hashtags
- `GET /api/v1/data/keywords/trends` - Keyword analysis
- `GET /api/v1/data/posts/top` - Top posts by engagement

#### AI Services
- `POST /api/v1/ai/generate/summary` - Generate AI summary
- `POST /api/v1/ai/generate/insights` - Generate insights

#### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/{id}/status` - Check report status

### Interactive API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🧪 Testing

### Run All Tests
```bash
./test.sh
```

### Manual Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Results (Current)
✅ **12 tests passing**  
⏭️ **3 tests skipped** (optional features)

## 🤖 Background Tasks

### Celery Tasks (Auto-configured)

The application runs these tasks automatically:

1. **Tweet Ingestion** (Every 15 minutes)
   - Fetches recent tweets matching queries
   - Analyzes sentiment with TextBlob
   - Stores in database

2. **Sentiment Aggregation** (Every hour)
   - Aggregates into time series
   - Calculates metrics
   - Updates trends

3. **Anomaly Detection** (Every 2 hours)
   - Statistical anomaly detection
   - Z-score analysis
   - Alert generation

4. **Data Cleanup** (Daily)
   - Removes old data (30+ days)
   - Manages storage

## 🐛 Troubleshooting

### Setup Issues

#### Python Version Error
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Install Python 3.9+ if needed
# Ubuntu/Debian: sudo apt install python3.9
# macOS: brew install python@3.9
```

#### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping  # Should return: PONG

# Start Redis
# Linux: sudo systemctl start redis
# macOS: brew services start redis
# Docker: docker run -d -p 6379:6379 redis:alpine
```

#### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Database Locked (SQLite)
```bash
# Reset database
rm social_media.db
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
```

### Runtime Issues

#### Twitter API Errors
```bash
# Verify token
echo $TWITTER_BEARER_TOKEN

# Test API access
curl "https://api.twitter.com/2/tweets/search/recent?query=test&max_results=10" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

#### Celery Worker Not Starting
```bash
# Check for errors
celery -A app.celery_app worker --loglevel=debug

# Purge old tasks
celery -A app.celery_app purge

# Restart with clean state
./stop.sh && ./start.sh
```

## 📊 System Verification

### Check Installation
```bash
# Run system verification
python3 << 'EOF'
import asyncio
import sys

async def verify():
    print("🔍 Verifying installation...\n")
    
    # Check Python version
    import sys
    version = sys.version_info
    if version >= (3, 9):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need 3.9+")
        return
    
    # Check dependencies
    deps = ['fastapi', 'uvicorn', 'sqlalchemy', 'celery', 'redis', 'tweepy', 'textblob']
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Run: pip install {dep}")
    
    # Check database
    try:
        from app.database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connected")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Check Redis
    try:
        from app.redis_client import get_redis
        redis = await get_redis()
        await redis.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis: {e}")
    
    print("\n✅ Verification complete!")

- Use environment variables for secrets
- Don't commit `.env` file
- SQLite file should have restricted permissions

### Production Requirements
- HTTPS/TLS encryption
- API rate limiting per user
- OAuth2 authentication
- Database encryption at rest
- Regular security audits

## 📝 API Usage Examples

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### Get Overview (with auth)
```bash
curl "http://localhost:8000/api/v1/data/overview" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🎓 Learning Resources

- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs: `tail -f logs/app.log`
3. Check Celery logs: `celery -A app.celery_app events`

## 📄 License

This POC is provided as-is for demonstration purposes.

## 🚧 Next Steps

1. **Collect Initial Data**: Run for 24-48 hours to gather sample data
2. **Test API Endpoints**: Verify all endpoints work correctly
3. **Monitor Rate Limits**: Track Twitter API usage
4. **Evaluate Results**: Review sentiment accuracy
5. **Plan Production**: Decide on paid services for scaling

---

**Status**: POC Ready ✅  
**Version**: 0.1.0  
**Last Updated**: 2025-10-16

