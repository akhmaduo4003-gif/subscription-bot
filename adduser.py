
import asyncio, aiosqlite

from datetime import datetime, timedelta

async def add(user_id):

    async with aiosqlite.connect('users.db') as db:

        expires = (datetime.now() + timedelta(days=30)).isoformat()

        await db.execute("""

            INSERT INTO subscribers (user_id, expires_at)

            VALUES (?, ?)

            ON CONFLICT(user_id) DO UPDATE SET expires_at = ?

        """, (user_id, expires, expires))

        await db.commit()

        print(f'Done! User {user_id} subscribed for 30 days.')

asyncio.run(add(6247857558_ID))

