#!/usr/bin/env python3
"""
Clean database by dropping the public schema
Then use Alembic to create all tables properly
"""

import asyncio
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()


def clean_database():
    """Clean the database by dropping the public schema"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Convert async URL to sync URL for direct SQL execution
    sync_url = DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', '')
    
    print("=" * 70)
    print("Cleaning Database Schema")
    print("=" * 70)
    print()
    print(f"Database: {sync_url.split('@')[1] if '@' in sync_url else 'localhost'}")
    print()
    
    try:
        # Create synchronous engine
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            # Drop schema cascade (removes everything)
            print("  1. Dropping public schema...")
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.commit()
            print("     ✓ Schema dropped")
            
            # Recreate schema
            print("  2. Recreating public schema...")
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
            print("     ✓ Schema created")
            
            # Grant permissions
            print("  3. Granting permissions...")
            conn.execute(text("GRANT ALL ON SCHEMA public TO sa"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
            print("     ✓ Permissions granted")
        
        engine.dispose()
        
        print()
        print("✅ Database cleaned successfully!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False


def run_alembic_migrations():
    """Run Alembic migrations to create all tables"""
    print("=" * 70)
    print("Running Alembic Migrations")
    print("=" * 70)
    print()
    
    try:
        # Run alembic upgrade to head
        print("Running: alembic upgrade head")
        print()
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print()
            print("✅ Migrations completed successfully!")
            return True
        else:
            print()
            print(f"❌ Migration failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False


def verify_tables():
    """Verify tables were created"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    sync_url = DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', '')
    
    print()
    print("=" * 70)
    print("Verifying Tables")
    print("=" * 70)
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
                print(f"✅ Found {len(tables)} table(s):")
                print()
                for table in tables:
                    print(f"  - {table}")
                print()
            else:
                print("⚠️  No tables found!")
                return False
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False


if __name__ == "__main__":
    print()
    print("This script will:")
    print("  1. Drop the public schema (removes ALL data)")
    print("  2. Recreate the schema")
    print("  3. Run Alembic migrations to create tables")
    print()
    
    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)
    
    print()
    
    # Step 1: Clean database
    if not clean_database():
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_alembic_migrations():
        sys.exit(1)
    
    # Step 3: Verify tables
    if not verify_tables():
        sys.exit(1)
    
    print("=" * 70)
    print("✅ Database setup complete!")
    print("=" * 70)
    print()

