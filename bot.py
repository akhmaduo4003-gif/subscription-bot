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
    "🌬 Дыхание 4-7-8:\nВдох 4 сек, задержка 7, выдох 8.\nПовтори 3 раза. Тревога уходит.",
    "✍️ Запиши 3 вещи за которые ты благодарен прямо сейчас.\nДаже мелочи считаются.",
    "🧘 Техника 5-4-3-2-1:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n2 запаха\n1 вкус\n\nТы здесь. Ты в безопасности.",
    "🚶 Встань и сделай 10 медленных шагов.\nФокус только на ощущениях в ногах.\nМысли утихнут сами.",
    "😮‍💨 Квадратное дыхание:\nВдох 4, задержка 4, выдох 4, задержка 4.\nПовтори 4 раза.",
    "📝 Напиши что тебя сейчас тревожит.\nРядом напиши одно действие которое ты можешь сделать прямо сейчас.",
    "👀 Посмотри вокруг и найди 3 красивые вещи.\nМозг переходит из режима угрозы в режим наблюдения.",
]

REFLECTIONS = [
    "Что сегодня забрало у тебя больше всего энергии?",
    "Какой момент сегодня был самым живым и настоящим?",
    "Что ты сделал для себя сегодня — не для работы, не для других?",
    "Если бы день повторился — что бы ты изменил?",
    "Что тебя порадовало сегодня, даже мелочь?",
    "Какие мысли сегодня забирали больше всего сил?",
    "Что ты хотел сказать кому-то, но не сказал?",
]

LESSONS = [
    "🧠 УРОК 1: Тревога\n\nТревога — это не слабость.\nЭто сигнал мозга о возможной угрозе.\n\nПроблема в том что мозг не различает реальную угрозу от воображаемой.\n\nЧто делать:\n1. Замети тревогу без осуждения\n2. Спроси: эта угроза реальна прямо сейчас?\n3. Дыши медленно\n4. Сделай одно маленькое действие",
    "🚪 УРОК 2: Границы\n\nГраница — это дверь которую открываешь ты.\n\nПочему тяжело говорить нет:\n— Боимся потерять отношения\n— Нам нужно одобрение других\n\nНо без границ ты теряешь себя.\n\nНачни с малого: откажи в одном маленьком деле сегодня.",
    "🕯 УРОК 3: Выгорание\n\nВыгорание — когда ты так долго давал другим\nчто забыл давать себе.\n\nСимптомы:\n— Всё раздражает\n— Нет сил даже на любимое\n— Пустота\n\nВыход: остановись и спроси — что мне сейчас нужно?",
    "💭 УРОК 4: Внутренний критик\n\nТот голос который говорит ты недостаточно хорош — это не правда.\n\nЭто усвоенные чужие слова из прошлого.\n\nКогда слышишь критика — спроси:\nЯ бы сказал это другу?\n\nЕсли нет — не говори себе.",
    "💙 УРОК 5: Самосострадание\n\nТы не обязан быть продуктивным каждый день.\nТы не обязан всегда быть в ресурсе.\n\nОтносись к себе как к другу которому плохо.\nС теплом. Без осуждения.\n\nЭто не слабость — это сила.",
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
        InlineKeyboardButton(text="⭐ Подписка 30 дней — 450 Stars", callback_data="subscribe")
    ]])

def menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Практика", callback_data="practice"),
         InlineKeyboardButton(text="🌙 Рефлексия", callback_data="reflection")],
        [InlineKeyboardButton(text="🌪 Помощь при тревоге", callback_data="crisis"),
         InlineKeyboardButton(text="🧠 Урок", callback_data="lesson")],
        [InlineKeyboardButton(text="✅ Мой статус", callback_data="status")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🧠 Психология в кармане\n\n"
        "Ежедневные практики от тревоги, выгорания и для саморазвития.\n\n"
        "С подпиской ты получаешь:\n"
        "🔹 Ежедневная практика\n"
        "🔹 Вечерний вопрос для рефлексии\n"
        "🔹 Помощь при тревоге\n"
        "🔹 Уроки по психологии\n\n"
        "450 Stars в месяц 👇",
        reply_markup=sub_keyboard()
    )

@dp.callback_query(F.data == "practice")
async def cb_practice(callback):
    if not await is_subscribed(callback.from_user.id):
        await callback.answer("Только для подписчиков", show_alert=True)
        return
    await callback.message.answer("💡 Практика дня:\n\n" + random.choice(PRACTICES), reply_markup=menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "reflection")
async def cb_reflection(callback):
    if not await is_subscribed(callback.from_user.id):
        await callback.answer("Только для подписчиков", show_alert=True)
        return
    await callback.message.answer("🌙 Вечерний вопрос:\n\n" + random.choice(REFLECTIONS), reply_markup=menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "crisis")
async def cb_crisis(callback):
    if not await is_subscribed(callback.from_user.id):
        await callback.answer("Только для подписчиков", show_alert=True)
        return
    await callback.message.answer(
        "🌪 Помощь при тревоге:\n\n"
        "1. Вдох — 4 секунды\n"
        "2. Задержка — 4 секунды\n"
        "3. Выдох — 6 секунд\n"
        "Повтори 5 раз.\n\n"
        "Затем назови вслух:\n"
        "5 вещей которые видишь\n"
        "4 звука которые слышишь\n"
        "3 вещи которых можешь коснуться\n\n"
        "Ты в безопасности. Ты справишься. 💙",
        reply_markup=menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "lesson")
async def cb_lesson(callback):
    if not await is_subscribed(callback.from_user.id):
        await callback.answer("Только для подписчиков", show_alert=True)
        return
    await callback.message.answer(random.choice(LESSONS), reply_markup=menu_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "status")
async def cb_status(callback):
    if await is_subscribed(callback.from_user.id):
        async with aiosqlite.connect(DB) as db:
            async with db.execute("SELECT expires_at FROM subscribers WHERE user_id = ?", (callback.from_user.id,)) as cursor:
                row = await cursor.fetchone()
                exp = datetime.fromisoformat(row[0]).strftime("%d.%m.%Y")
        await callback.message.answer(f"✅ Подписка активна до {exp}", reply_markup=menu_keyboard())
    else:
        await callback.message.answer("❌ Нет активной подписки.", reply_markup=sub_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "subscribe")
async def send_invoice(callback):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Психология в кармане — 30 дней",
        description="Ежедневные практики, помощь при тревоге и уроки психологии",
        payload="sub_30d",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Подписка", amount=450)],
        start_parameter="sub"
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def payment_done(message: Message):
    await add_subscriber(message.from_user.id, days=30)
    await message.answer(
        "🎉 Оплата прошла! Подписка активна 30 дней.\n\nВыбери что делать:",
        reply_markup=menu_keyboard()
    )

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
