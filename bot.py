import asyncio
from datetime import datetime, timedelta
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from dotenv import load_dotenv
import os, random

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
DB = "users.db"

CONTENT = {
    "ru": {
        "start": "🧠 Психология в кармане\n\nЕжедневные практики от тревоги, выгорания и для саморазвития.\n\nС подпиской ты получаешь:\n🔹 Ежедневная практика\n🔹 Вечерний вопрос для рефлексии\n🔹 Помощь при тревоге\n🔹 Уроки по психологии\n\n450 Stars в месяц 👇",
        "sub_btn": "⭐ Подписка 30 дней — 450 Stars",
        "only_subs": "Только для подписчиков",
        "practice_title": "💡 Практика дня:\n\n",
        "reflection_title": "🌙 Вечерний вопрос:\n\n",
        "lesson_title": "",
        "status_active": "✅ Подписка активна до ",
        "status_none": "❌ Нет активной подписки.",
        "paid": "🎉 Оплата прошла! Подписка активна 30 дней.\n\nВыбери что делать:",
        "invoice_title": "Психология в кармане — 30 дней",
        "invoice_desc": "Ежедневные практики, помощь при тревоге и уроки психологии",
        "menu": ["💡 Практика", "🌙 Рефлексия", "🌪 Помощь при тревоге", "🧠 Урок", "✅ Мой статус"],
        "crisis": "🌪 Помощь при тревоге:\n\n1. Вдох — 4 секунды\n2. Задержка — 4 секунды\n3. Выдох — 6 секунд\nПовтори 5 раз.\n\nЗатем назови вслух:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n\nТы в безопасности. Ты справишься. 💙",
        "practices": [
            "🌬 Дыхание 4-7-8:\nВдох 4 сек, задержка 7, выдох 8.\nПовтори 3 раза. Тревога уходит.",
            "✍️ Запиши 3 вещи за которые ты благодарен прямо сейчас.\nДаже мелочи считаются.",
            "🧘 Техника 5-4-3-2-1:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n2 запаха\n1 вкус\n\nТы здесь. Ты в безопасности.",
            "🚶 Встань и сделай 10 медленных шагов.\nФокус только на ощущениях в ногах.\nМысли утихнут сами.",
            "😮‍💨 Квадратное дыхание:\nВдох 4, задержка 4, выдох 4, задержка 4.\nПовтори 4 раза.",
            "📝 Напиши что тебя сейчас тревожит.\nРядом напиши одно действие которое ты можешь сделать прямо сейчас.",
            "👀 Посмотри вокруг и найди 3 красивые вещи.\nМозг переходит из режима угрозы в режим наблюдения.",
        ],
        "reflections": [
            "Что сегодня забрало у тебя больше всего энергии?",
            "Какой момент сегодня был самым живым и настоящим?",
            "Что ты сделал для себя сегодня — не для работы, не для других?",
            "Если бы день повторился — что бы ты изменил?",
            "Что тебя порадовало сегодня, даже мелочь?",
            "Какие мысли сегодня забирали больше всего сил?",
            "Что ты хотел сказать кому-то, но не сказал?",
        ],
        "lessons": [
            "🧠 УРОК 1: Тревога\n\nТревога — это не слабость.\nЭто сигнал мозга о возможной угрозе.\n\nЧто делать:\n1. Замети тревогу без осуждения\n2. Спроси: эта угроза реальна прямо сейчас?\n3. Дыши медленно\n4. Сделай одно маленькое действие",
            "🚪 УРОК 2: Границы\n\nГраница — это дверь которую открываешь ты.\n\nПочему тяжело говорить нет:\n— Боимся потерять отношения\n— Нам нужно одобрение других\n\nНачни с малого: откажи в одном деле сегодня.",
            "🕯 УРОК 3: Выгорание\n\nВыгорание — когда ты так долго давал другим что забыл давать себе.\n\nСимптомы:\n— Всё раздражает\n— Нет сил даже на любимое\n— Пустота\n\nВыход: остановись и спроси — что мне сейчас нужно?",
            "💭 УРОК 4: Внутренний критик\n\nТот голос который говорит ты недостаточно хорош — это не правда.\n\nКогда слышишь критика — спроси:\nЯ бы сказал это другу?\n\nЕсли нет — не говори себе.",
            "💙 УРОК 5: Самосострадание\n\nТы не обязан быть продуктивным каждый день.\nОтносись к себе как к другу которому плохо.\nС теплом. Без осуждения.",
        ],
    },
    "en": {
        "start": "🧠 Psychology in Pocket\n\nDaily practices for anxiety, burnout and self-development.\n\nWith subscription you get:\n🔹 Daily practice\n🔹 Evening reflection question\n🔹 Crisis help\n🔹 Psychology lessons\n\n450 Stars per month 👇",
        "sub_btn": "⭐ Subscribe 30 days — 450 Stars",
        "only_subs": "Subscribers only",
        "practice_title": "💡 Practice of the day:\n\n",
        "reflection_title": "🌙 Evening question:\n\n",
        "lesson_title": "",
        "status_active": "✅ Subscription active until ",
        "status_none": "❌ No active subscription.",
        "paid": "🎉 Payment successful! Subscription active for 30 days.\n\nChoose what to do:",
        "invoice_title": "Psychology in Pocket — 30 days",
        "invoice_desc": "Daily practices, crisis help and psychology lessons",
        "menu": ["💡 Practice", "🌙 Reflection", "🌪 Crisis help", "🧠 Lesson", "✅ My status"],
        "crisis": "🌪 Crisis help:\n\n1. Breathe in — 4 seconds\n2. Hold — 4 seconds\n3. Breathe out — 6 seconds\nRepeat 5 times.\n\nThen name out loud:\n5 things you see\n4 sounds you hear\n3 things you can touch\n\nYou are safe. You will be okay. 💙",
        "practices": [
            "🌬 Breathing 4-7-8:\nInhale 4 sec, hold 7, exhale 8.\nRepeat 3 times. Anxiety fades.",
            "✍️ Write 3 things you are grateful for right now.\nEven small things count.",
            "🧘 Technique 5-4-3-2-1:\n5 things you see\n4 sounds you hear\n3 things you can touch\n2 smells\n1 taste\n\nYou are here. You are safe.",
            "🚶 Stand up and take 10 slow steps.\nFocus only on the sensations in your feet.\nThoughts will quiet down.",
            "😮‍💨 Box breathing:\nInhale 4, hold 4, exhale 4, hold 4.\nRepeat 4 times.",
            "📝 Write what worries you right now.\nNext to it write one action you can take right now.",
            "👀 Look around and find 3 beautiful things.\nYour brain shifts from threat mode to observation mode.",
        ],
        "reflections": [
            "What took the most energy from you today?",
            "What moment today felt most real and alive?",
            "What did you do for yourself today — not for work, not for others?",
            "If the day repeated — what would you change?",
            "What made you happy today, even a small thing?",
            "Which thoughts took the most energy today?",
            "What did you want to say to someone but didn't?",
        ],
        "lessons": [
            "🧠 LESSON 1: Anxiety\n\nAnxiety is not weakness.\nIt's your brain signaling a possible threat.\n\nWhat to do:\n1. Notice anxiety without judgment\n2. Ask: is this threat real right now?\n3. Breathe slowly\n4. Take one small action",
            "🚪 LESSON 2: Boundaries\n\nA boundary is a door that you open.\n\nWhy it's hard to say no:\n— Fear of losing relationships\n— We need approval from others\n\nStart small: say no to one thing today.",
            "🕯 LESSON 3: Burnout\n\nBurnout is when you gave so much to others that you forgot to give to yourself.\n\nSymptoms:\n— Everything irritates\n— No energy even for what you love\n— Emptiness\n\nSolution: stop and ask — what do I need right now?",
            "💭 LESSON 4: Inner critic\n\nThat voice saying you are not good enough — it's not true.\n\nWhen you hear the critic — ask:\nWould I say this to a friend?\n\nIf not — don't say it to yourself.",
            "💙 LESSON 5: Self-compassion\n\nYou don't have to be productive every day.\nTreat yourself like a friend who is struggling.\nWith warmth. Without judgment.",
        ],
    }
}

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                expires_at TEXT,
                lang TEXT DEFAULT 'ru'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'ru'
            )
        """)
        await db.commit()

async def get_lang(user_id: int) -> str:
    async with aiosqlite.connect(DB) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else "ru"

async def set_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO users (user_id, lang) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET lang = ?
        """, (user_id, lang, lang))
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

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
    ]])

def sub_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=CONTENT[lang]["sub_btn"], callback_data="subscribe")
    ]])

def menu_keyboard(lang):
    m = CONTENT[lang]["menu"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m[0], callback_data="practice"),
         InlineKeyboardButton(text=m[1], callback_data="reflection")],
        [InlineKeyboardButton(text=m[2], callback_data="crisis"),
         InlineKeyboardButton(text=m[3], callback_data="lesson")],
        [InlineKeyboardButton(text=m[4], callback_data="status")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌍 Choose your language / Выбери язык:",
        reply_markup=lang_keyboard()
    )

@dp.callback_query(F.data.in_(["lang_ru", "lang_en"]))
async def cb_set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await set_lang(callback.from_user.id, lang)
    c = CONTENT[lang]
    await callback.message.answer(c["start"], reply_markup=menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "practice")
async def cb_practice(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    c = CONTENT[lang]
    if not await is_subscribed(callback.from_user.id):
        await callback.answer(c["only_subs"], show_alert=True)
        return
    await callback.message.answer(c["practice_title"] + random.choice(c["practices"]), reply_markup=menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "reflection")
async def cb_reflection(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    c = CONTENT[lang]
    if not await is_subscribed(callback.from_user.id):
        await callback.answer(c["only_subs"], show_alert=True)
        return
    await callback.message.answer(c["reflection_title"] + random.choice(c["reflections"]), reply_markup=menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "crisis")
async def cb_crisis(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    c = CONTENT[lang]
    if not await is_subscribed(callback.from_user.id):
        await callback.answer(c["only_subs"], show_alert=True)
        return
    await callback.message.answer(c["crisis"], reply_markup=menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "lesson")
async def cb_lesson(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    c = CONTENT[lang]
    if not await is_subscribed(callback.from_user.id):
        await callback.answer(c["only_subs"], show_alert=True)
        return
    async with aiosqlite.connect(DB) as db:
        async with db.execute(
            "SELECT expires_at FROM subscribers WHERE user_id = ?", (callback.from_user.id,)
        ) as cursor:
            row = await cursor.fetchone()
            start = datetime.fromisoformat(row[0]) - timedelta(days=30)
            days_passed = (datetime.now() - start).days
            lesson_index = min(days_passed, len(c["lessons"]) - 1)
    lesson = c["lessons"][lesson_index]
    total = len(c["lessons"])
    if lang == "ru":
        header = f"📚 Урок {lesson_index + 1} из {total}\n\n"
        if lesson_index + 1 < total:
            footer = f"\n\n⏳ Следующий урок откроется завтра."
        else:
            footer = "\n\n✅ Ты прошёл все уроки!"
    else:
        header = f"📚 Lesson {lesson_index + 1} of {total}\n\n"
        if lesson_index + 1 < total:
            footer = f"\n\n⏳ Next lesson unlocks tomorrow."
        else:
            footer = "\n\n✅ You completed all lessons!"
    await callback.message.answer(header + lesson + footer, reply_markup=menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "status")
async def cb_status(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    c = CONTENT[lang]
    if await is_subscribed(callback.from_user.id):
        async with aiosqlite.connect(DB) as db:
            async with db.execute("SELECT expires_at FROM subscribers WHERE user_id = ?", (callback.from_user.id,)) as cursor:
                row = await cursor.fetchone()
                exp = datetime.fromisoformat(row[0]).strftime("%d.%m.%Y")
        await callback.message.answer(c["status_active"] + exp, reply_markup=menu_keyboard(lang))
    else:
        await callback.message.answer(c["status_none"], reply_markup=sub_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "subscribe")
async def send_invoice(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    c = CONTENT[lang]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=c["invoice_title"],
        description=c["invoice_desc"],
        payload="sub_30d",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Subscription", amount=450)],
        start_parameter="sub"
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def payment_done(message: Message):
    lang = await get_lang(message.from_user.id)
    c = CONTENT[lang]
    await add_subscriber(message.from_user.id, days=30)
    await message.answer(c["paid"], reply_markup=menu_keyboard(lang))

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
