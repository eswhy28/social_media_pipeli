# Setup & Troubleshooting Guide Index

## Quick Links

### 🚀 Getting Started
- **[ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)** - Complete guide for database setup using Alembic migrations
- **[STARTUP_FIX.md](STARTUP_FIX.md)** - Fix "duplicate index" errors when starting the app

### 🔧 Setup Scripts

**Recommended: Complete Setup (Database + Data + AI)**
```bash
python scripts/complete_setup.py
```
This does everything: clean database, migrations, import data, and AI processing.

**Alternative: Database Only**
```bash
python scripts/setup_with_alembic.py
```
Just creates tables using Alembic migrations.

**Legacy: Direct Table Creation** (Not recommended)
```bash
python scripts/create_all_tables.py
python scripts/reset_database.py
```

### 📚 Documentation Files

1. **[ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)** - Using Alembic for database migrations
2. **[STARTUP_FIX.md](STARTUP_FIX.md)** - Application startup issues
3. **[DATABASE_SETUP_FIX.md](DATABASE_SETUP_FIX.md)** - Docker & PostgreSQL setup issues
4. **[IMMEDIATE_FIX.md](IMMEDIATE_FIX.md)** - Quick fixes for common problems

### ⚠️ Common Issues & Solutions

#### Issue 1: "relation already exists" or "duplicate index"
**Solution:** Run complete setup
```bash
python scripts/complete_setup.py
```
See: [STARTUP_FIX.md](STARTUP_FIX.md)

#### Issue 2: "relation does not exist"  
**Solution:** Tables not created. Run:
```bash
alembic upgrade head
# or
python scripts/complete_setup.py
```
See: [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)

#### Issue 3: Docker container issues
**Solution:** Check container and superuser
```bash
docker ps | grep postgres
docker exec postgres psql -U sa -d social_media_pipeline -c '\dt'
```
See: [DATABASE_SETUP_FIX.md](DATABASE_SETUP_FIX.md)

### 🎯 Typical Workflow

#### First Time Setup
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run complete setup (database + data + AI)
python scripts/complete_setup.py

# 3. Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Test
curl http://localhost:8000/health
```

#### After Schema Changes
```bash
# 1. Create migration
alembic revision --autogenerate -m "description"

# 2. Review the migration file in alembic/versions/

# 3. Apply migration
alembic upgrade head

# 4. Restart app (if running)
```

#### Resetting Everything
```bash
# Clean database and start fresh
python scripts/complete_setup.py
```

### 📊 Available Scripts

#### Setup Scripts (in `scripts/` directory)
- **complete_setup.py** - Full setup: clean DB, migrations, import data, AI processing
- **setup_with_alembic.py** - Database setup with Alembic only
- **create_all_tables.py** - Create tables directly (legacy)
- **reset_database.py** - Interactive database reset
- **force_reset_database.py** - Non-interactive database reset

#### Data & Import Scripts
- **import_data.py** - Import JSON data files
- **setup_intelligence_system.py** - Run AI processing on existing data

#### Verification Scripts
- **verify_database.sh** - Check database status
- **check_db.py** - Detailed database inspection
- **verify_ai_system.py** - Verify AI processing is working

### 🔍 Quick Diagnostics

```bash
# Check if database exists
docker exec postgres psql -U sa -d mydb -c '\l'

# List tables
docker exec postgres psql -U sa -d social_media_pipeline -c '\dt'

# Check table counts
docker exec postgres psql -U sa -d social_media_pipeline -c "
  SELECT 
    schemaname,
    COUNT(*) as table_count 
  FROM pg_tables 
  WHERE schemaname = 'public' 
  GROUP BY schemaname;
"

# Check Alembic migration status
alembic current
alembic history

# Verify app can connect
curl http://localhost:8000/health
```

### 🎓 Learning Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### 🆘 Still Having Issues?

1. Check the specific guide:
   - Database issues → [DATABASE_SETUP_FIX.md](DATABASE_SETUP_FIX.md)
   - Startup issues → [STARTUP_FIX.md](STARTUP_FIX.md)
   - Alembic questions → [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)

2. Run diagnostics:
   ```bash
   ./verify_database.sh
   python scripts/check_db.py
   ```

3. Nuclear option (clean slate):
   ```bash
   python scripts/complete_setup.py
   ```

