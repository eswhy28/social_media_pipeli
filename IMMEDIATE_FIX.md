# IMMEDIATE FIX - Database Tables Not Created

## The Problem
Your database exists but has no tables (or partially created tables with index conflicts), causing the error:
```
relation "apify_scraped_data" does not exist
```

## Quick Solution (Choose One)

### Option 1: Reset Database (RECOMMENDED - Clean Slate)
This will delete any existing data and create fresh tables:

```bash
cd /home/aminu/projects/social_media_pipeli
source venv/bin/activate
python scripts/reset_database.py
# Type 'YES' when prompted
```

### Option 2: Force Reset (Non-Interactive)
Same as Option 1 but no confirmation prompt:

```bash
python scripts/force_reset_database.py
```

### Option 3: Try Creating Tables (May fail if conflicts exist)
```bash
python scripts/create_all_tables.py
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

