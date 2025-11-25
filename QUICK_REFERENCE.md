# POC Quick Reference Card

## 🚀 One-Command Setup

```bash
./setup_poc.sh
```

This runs everything you need: migration + AI processing (optional)

---

## 📋 Manual Commands

### Setup & Migration
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run migration (JSON → SQLite)
./scripts/migrate_to_sqlite.sh

# 3. Run AI processing
python scripts/run_ai_processing.py

# 4. Verify setup
python scripts/verify_poc_setup.py
```

### Running the Server
```bash
# Option 1: Using the start script
./start_server.sh

# Option 2: Directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Commands
```bash
# Check database records
sqlite3 social_media.db "SELECT COUNT(*) FROM apify_scraped_data;"

# Check AI analysis
sqlite3 social_media.db "SELECT COUNT(*) FROM apify_sentiment_analysis;"

# Reset database
rm social_media.db && ./scripts/migrate_to_sqlite.sh
```

---

## 🔗 Important URLs

| Resource | URL |
|----------|-----|
| API Base | http://localhost:8000/api/v1 |
| Health Check | http://localhost:8000/health |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 🎯 Key API Endpoints

### Analytics
```bash
# Overall statistics
curl http://localhost:8000/api/v1/social-media/analytics/stats

# Aggregated analytics (last 7 days)
curl http://localhost:8000/api/v1/social-media/analytics/aggregated?days=7
```

### AI Analysis
```bash
# Analyze sentiment
curl -X POST http://localhost:8000/api/v1/ai/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Nigeria is amazing!"}'

# Extract locations
curl -X POST http://localhost:8000/api/v1/ai/locations/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Lagos and Abuja are great cities"}'

# Comprehensive analysis
curl -X POST http://localhost:8000/api/v1/ai/analysis/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"text": "President visited Lagos today"}'
```

### Data Retrieval
```bash
# Get scraped posts
curl http://localhost:8000/api/v1/social-media/data/scraped?limit=10

# Get posts with media
curl "http://localhost:8000/api/v1/social-media/data/scraped?has_media=true&limit=20"

# Geographic analysis
curl "http://localhost:8000/api/v1/social-media/data/geo-analysis?hours_back=24"
```

### Social Media Scraping
```bash
# Scrape Twitter with Apify
curl -X POST http://localhost:8000/api/v1/social-media/apify/scrape \
  -H "Content-Type: application/json" \
  -d '{"platform": "twitter", "target": "#Nigeria", "limit": 50}'

# Get Google Trends
curl "http://localhost:8000/api/v1/social-media/google-trends/trending?region=NG"
```

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| **POC_SETUP.md** | Complete setup guide with troubleshooting |
| **API_ENDPOINTS.md** | Full API documentation with examples |
| **MIGRATION_SUMMARY.md** | What changed for POC deployment |
| **README.md** | Main project documentation |

### Quick Access
```bash
# View POC setup guide
cat POC_SETUP.md

# View API documentation
cat API_ENDPOINTS.md

# View migration summary
cat MIGRATION_SUMMARY.md
```

---

## 🛠️ Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Database issues
```bash
# Remove and recreate
rm social_media.db
./scripts/migrate_to_sqlite.sh
python scripts/run_ai_processing.py
```

### AI processing fails
```bash
# Check SpaCy model
python -m spacy validate

# Reinstall if needed
python -m spacy download en_core_web_sm
```

### No data in database
```bash
# Run migration
./scripts/migrate_to_sqlite.sh

# Verify
sqlite3 social_media.db "SELECT COUNT(*) FROM apify_scraped_data;"
```

---

## 🔍 Verification Commands

```bash
# Verify complete setup
python scripts/verify_poc_setup.py

# Check API health
curl http://localhost:8000/health

# Test database connection
sqlite3 social_media.db ".tables"

# Check logs
tail -f logs/app.log  # if logging to file
```

---

## 📊 Database Schema Quick Reference

### Main Tables
- `apify_scraped_data` - Social media posts (Twitter, etc.)
- `apify_sentiment_analysis` - AI sentiment results
- `apify_location_extractions` - Extracted locations
- `apify_entity_extractions` - Named entities
- `apify_keyword_extractions` - Keywords
- `apify_data_processing_status` - Processing tracking

### Check Table Contents
```bash
# List all tables
sqlite3 social_media.db ".tables"

# Count records in each table
sqlite3 social_media.db "
  SELECT 'apify_scraped_data' as table_name, COUNT(*) as count FROM apify_scraped_data
  UNION ALL
  SELECT 'apify_sentiment_analysis', COUNT(*) FROM apify_sentiment_analysis
  UNION ALL
  SELECT 'apify_location_extractions', COUNT(*) FROM apify_location_extractions;
"
```

---

## 🎨 Frontend Integration Example

```javascript
// Base API URL
const API_BASE = 'http://localhost:8000/api/v1';

// Fetch posts with filters
async function getPosts() {
  const response = await fetch(
    `${API_BASE}/social-media/data/scraped?has_media=true&limit=20`
  );
  const data = await response.json();
  return data.data.posts;
}

// Analyze sentiment
async function analyzeSentiment(text) {
  const response = await fetch(
    `${API_BASE}/ai/sentiment/analyze`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    }
  );
  return await response.json();
}

// Get statistics
async function getStats() {
  const response = await fetch(
    `${API_BASE}/social-media/analytics/stats`
  );
  return await response.json();
}
```

---

## 📦 Package Management

```bash
# Install all dependencies
pip install -r requirements.txt

# Install SpaCy model
python -m spacy download en_core_web_sm

# Update requirements (if adding packages)
pip freeze > requirements.txt
```

---

## 🔄 Workflow Summary

```
1. Setup
   └── ./setup_poc.sh

2. Development
   ├── Start server: ./start_server.sh
   ├── Test APIs: http://localhost:8000/docs
   └── Check logs in terminal

3. Testing
   ├── Verify: python scripts/verify_poc_setup.py
   ├── Test endpoints: See API_ENDPOINTS.md
   └── Check database: sqlite3 social_media.db

4. Frontend Integration
   ├── Use APIs from API_ENDPOINTS.md
   ├── No authentication needed (POC)
   └── All data is pre-analyzed
```

---

## ⚡ Performance Tips

- Use `limit` parameter to control response size
- Filter by `hours_back` for recent data
- Use `has_media=true` to get only posts with images
- Enable caching for repeated queries (Redis optional)

---

## 📞 Support

- Check **POC_SETUP.md** for detailed troubleshooting
- Use **API_ENDPOINTS.md** for endpoint documentation
- Interactive docs at http://localhost:8000/docs

---

**POC Version:** 0.1.0  
**Database:** SQLite  
**Last Updated:** 2025-11-25

---

**Quick Links:**
- [POC Setup Guide](POC_SETUP.md)
- [API Documentation](API_ENDPOINTS.md)
- [Migration Summary](MIGRATION_SUMMARY.md)
- [Main README](README.md)
