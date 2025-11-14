#!/usr/bin/env python3
"""Test PostgreSQL database connection"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """Test database connection"""
    database_url = os.getenv('DATABASE_URL')
    print(f"Testing connection to: {database_url}")

    engine = create_async_engine(database_url)

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT version()'))
            version = result.scalar()
            print(f"✅ PostgreSQL connection successful!")
            print(f"Version: {version}")

            # Test if tables exist
            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            )
            table_count = result.scalar()
            print(f"Tables in database: {table_count}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        await engine.dispose()

    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)