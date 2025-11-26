# Using Alembic for Database Migrations

## Quick Start

### Option 1: Automated Setup (Recommended)
This script cleans the database and runs all migrations:

```bash
cd /home/aminu/projects/social_media_pipeli
source venv/bin/activate
python scripts/setup_with_alembic.py
```

### Option 2: Manual Alembic Commands

#### Clean the database first (removes all data):
```bash
docker exec postgres psql -U sa -d social_media_pipeline -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO sa; GRANT ALL ON SCHEMA public TO public;"
```

#### Run all migrations:
```bash
alembic upgrade head
```

#### Check migration status:
```bash
alembic current
alembic history
```

## Available Migrations

1. **001_initial_migration** - Creates users and social_posts tables
2. **002_add_social_media_sources** - Adds Google Trends, TikTok, Facebook, Apify tables
3. **003_add_ai_analysis_tables** - Adds AI analysis tables (sentiment, entities, keywords, etc.)

## Common Alembic Commands

### Check current migration version:
```bash
alembic current
```

### View migration history:
```bash
alembic history --verbose
```

### Upgrade to latest:
```bash
alembic upgrade head
```

### Upgrade one version:
```bash
alembic upgrade +1
```

### Downgrade one version:
```bash
alembic downgrade -1
```

### Downgrade to specific version:
```bash
alembic downgrade 002
```

### Create a new migration (auto-generate from models):
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create an empty migration:
```bash
alembic revision -m "description"
```

## Verify Tables After Migration

```bash
# List all tables
docker exec postgres psql -U sa -d social_media_pipeline -c '\dt'

# Check a specific table structure
docker exec postgres psql -U sa -d social_media_pipeline -c '\d apify_scraped_data'

# Count tables
docker exec postgres psql -U sa -d social_media_pipeline -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

## Expected Tables After Running All Migrations

After running `alembic upgrade head`, you should have:

**Base Tables (from 001 & 002):**
- users
- social_posts
- google_trends_data
- tiktok_content
- facebook_content
- apify_scraped_data
- social_media_aggregation
- data_source_monitoring

**AI Analysis Tables (from 003):**
- apify_data_processing_status
- apify_sentiment_analysis
- apify_location_extractions
- apify_entity_extractions
- apify_keyword_extractions
- apify_ai_batch_jobs

**Total: 14 tables**

## Troubleshooting

### If you get "Target database is not up to date":
```bash
alembic stamp head
```

### If migrations fail due to existing objects:
```bash
# Option 1: Clean database and start fresh
python scripts/setup_with_alembic.py

# Option 2: Manual SQL cleanup
docker exec postgres psql -U sa -d social_media_pipeline -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO sa;"
alembic upgrade head
```

### If you need to skip a specific migration:
```bash
# Mark migration as applied without running it
alembic stamp 003
```

## Integration with setup.sh

The main `setup.sh` script will be updated to use Alembic migrations instead of creating tables directly.

## Benefits of Using Alembic

1. **Version Control** - Track database schema changes
2. **Reproducible** - Same schema across dev/staging/production
3. **Rollback Support** - Can downgrade if needed
4. **No Conflicts** - Properly handles existing objects
5. **Team Collaboration** - Multiple developers can track schema changes

