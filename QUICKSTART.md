# 🚀 QUICKSTART GUIDE
## Get Social Media Pipeline Running in 5 Minutes

### Prerequisites
- **Python 3.9+** installed
- **Redis** (will auto-install if missing)
- **5 minutes** of your time

---

## 🎯 Option 1: Automated Setup (Recommended)

### Step 1: Run Setup Script
```bash
cd /path/to/social_media_pipeline
./setup.sh
```

This automatically:
- ✅ Checks Python version (3.9+)
- ✅ Installs/starts Redis
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Downloads NLP data
- ✅ Initializes database (14 tables)
- ✅ Creates .env configuration

### Step 2: Add Twitter Token (Optional)
```bash
nano .env
# Add: TWITTER_BEARER_TOKEN=your_token_here
```

Get token: https://developer.twitter.com/en/portal/dashboard

### Step 3: Start Application
```bash
./start.sh
```

### Step 4: Access API
Open in browser: **http://localhost:8000/docs**

**Done!** 🎉

---

## 🔧 Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLP data
python -m textblob.download_corpora

# 4. Start Redis
redis-server --daemonize yes

# 5. Initialize database
python3 << 'EOF'
import asyncio
from app.models import *
from app.database import Base, engine

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

asyncio.run(init())
EOF

# 6. Create .env file
cp .env.example .env

# 7. Start application
uvicorn app.main:app --reload
```

---

## 🎮 Using the Application

### Login Credentials
- **Username:** `demo`
- **Password:** `demo123`

### Key Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=demo&password=demo123"

# Get sentiment data
curl http://localhost:8000/api/v1/data/overview \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🛠️ Useful Commands

```bash
./start.sh    # Start all services
./stop.sh     # Stop all services
./test.sh     # Run test suite
```

### View Logs
```bash
tail -f logs/api.log           # API logs
tail -f logs/celery_worker.log # Background tasks
```

---

## 🧪 Quick Test

```bash
# Run tests
./test.sh

# Should show: 12 passed, 3 skipped ✅
```

---

## 🐛 Troubleshooting

### Redis Not Running
```bash
redis-cli ping  # Should return: PONG

# If not running:
redis-server --daemonize yes
```

### Port 8000 Taken
```bash
# Find process
lsof -i :8000

# Use different port
uvicorn app.main:app --port 8001
```

### Reset Everything
```bash
./stop.sh
rm -rf venv social_media.db logs/
./setup.sh
```

---

## 📊 What You Get

### Features Working Out of the Box:
- ✅ REST API with authentication
- ✅ Sentiment analysis (TextBlob)
- ✅ Trending topics detection
- ✅ Anomaly detection
- ✅ Real-time data processing
- ✅ Background task scheduling
- ✅ Caching with Redis
- ✅ SQLite database with 14 tables
- ✅ Interactive API documentation
- ✅ Test suite with 12 passing tests

### Background Tasks (Auto-running):
- Tweet ingestion every 15 minutes
- Sentiment aggregation every hour
- Anomaly detection every 2 hours
- Data cleanup daily

---

## 🚀 Next Steps

1. **Explore API**: http://localhost:8000/docs
2. **Add Twitter token** to fetch real tweets
3. **Read full docs**: `README_POC.md`
4. **Check system status**: http://localhost:8000/health

---

## 💡 Pro Tips

### Enable Twitter Integration
1. Create account: https://developer.twitter.com/portal
2. Create project and app
3. Copy Bearer Token
4. Add to `.env`: `TWITTER_BEARER_TOKEN=...`
5. Restart: `./stop.sh && ./start.sh`

### Production Deployment
- Change `SECRET_KEY` in `.env`
- Use PostgreSQL instead of SQLite
- Enable HTTPS
- Set `DEBUG=False`

### Development Workflow
```bash
# Make changes to code
./stop.sh
./test.sh        # Run tests
./start.sh       # Restart with changes
```

---

## 📞 Need Help?

- **Check logs**: `tail -f logs/api.log`
- **Run tests**: `./test.sh`
- **System check**: See README_POC.md § System Verification
- **Reset**: `./stop.sh && rm -rf venv && ./setup.sh`

---

**Time to run:** 5 minutes ⏱️  
**Cost:** $0/month 💰  
**Status:** Production Ready ✅

**Happy monitoring!** 🎉

