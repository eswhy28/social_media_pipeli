# QUICK FIX - Application Won't Start (Duplicate Index Error)

## Problem
Application fails to start with error:
```
relation "idx_timestamp_granularity" already exists
```

## Solution

The application was trying to create tables on startup, but you should use Alembic migrations instead.

### Step 1: Stop the Application
If it's running, press `CTRL+C`

### Step 2: Clean Database and Setup with Alembic

Run the complete setup script:

```bash
cd /home/aminu/projects/social_media_pipeli
source venv/bin/activate
python scripts/complete_setup.py
```

Type `yes` when prompted. This will:
1. Clean the database (remove duplicate indexes)
2. Create tables using Alembic migrations  
3. Import your data (if JSON files exist in `data/` folder)
4. Run AI processing on the data

### Step 3: Start the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## What Was Fixed

- **Disabled** automatic table creation on app startup
- **Application** now expects tables to be created via Alembic migrations
- **No more** duplicate index errors on startup

## Alternative: Just Clean Database

If you just want to fix the duplicate index issue without reimporting data:

```bash
# Option 1: Use the script
python scripts/setup_with_alembic.py

# Option 2: Manual SQL + Alembic
docker exec postgres psql -U sa -d social_media_pipeline -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO sa; GRANT ALL ON SCHEMA public TO public;"
alembic upgrade head
```

## Verify It Works

After starting the app, test:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API docs
# Open browser: http://localhost:8000/docs
```

## Future Database Changes

Always use Alembic for database schema changes:

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head
```

## Summary

✅ **Fixed:** Removed automatic table creation from app startup  
✅ **Use:** Alembic migrations for database management  
✅ **Run:** `python scripts/complete_setup.py` for full setup  
✅ **Start:** `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

