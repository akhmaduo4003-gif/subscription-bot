import asyncio
from datetime import datetime, timedelta
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from dotenv import load_dotenv
import os, random
from google import genai

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
DB = "users.db"
chat_history = {}
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CONTENT = {
    "ru": {
        "start": "🧠 Психология в кармане\n\nЕжедневные практики от тревоги, выгорания и для саморазвития.\n\nС подпиской ты получаешь:\n🔹 Ежедневная практика\n🔹 Вечерний вопрос для рефлексии\n🔹 Помощь при тревоге\n🔹 Уроки по психологии\n🔹 Личный AI-психолог\n\n450 Stars в месяц 👇",
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
        "ai_thinking": "🤔 Думаю...",
        "ai_nosub": "💬 Личный AI-психолог доступен только подписчикам.\n\nОформи подписку чтобы получить поддержку:",
        "crisis": "🌪 Помощь при тревоге:\n\n1. Вдох — 4 секунды\n2. Задержка — 4 секунды\n3. Выдох — 6 секунд\nПовтори 5 раз.\n\nЗатем назови вслух:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n\nТы в безопасности. Ты справишься. 💙",
       "practices": PRACTICES_RU,
        "reflections": REFLECTIONS_RU,
        "lessons": [
            "🧠 УРОК 1: Тревога\n\nТревога — это не слабость.\nЭто сигнал мозга о возможной угрозе.\n\nПроблема в том что мозг не различает реальную угрозу от воображаемой.\n\nЧто делать:\n1. Замети тревогу без осуждения\n2. Спроси: эта угроза реальна прямо сейчас?\n3. Дыши медленно\n4. Сделай одно маленькое действие",
            "🚪 УРОК 2: Границы\n\nГраница — это дверь которую открываешь ты.\n\nПочему тяжело говорить нет:\n— Боимся потерять отношения\n— Нам нужно одобрение других\n\nНачни с малого: откажи в одном деле сегодня.",
            "🕯 УРОК 3: Выгорание\n\nВыгорание — когда ты так долго давал другим что забыл давать себе.\n\nСимптомы:\n— Всё раздражает\n— Нет сил даже на любимое\n— Пустота\n\nВыход: остановись и спроси — что мне сейчас нужно?",
            "💭 УРОК 4: Внутренний критик\n\nТот голос который говорит ты недостаточно хорош — это не правда.\n\nКогда слышишь критика — спроси:\nЯ бы сказал это другу?\n\nЕсли нет — не говори себе.",
            "💙 УРОК 5: Самосострадание\n\nТы не обязан быть продуктивным каждый день.\nОтносись к себе как к другу которому плохо.\nС теплом. Без осуждения.",
            "😤 УРОК 6: Злость\n\nЗлость — это нормальная эмоция.\nОна говорит что твои границы нарушены.\n\nЧто делать со злостью:\n1. Признай её — я злюсь и это нормально\n2. Найди причину — что именно нарушено?\n3. Вырази безопасно — спорт, письмо, разговор",
            "😔 УРОК 7: Грусть\n\nГрусть не надо заглушать.\nОна приходит когда мы потеряли что-то важное.\n\nПозволь себе погрустить.\nЭто не слабость — это честность с собой.\n\nГрусть проходит быстрее когда её не подавляют.",
            "🔄 УРОК 8: Привычки\n\nМозг любит автоматизм.\n20 дней — формируется привычка.\n66 дней — она становится автоматической.\n\nХочешь изменить жизнь — измени одну маленькую привычку.\nНе десять. Одну.",
            "🛌 УРОК 9: Сон и психика\n\nНедосып — главная причина тревоги и раздражительности.\n\n7-9 часов сна = стабильная психика.\n\nЛайфхак: ложись в одно время каждый день.\nМозг начнёт засыпать автоматически через 2 недели.",
            "🤝 УРОК 10: Отношения\n\nЗдоровые отношения строятся на трёх вещах:\n1. Безопасность — можно быть собой\n2. Уважение — границы соблюдаются\n3. Поддержка — рядом в трудный момент\n\nЕсли одного нет — стоит поговорить.",
        ] + LESSONS_RU_NEW,
        "crisis_list": CRISIS_RU_NEW,
    },
    "en": {
        "start": "🧠 Psychology in Pocket\n\nDaily practices for anxiety, burnout and self-development.\n\nWith subscription you get:\n🔹 Daily practice\n🔹 Evening reflection question\n🔹 Crisis help\n🔹 Psychology lessons\n🔹 Personal AI psychologist\n\n450 Stars per month 👇",
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
        "ai_thinking": "🤔 Thinking...",
        "ai_nosub": "💬 Personal AI psychologist is available for subscribers only.\n\nGet a subscription to receive support:",
        "crisis": "🌪 Crisis help:\n\n1. Breathe in — 4 seconds\n2. Hold — 4 seconds\n3. Breathe out — 6 seconds\nRepeat 5 times.\n\nThen name out loud:\n5 things you see\n4 sounds you hear\n3 things you can touch\n\nYou are safe. You will be okay. 💙",
       "practices": PRACTICES_EN,
        "reflections": REFLECTIONS_EN,
        "lessons": [
            "🧠 УРОК 1: Тревога\n\nТревога — это не слабость.\nЭто сигнал мозга о возможной угрозе.\n\nПроблема в том что мозг не различает реальную угрозу от воображаемой.\n\nЧто делать:\n1. Замети тревогу без осуждения\n2. Спроси: эта угроза реальна прямо сейчас?\n3. Дыши медленно\n4. Сделай одно маленькое действие",
            "🚪 УРОК 2: Границы\n\nГраница — это дверь которую открываешь ты.\n\nПочему тяжело говорить нет:\n— Боимся потерять отношения\n— Нам нужно одобрение других\n\nНачни с малого: откажи в одном деле сегодня.",
            "🕯 УРОК 3: Выгорание\n\nВыгорание — когда ты так долго давал другим что забыл давать себе.\n\nСимптомы:\n— Всё раздражает\n— Нет сил даже на любимое\n— Пустота\n\nВыход: остановись и спроси — что мне сейчас нужно?",
            "💭 УРОК 4: Внутренний критик\n\nТот голос который говорит ты недостаточно хорош — это не правда.\n\nКогда слышишь критика — спроси:\nЯ бы сказал это другу?\n\nЕсли нет — не говори себе.",
            "💙 УРОК 5: Самосострадание\n\nТы не обязан быть продуктивным каждый день.\nОтносись к себе как к другу которому плохо.\nС теплом. Без осуждения.",
            "😤 УРОК 6: Злость\n\nЗлость — это нормальная эмоция.\nОна говорит что твои границы нарушены.\n\nЧто делать со злостью:\n1. Признай её — я злюсь и это нормально\n2. Найди причину — что именно нарушено?\n3. Вырази безопасно — спорт, письмо, разговор",
            "😔 УРОК 7: Грусть\n\nГрусть не надо заглушать.\nОна приходит когда мы потеряли что-то важное.\n\nПозволь себе погрустить.\nЭто не слабость — это честность с собой.\n\nГрусть проходит быстрее когда её не подавляют.",
            "🔄 УРОК 8: Привычки\n\nМозг любит автоматизм.\n20 дней — формируется привычка.\n66 дней — она становится автоматической.\n\nХочешь изменить жизнь — измени одну маленькую привычку.\nНе десять. Одну.",
            "🛌 УРОК 9: Сон и психика\n\nНедосып — главная причина тревоги и раздражительности.\n\n7-9 часов сна = стабильная психика.\n\nЛайфхак: ложись в одно время каждый день.\nМозг начнёт засыпать автоматически через 2 недели.",
            "🤝 УРОК 10: Отношения\n\nЗдоровые отношения строятся на трёх вещах:\n1. Безопасность — можно быть собой\n2. Уважение — границы соблюдаются\n3. Поддержка — рядом в трудный момент\n\nЕсли одного нет — стоит поговорить.",
        ] + LESSONS_EN_NEW,
        "crisis_list": CRISIS_EN_NEW,
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

@dp.message(Command("adduser"))
async def cmd_adduser(message: Message):
    if message.from_user.id != 1001401247:
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /adduser ID")
        return
    user_id = int(parts[1])
    await add_subscriber(user_id, days=30)
    await message.answer(f"Done! User {user_id} subscribed for 30 days.")

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
    await callback.message.answer(random.choice(c["crisis_list"]), reply_markup=menu_keyboard(lang))
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
        footer = f"\n\n⏳ Следующий урок завтра." if lesson_index + 1 < total else "\n\n✅ Ты прошёл все уроки!"
    else:
        header = f"📚 Lesson {lesson_index + 1} of {total}\n\n"
        footer = f"\n\n⏳ Next lesson tomorrow." if lesson_index + 1 < total else "\n\n✅ You completed all lessons!"
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

@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    c = CONTENT[lang]
    if not await is_subscribed(user_id):
        await message.answer(c["ai_nosub"], reply_markup=sub_keyboard(lang))
        return
    thinking = await message.answer(c["ai_thinking"])
    system = (
        "Ты тёплый и поддерживающий психолог-ассистент. "
        "Отвечай коротко — максимум 2-3 абзаца. "
        "Не ставь диагнозы. Не давай медицинских советов. "
        "Помогай человеку разобраться в своих чувствах и найти практические шаги. "
        "Отвечай на том же языке на котором пишет пользователь. "
        "Учитывай предыдущие сообщения в разговоре и не теряй контекст."
    )

    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({"role": "user", "text": message.text})
    chat_history[user_id] = chat_history[user_id][-10:]

    conversation = ""
    for msg in chat_history[user_id]:
        role = "Пользователь" if msg["role"] == "user" else "Ассистент"
        conversation += f"{role}: {msg['text']}\n"

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: gemini.models.generate_content(
                model="gemini-2.5-flash",
                contents=system + "\n\nИстория разговора:\n" + conversation + "\nАссистент:"
            )
        )
        reply_text = response.text
        chat_history[user_id].append({"role": "assistant", "text": reply_text})
        chat_history[user_id] = chat_history[user_id][-10:]
        await thinking.edit_text(reply_text, reply_markup=menu_keyboard(lang))
    except Exception as e:
        print(f"GEMINI ERROR: {repr(e)}")
        error_text = "Что-то пошло не так. Попробуй ещё раз." if lang == "ru" else "Something went wrong. Please try again."
        await thinking.edit_text(error_text, reply_markup=menu_keyboard(lang))
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
