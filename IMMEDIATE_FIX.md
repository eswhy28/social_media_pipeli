# IMMEDIATE FIX - Database Tables Not Created

## The Problem
Your database exists but has stubborn indexes from partial table creation, causing the error:
```
relation "apify_scraped_data" does not exist
relation "idx_posted_at" already exists
```

## Quick Solution (RECOMMENDED)

### Option 1: Manual SQL Reset (Most Reliable)
Run this command directly on your cloud server:

```bash
docker exec postgres psql -U sa -d social_media_pipeline -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO sa; GRANT ALL ON SCHEMA public TO public;"
```

Then create the tables:
```bash
cd /home/aminu/projects/social_media_pipeli
source venv/bin/activate
python scripts/create_all_tables.py
```

### Option 2: Force Reset Script  
```bash
cd /home/aminu/projects/social_media_pipeli
source venv/bin/activate
python scripts/force_reset_database.py
```

###Option 3: Interactive Reset
```bash
python scripts/reset_database.py
# Type 'YES' when prompted
```

## After Creating Tables

Once tables are created successfully, you can:

### Start the API server:
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Or continue with setup.sh:
```bash
./setup.sh
# It should now detect the tables and continue
```

## Verify Everything Works

```bash
# Check tables exist
docker exec postgres psql -U sa -d social_media_pipeline -c '\dt'

# Should see 12 tables:
# - apify_ai_batch_jobs
# - apify_data_processing_status
# - apify_entity_extractions
# - apify_keyword_extractions
# - apify_location_extractions
# - apify_scraped_data          <-- This is the one causing the error
# - apify_sentiment_analysis
# - data_source_monitoring
# - facebook_content
# - google_trends_data
# - social_media_aggregation
# - tiktok_content
```

## What Changed

### Fixed Scripts:
1. **setup.sh** - Now detects your Docker container ('postgres') and superuser ('sa')
2. **create_all_tables.py** - Creates tables one by one to avoid transaction rollback on duplicate errors
3. **reset_database.py** - Interactive reset with confirmation
4. **force_reset_database.py** - Non-interactive reset for automation

### Root Cause:
The original setup tried to create all tables in one transaction. When it encountered a duplicate index (probably from a previous partial setup), the entire transaction failed, leaving you with 0 tables.

The new version creates tables individually, so if one fails, others still get created.

## Need Help?

Check the main documentation:
- `DATABASE_SETUP_FIX.md` - Complete setup guide
- `README.md` - Project overview

Run diagnostics:
```bash
./verify_database.sh
```

