import asyncio, aiosqlite
from datetime import datetime, timedelta

async def add():
    async with aiosqlite.connect('users.db') as db:
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        await db.execute(
            'INSERT INTO subscribers (user_id, expires_at) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET expires_at = ?',
            (1001401247, expires, expires)
        )
        await db.commit()
        print('Done!')

asyncio.run(add())
