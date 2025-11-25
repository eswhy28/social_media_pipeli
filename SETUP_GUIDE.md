# Enhanced Setup Script - Documentation

## Overview

The `setup.sh` script has been enhanced to provide a **complete, automated setup** for the Social Media Analytics Pipeline with PostgreSQL, including automatic data migration and AI processing.

---

## What the Script Does

### 11-Step Automated Setup Process

#### **Steps 1-7: Environment Setup** (Same as before)
1. ✅ Check Python version (3.10+)
2. ✅ Check PostgreSQL installation
3. ✅ Create Python virtual environment
4. ✅ Install Python dependencies
5. ✅ Install SpaCy language model
6. ✅ Configure environment variables (.env)
7. ✅ Create PostgreSQL database and user

#### **Step 8: Database Tables** ✅
- Creates all required tables in PostgreSQL
- Runs `scripts/create_ai_tables.py`
- Creates tables for:
  - Social media posts (`apify_scraped_data`)
  - AI sentiment analysis
  - Location extractions
  - Entity extractions
  - Keyword extractions
  - Processing status tracking

#### **Step 9: JSON Data Migration** ✅ **NEW**
- Automatically finds JSON files in `/data` directory
- Imports all JSON data to PostgreSQL database
- Uses `scripts/import_data.py`
- Handles duplicates automatically
- Shows progress and import statistics

#### **Step 10: AI Processing** ✅ **NEW**
- Automatically runs AI analysis on imported data
- Processes all posts with:
  - **Sentiment Analysis** (positive/negative/neutral)
  - **Location Extraction** (with geocoding)
  - **Entity Recognition** (people, places, organizations)
  - **Keyword Extraction** (important terms)
- Saves all results to PostgreSQL
- Uses `scripts/setup_intelligence_system.py`

#### **Step 11: Verification** ✅ **NEW**
- Verifies database contains imported data
- Checks AI processing completion
- Shows record counts:
  - Total posts imported
  - Total sentiment analyses
- Confirms setup is ready for use

---

## Usage

### Basic Usage (Recommended)
```bash
./setup.sh
```

The script will:
1. Set up the environment automatically
2. Create PostgreSQL database
3. Import JSON data automatically
4. Run AI processing automatically
5. Verify everything is working

### What You'll See

```
╔════════════════════════════════════════════════════════════╗
║   Social Media Analytics Pipeline - Setup Script          ║
╚════════════════════════════════════════════════════════════╝

[1/11] Checking Python version...
✓ Python 3.13.0

[2/11] Checking PostgreSQL...
✓ PostgreSQL 14.5 installed

[3/11] Setting up Python virtual environment...
✓ Virtual environment already exists

[4/11] Installing Python dependencies...
✓ Dependencies installed

[5/11] Installing SpaCy language model...
✓ SpaCy model installed

[6/11] Configuring environment...
✓ .env already exists

[7/11] Setting up database...
✓ Database 'social_media_pipeline' already exists
Testing database connection...
✓ Database connection successful

[8/11] Initializing database tables...
✓ Database tables created

[9/11] Importing JSON data to PostgreSQL...
Found 11 JSON file(s) in data directory
Importing data to PostgreSQL database...

Processing file: dataset_tweet-scraper_2025-11-21_21-51-32-246.json
  Tweets in file: 10
  Inserted: 10, Skipped (duplicates): 0

... (processing continues for all files)

✓ Data imported successfully

[10/11] Running AI analysis on imported data...
This may take a few minutes depending on data size...

═══ AI Processing Started ═══

Processing sentiment analysis...
✓ Processed 106 posts

Processing location extraction...
✓ Extracted 45 locations

... (AI processing continues)

✓ AI processing completed successfully

[11/11] Verifying setup...
✓ Database contains 106 records
✓ AI analysis complete: 106 sentiment records

╔════════════════════════════════════════════════════════════╗
║                  Setup Complete!                            ║
╚════════════════════════════════════════════════════════════╝

✓ Python Environment: venv
✓ Database: PostgreSQL (social_media_pipeline)
✓ Dependencies: Installed
✓ Tables: Created
✓ Data: 106 records imported
✓ AI Analysis: 106 records processed

Next Steps:

  1. Activate virtual environment:
     source venv/bin/activate

  2. Start the API server:
     ./start_server.sh

  3. Access API documentation:
     http://localhost:8000/docs

  4. Test the API:
     curl http://localhost:8000/health

  5. Test data endpoints:
     curl http://localhost:8000/api/v1/social-media/data/scraped?limit=10
     curl http://localhost:8000/api/v1/social-media/data/with-media?limit=10

════════════════════════════════════════════════════════════

Start the API server now? (y/N)
```

---

## Features

### Automatic Data Import ✅
- Scans `/data` directory for JSON files
- Imports all found JSON files automatically
- No manual intervention required
- Handles duplicates intelligently

### Automatic AI Processing ✅
- Runs immediately after data import
- Processes all imported posts
- Saves results to PostgreSQL
- Shows progress for each AI task

### Verification ✅
- Confirms data was imported
- Checks AI processing completed
- Shows actual record counts
- Validates database connectivity

### Intelligent Workflow
- Only runs AI processing if data was imported successfully
- Skips steps gracefully if files are missing
- Provides helpful error messages
- Shows next steps based on what was completed

---

## Requirements

### Before Running

1. **PostgreSQL must be installed and running**
   ```bash
   # Check if PostgreSQL is installed
   psql --version
   
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   ```

2. **JSON data files in `/data` directory** (optional but recommended)
   - Script will import any `*.json` files found
   - Works with Twitter/X data format
   - Supports multiple files

3. **Python 3.10+**
   ```bash
   python3 --version
   ```

---

## What Gets Created

### Database Objects
- **Database:** `social_media_pipeline`
- **User:** `sa` (password: `Mercury1_2`)
- **Tables:** 15+ tables including:
  - `apify_scraped_data` - Social media posts
  - `apify_sentiment_analysis` - Sentiment results
  - `apify_location_extractions` - Location data
  - `apify_entity_extractions` - Named entities
  - `apify_keyword_extractions` - Keywords
  - `apify_data_processing_status` - Processing tracking

### Data
- All JSON files from `/data` imported
- AI analysis for all posts:
  - Sentiment scores
  - Extracted locations with coordinates
  - Identified entities (people, places, orgs)
  - Extracted keywords

### Environment
- Python virtual environment (`venv/`)
- Configured `.env` file
- Installed dependencies
- SpaCy language model

---

## Troubleshooting

### PostgreSQL Not Found
**Error:** `PostgreSQL not found`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@14

# Then start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql@14  # macOS
```

### Database Connection Failed
**Error:** `Cannot connect to database`

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Try manual connection
psql -h localhost -U sa -d social_media_pipeline
```

### No JSON Files Found
**Warning:** `No JSON files found in data directory`

**Solution:**
- Place your JSON data files in `/data` directory
- Ensure files have `.json` extension
- Re-run setup script

### AI Processing Script Not Found
**Warning:** `AI processing script not found`

**Solution:**
```bash
# Verify script exists
ls -lah scripts/setup_intelligence_system.py

# If missing, you can run AI processing manually later
python scripts/setup_intelligence_system.py
```

---

## Manual Steps (If Needed)

If you prefer to run steps manually:

```bash
# 1. Create database
sudo -u postgres psql
CREATE DATABASE social_media_pipeline;
CREATE USER sa WITH PASSWORD 'Mercury1_2';
GRANT ALL PRIVILEGES ON DATABASE social_media_pipeline TO sa;

# 2. Create tables
python scripts/create_ai_tables.py

# 3. Import data
python scripts/import_data.py

# 4. Run AI processing
python scripts/setup_intelligence_system.py

# 5. Start server
./start_server.sh
```

---

## Verification Commands

After setup completes, verify everything:

```bash
# 1. Check database has data
# Login to PostgreSQL
PGPASSWORD=Mercury1_2 psql -h localhost -U sa -d social_media_pipeline

# Run these SQL queries:
SELECT COUNT(*) FROM apify_scraped_data;
SELECT COUNT(*) FROM apify_sentiment_analysis;
SELECT COUNT(*) FROM apify_location_extractions;

# 2. Check API health
curl http://localhost:8000/health

# 3. Get some data
curl http://localhost:8000/api/v1/social-media/data/scraped?limit=5

# 4. Get posts with media
curl http://localhost:8000/api/v1/social-media/data/with-media?limit=5
```

---

## Summary of Changes

### Before (Old Setup)
- 8 steps total
- Manual data import (prompted user)
- No automatic AI processing
- No verification step

### After (New Setup)
- 11 steps total
- **Automatic data import** ✅
- **Automatic AI processing** ✅
- **Verification with record counts** ✅
- **Smarter error handling** ✅
- **Better progress reporting** ✅

---

## Next Steps After Setup

1. **Start the server:**
   ```bash
   source venv/bin/activate
   ./start_server.sh
   ```

2. **Access API docs:**
   - Swagger: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Test endpoints:**
   - See `API_UPDATES.md` for new media endpoint
   - See `CLIENT_README.md` for complete guides

---

**Setup Script Version:** 2.0  
**Last Updated:** 2025-11-25  
**Database:** PostgreSQL  
**Features:** Automatic data import + AI processing
