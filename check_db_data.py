"""Check database for Twitter records"""
import asyncio
import sys
sys.path.insert(0, '.')
from app.database import get_db
from app.models.social_media_sources import ApifyScrapedData
from sqlalchemy import select

async def check_data():
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Get latest 3 Twitter records
    result = await db.execute(
        select(ApifyScrapedData)
        .where(ApifyScrapedData.platform == 'twitter')
        .order_by(ApifyScrapedData.collected_at.desc())
        .limit(3)
    )
    records = result.scalars().all()
    
    print(f'\n📊 Found {len(records)} Twitter records in database\n')
    
    for i, record in enumerate(records, 1):
        print(f'Record #{i}:')
        print(f'  ID: {record.id}')
        print(f'  Author: @{record.author}')
        print(f'  Content: {record.content[:100] if record.content else "(empty)"}...')
        print(f'  Metrics: {record.metrics_json}')
        print(f'  Hashtags: {record.hashtags}')
        print(f'  Has Raw Data: {bool(record.raw_data)}')
        if record.raw_data:
            print(f'  Raw Data Keys: {list(record.raw_data.keys())[:10]}')
        print()
    
    await db.close()

asyncio.run(check_data())
