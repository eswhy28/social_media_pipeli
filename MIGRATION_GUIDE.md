# Database Migration Guide

## Overview

This project uses Alembic for database migrations. All social media source tables are configured and ready for migration.

## Migration Files

### Existing Migrations

1. **001_initial_migration.py** - Initial database schema
   - Creates base tables: users, social_posts, sentiment_timeseries, etc.

2. **002_add_social_media_sources.py** - Social media integration tables
   - `google_trends_data` - Google Trends data
   - `tiktok_content` - TikTok videos
   - `facebook_content` - Facebook posts
   - `apify_scraped_data` - Multi-platform Apify data
   - `social_media_aggregation` - Cross-platform metrics
   - `data_source_monitoring` - Health monitoring

## Running Migrations

### 1. Check Current Migration Status

```bash
alembic current
```

### 2. View Migration History

```bash
alembic history --verbose
```

### 3. Run All Pending Migrations

```bash
alembic upgrade head
```

### 4. Rollback to Previous Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 001
```

### 5. Generate New Migration (Auto-detect changes)

```bash
alembic revision --autogenerate -m "Description of changes"
```

## Migration Process Flow

```
Current Database State
         |
         v
[Check: alembic current]
         |
         v
[View pending: alembic history]
         |
         v
[Apply: alembic upgrade head]
         |
         v
[Verify: Check tables in database]
```

## Verification

### Check Tables Were Created

```bash
# For SQLite
sqlite3 social_media.db ".tables"

# For PostgreSQL
psql -d your_database -c "\dt"
```

### Verify Specific Table Structure

```bash
# For SQLite
sqlite3 social_media.db ".schema google_trends_data"

# For PostgreSQL
psql -d your_database -c "\d google_trends_data"
```

## Troubleshooting

### Issue: "MissingGreenlet" or "await_only()" error

**Problem**: Alembic is trying to use async database driver in sync context

**Solution**: Already fixed in `alembic/env.py`
```python
# Convert async URL to sync URL for Alembic
sync_db_url = settings.DATABASE_URL.replace('+aiosqlite', '').replace('+asyncpg', '')
config.set_main_option('sqlalchemy.url', sync_db_url)
```

### Issue: "near '(': syntax error" with `now()`

**Problem**: SQLite doesn't support `now()` function

**Solution**: Already fixed in migration files
- Changed `server_default=sa.text('now()')`
- To `server_default=sa.text('CURRENT_TIMESTAMP')`

### Issue: Migration fails with "Target database is not up to date"

```bash
# Stamp the database with current revision
alembic stamp head
```

### Issue: Need to create new database from scratch

```bash
# Drop all tables (careful!)
# Then run migrations
alembic upgrade head
```

### Issue: Want to test migration without applying

```bash
# Show SQL that would be executed
alembic upgrade head --sql
```

## Environment Configuration

Ensure your `.env` file has the correct database URL:

```bash
# For SQLite (default)
DATABASE_URL=sqlite+aiosqlite:///./social_media.db

# For PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

## Models Configuration

The `alembic/env.py` file is configured to import all models, including:

```python
# Base models from app.models
from app.models import *

# Social media source models
from app.models.social_media_sources import (
    GoogleTrendsData,
    TikTokContent,
    FacebookContent,
    ApifyScrapedData,
    SocialMediaAggregation,
    DataSourceMonitoring
)
```

## Creating Custom Migrations

### Manual Migration Example

```bash
# Create empty migration file
alembic revision -m "add_new_column"
```

Edit the generated file:

```python
def upgrade() -> None:
    op.add_column('table_name',
        sa.Column('new_column', sa.String(100), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('table_name', 'new_column')
```

## Best Practices

1. **Always backup your database before running migrations**
   ```bash
   # For SQLite
   cp social_media.db social_media.db.backup
   ```

2. **Test migrations in development first**
   - Never run untested migrations in production

3. **Review auto-generated migrations**
   - Alembic's autogenerate may miss some changes
   - Always review generated migration files

4. **Use descriptive migration messages**
   ```bash
   alembic revision -m "add_user_preferences_table"
   ```

5. **Keep migrations sequential**
   - Don't modify old migrations after they've been applied

## Database Schema Versions

| Revision | Description | Tables Added/Modified |
|----------|-------------|----------------------|
| 001 | Initial schema | 20+ base tables |
| 002 | Social media sources | 6 new tables |

## Next Steps After Migration

1. **Verify tables exist**:
   ```python
   from app.database import AsyncSessionLocal
   from sqlalchemy import inspect

   async with AsyncSessionLocal() as db:
       inspector = inspect(db.bind)
       tables = await inspector.get_table_names()
       print(tables)
   ```

2. **Run test data insertion**:
   ```bash
   python -c "from app.services.data_pipeline_service import DataPipelineService; # test code"
   ```

3. **Start application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## References

- Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Project Database Models: `app/models/` directory