#!/usr/bin/env python3
"""
Complete Database Setup with Alembic and AI Processing
This script will:
1. Clean the database (drop/recreate schema)
2. Run Alembic migrations to create tables
3. Import data from JSON files
4. Run AI processing on imported data
"""

import asyncio
import sys
import subprocess
from pathlib import Path
import os
import glob

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def clean_database():
    """Clean the database by dropping the public schema"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Convert async URL to sync URL for direct SQL execution
    sync_url = DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', '')
    
    print("=" * 80)
    print("STEP 1: Cleaning Database Schema")
    print("=" * 80)
    print()
    
    try:
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            print("  → Dropping public schema...")
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.commit()
            
            print("  → Recreating public schema...")
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
            
            print("  → Granting permissions...")
            conn.execute(text("GRANT ALL ON SCHEMA public TO sa"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
        
        engine.dispose()
        
        print("  ✅ Database cleaned successfully!")
        print()
        return True
        
    except Exception as e:
        print(f"  ❌ Error cleaning database: {e}")
        return False


def run_alembic_migrations():
    """Run Alembic migrations to create all tables"""
    print("=" * 80)
    print("STEP 2: Running Alembic Migrations")
    print("=" * 80)
    print()
    
    try:
        print("  → Running: alembic upgrade head")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        # Show output
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"     {line}")
        
        if result.returncode == 0:
            print()
            print("  ✅ Migrations completed successfully!")
            print()
            return True
        else:
            print()
            print(f"  ❌ Migration failed with return code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error running migrations: {e}")
        return False


def verify_tables():
    """Verify tables were created"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    sync_url = DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', '')
    
    print("=" * 80)
    print("STEP 3: Verifying Tables")
    print("=" * 80)
    print()
    
    try:
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"  ✅ Found {len(tables)} table(s):")
                print()
                for table in tables:
                    print(f"     • {table}")
                print()
            else:
                print("  ⚠️  No tables found!")
                return False
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"  ❌ Error verifying tables: {e}")
        return False


def import_data():
    """Import data from JSON files in data directory"""
    print("=" * 80)
    print("STEP 4: Importing Data")
    print("=" * 80)
    print()
    
    # Check if data directory exists and has JSON files
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print("  ⚠️  No 'data' directory found. Skipping data import.")
        print()
        return False
    
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print("  ⚠️  No JSON files found in 'data' directory. Skipping data import.")
        print()
        return False
    
    print(f"  → Found {len(json_files)} JSON file(s)")
    print()
    
    # Check if import script exists
    import_script = Path(__file__).parent / "import_data.py"
    if not import_script.exists():
        print("  ⚠️  Import script not found: scripts/import_data.py")
        print()
        return False
    
    try:
        print("  → Running data import script...")
        result = subprocess.run(
            ["python", str(import_script)],
            capture_output=True,
            text=True
        )
        
        # Show relevant output
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip() and ('✓' in line or '✅' in line or 'Imported' in line or 'records' in line):
                    print(f"     {line}")
        
        if result.returncode == 0:
            print()
            print("  ✅ Data imported successfully!")
            print()
            return True
        else:
            print()
            print(f"  ⚠️  Import completed with warnings")
            if result.stderr:
                print(f"     {result.stderr[:200]}")
            print()
            return True  # Continue even if there are warnings
            
    except Exception as e:
        print(f"  ❌ Error importing data: {e}")
        print()
        return False


def run_ai_processing():
    """Run AI processing on imported data"""
    print("=" * 80)
    print("STEP 5: Running AI Processing")
    print("=" * 80)
    print()
    
    # Check if AI processing script exists
    ai_script = Path(__file__).parent / "setup_intelligence_system.py"
    if not ai_script.exists():
        print("  ⚠️  AI processing script not found: scripts/setup_intelligence_system.py")
        print()
        return False
    
    try:
        print("  → Running AI analysis (sentiment, entities, locations, keywords)...")
        print()
        result = subprocess.run(
            ["python", str(ai_script)],
            capture_output=True,
            text=True
        )
        
        # Show output with better formatting
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Add indentation to output
                    print(f"     {line}")
        
        if result.returncode == 0:
            print()
            print("  ✅ AI processing completed successfully!")
            print()
            return True
        else:
            print()
            print(f"  ⚠️  AI processing completed with warnings")
            print()
            return True  # Continue even with warnings
            
    except Exception as e:
        print(f"  ❌ Error running AI processing: {e}")
        print()
        return False


def show_summary():
    """Show final summary"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    sync_url = DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', '')
    
    print("=" * 80)
    print("SETUP COMPLETE - SUMMARY")
    print("=" * 80)
    print()
    
    try:
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            # Count tables
            tables_result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = tables_result.scalar()
            
            # Count records in apify_scraped_data
            try:
                data_result = conn.execute(text("SELECT COUNT(*) FROM apify_scraped_data"))
                data_count = data_result.scalar()
            except:
                data_count = 0
            
            # Count sentiment analyses
            try:
                sentiment_result = conn.execute(text("SELECT COUNT(*) FROM apify_sentiment_analysis"))
                sentiment_count = sentiment_result.scalar()
            except:
                sentiment_count = 0
            
            # Count entities
            try:
                entity_result = conn.execute(text("SELECT COUNT(*) FROM apify_entity_extractions"))
                entity_count = entity_result.scalar()
            except:
                entity_count = 0
            
            # Count keywords
            try:
                keyword_result = conn.execute(text("SELECT COUNT(*) FROM apify_keyword_extractions"))
                keyword_count = keyword_result.scalar()
            except:
                keyword_count = 0
            
            print(f"  📊 Database Statistics:")
            print(f"     • Tables created: {table_count}")
            print(f"     • Data records: {data_count}")
            print(f"     • Sentiment analyses: {sentiment_count}")
            print(f"     • Entity extractions: {entity_count}")
            print(f"     • Keyword extractions: {keyword_count}")
            print()
        
        engine.dispose()
        
        print("  🚀 Next Steps:")
        print()
        print("     1. Start the API server:")
        print("        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print()
        print("     2. Access API documentation:")
        print("        http://localhost:8000/docs")
        print()
        print("     3. Test endpoints:")
        print("        curl http://localhost:8000/health")
        print("        curl http://localhost:8000/api/v1/social-media/data/scraped?limit=10")
        print()
        
    except Exception as e:
        print(f"  ⚠️  Could not generate summary: {e}")
        print()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "SOCIAL MEDIA PIPELINE - COMPLETE SETUP" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("This script will:")
    print("  1. Clean the database (removes ALL data)")
    print("  2. Run Alembic migrations to create tables")
    print("  3. Import data from JSON files (if available)")
    print("  4. Run AI processing on imported data")
    print()
    
    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Setup cancelled.")
        sys.exit(0)
    
    print()
    
    # Step 1: Clean database
    if not clean_database():
        print("\n❌ Setup failed at step 1")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_alembic_migrations():
        print("\n❌ Setup failed at step 2")
        sys.exit(1)
    
    # Step 3: Verify tables
    if not verify_tables():
        print("\n❌ Setup failed at step 3")
        sys.exit(1)
    
    # Step 4: Import data (optional - don't fail if no data)
    has_data = import_data()
    
    # Step 5: Run AI processing (only if data was imported)
    if has_data:
        run_ai_processing()
    else:
        print("=" * 80)
        print("STEP 5: Skipping AI Processing (no data imported)")
        print("=" * 80)
        print()
    
    # Show summary
    show_summary()
    
    print("=" * 80)
    print("✅ SETUP COMPLETE!")
    print("=" * 80)
    print()

