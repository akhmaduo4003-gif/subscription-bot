import asyncio
from datetime import datetime, timedelta
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import os, random

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
DB = "users.db"

PRACTICES = [
    "Breathing 4-7-8: inhale 4 sec, hold 7, exhale 8. Repeat 3 times.",
    "Write 3 things you are grateful for right now.",
    "Close your eyes, feel 5 things around you.",
    "Name 5 things you see, 4 you hear, 3 you can touch.",
]

REFLECTIONS = [
    "What took the most energy from you today?",
    "What moment today felt most real and alive?",
    "What did you do today for yourself, not for others?",
]

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                expires_at TEXT
            )
        """)
        await db.commit()

async def is_subscribed(user_id: int) -> bool:
    async with aiosqlite.connect(DB) as db:
        async with db.execute(
            "SELECT expires_at FROM subscribers WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            return datetime.fromisoformat(row[0]) > datetime.now()

async def add_subscriber(user_id: int, days: int = 30):
    expires = (datetime.now() + timedelta(days=days)).isoformat()
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO subscribers (user_id, expires_at)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET expires_at = ?
        """, (user_id, expires, expires))
        await db.commit()

def sub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Subscribe 30 days - 50 Stars", callback_data="subscribe")
    ]])

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello! I am your psychology bot.\n\n/practice - daily practice\n/reflection - evening question\n/crisis - help with anxiety\n/status - subscription status", reply_markup=sub_keyboard())

@dp.message(Command("practice"))
async def cmd_practice(message: Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("Subscribers only.", reply_markup=sub_keyboard())
        return
    await message.answer("Practice of the day:\n\n" + random.choice(PRACTICES))

@dp.message(Command("reflection"))
async def cmd_reflection(message: Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("Subscribers only.", reply_markup=sub_keyboard())
        return
    await message.answer("Evening question:\n\n" + random.choice(REFLECTIONS))

@dp.message(Command("crisis"))
async def cmd_crisis(message: Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("Subscribers only.", reply_markup=sub_keyboard())
        return
    await message.answer("Breathe in for 4 seconds. Hold for 4. Exhale for 6. Repeat 5 times. You will be okay.")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    if await is_subscribed(message.from_user.id):
        async with aiosqlite.connect(DB) as db:
            async with db.execute("SELECT expires_at FROM subscribers WHERE user_id = ?", (message.from_user.id,)) as cursor:
                row = await cursor.fetchone()
                exp = datetime.fromisoformat(row[0]).strftime("%d.%m.%Y")
        await message.answer(f"Active until {exp}")
    else:
        await message.answer("No subscription.", reply_markup=sub_keyboard())

@dp.callback_query(F.data == "subscribe")
async def send_invoice(callback):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Psychology Bot - 30 days",
        description="Daily practices, anxiety help and reflection questions",
        payload="sub_30d",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Subscription", amount=50)],
        start_parameter="sub"
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def payment_done(message: Message):
    await add_subscriber(message.from_user.id, days=30)
    await message.answer("Payment successful! Subscription active for 30 days.\n\n/practice\n/crisis\n/reflection")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

@dp.message(Command("addme"))
async def cmd_addme(message: Message):
    await add_subscriber(message.from_user.id, days=30)
    await message.answer("Done! Subscription active for 30 days.")
