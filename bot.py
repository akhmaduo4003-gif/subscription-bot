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
        "practices": [
            "🌬 Дыхание 4-7-8:\nВдох 4 сек, задержка 7, выдох 8.\nПовтори 3 раза. Тревога уходит.",
            "✍️ Запиши 3 вещи за которые ты благодарен прямо сейчас.\nДаже мелочи считаются.",
            "🧘 Техника 5-4-3-2-1:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n2 запаха\n1 вкус\n\nТы здесь. Ты в безопасности.",
            "🚶 Встань и сделай 10 медленных шагов.\nФокус только на ощущениях в ногах.\nМысли утихнут сами.",
            "😮‍💨 Квадратное дыхание:\nВдох 4, задержка 4, выдох 4, задержка 4.\nПовтори 4 раза.",
            "📝 Напиши что тебя сейчас тревожит.\nРядом напиши одно действие которое ты можешь сделать прямо сейчас.",
            "👀 Посмотри вокруг и найди 3 красивые вещи.\nМозг переходит из режима угрозы в режим наблюдения.",
            "💪 Прогрессивная релаксация:\nНапряги кулаки на 5 секунд — отпусти.\nПлечи вверх на 5 секунд — отпусти.\nПочувствуй разницу.",
            "🎵 Включи любимую музыку и просто слушай 5 минут.\nНе делай ничего другого. Только музыка.",
            "🌿 Выйди на воздух на 5 минут.\nСмотри на небо. Дыши медленно.\nПрирода снижает кортизол.",
            "💧 Выпей стакан воды медленно.\nФокусируйся на каждом глотке.\nЭто простой якорь в настоящий момент.",
            "🤲 Положи руку на сердце.\nПочувствуй как оно бьётся.\nСкажи себе: я справляюсь.",
            "📖 Напиши 3 предложения о том как ты себя чувствуешь.\nБез оценок. Просто факты.",
            "🌅 Вспомни момент когда тебе было хорошо.\nДержи его в голове 30 секунд.\nМозг не отличает воспоминание от реальности.",
        ],
        "reflections": [
            "Что сегодня забрало у тебя больше всего энергии?",
            "Какой момент сегодня был самым живым и настоящим?",
            "Что ты сделал для себя сегодня — не для работы, не для других?",
            "Если бы день повторился — что бы ты изменил?",
            "Что тебя порадовало сегодня, даже мелочь?",
            "Какие мысли сегодня забирали больше всего сил?",
            "Что ты хотел сказать кому-то, но не сказал?",
            "Чему ты сегодня научился — о себе или о мире?",
            "Что ты сделал сегодня впервые?",
            "Кому ты сегодня был благодарен, даже молча?",
            "Что тебя удивило сегодня?",
            "Что ты откладывал и почему?",
            "Где ты сегодня был честен с собой?",
            "Что дало тебе энергию сегодня?",
        ],
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
        ],
        "crisis_list": [
            "🌪 Дыхание:\n\n1. Вдох — 4 секунды\n2. Задержка — 4 секунды\n3. Выдох — 6 секунд\nПовтори 5 раз.\n\nТы в безопасности. 💙",
            "🧊 Техника холода:\nВозьми что-то холодное в руки.\nЛёд, холодная вода, металл.\nФокус на ощущении — мозг переключается.",
            "🏃 Физический сброс:\nПрыгни 10 раз.\nИли отожмись.\nИли потряси руками.\nТело сбрасывает адреналин через движение.",
            "💬 Назови эмоцию:\nСкажи вслух: я чувствую тревогу.\nНазывание эмоции снижает её интенсивность на 30%.\nЭто доказано нейронауками.",
            "🌿 Заземление:\nПочувствуй ноги на полу.\nСпина на стуле.\nРуки на коленях.\nТы здесь. Ты реален. Ты в безопасности.",
            "👁 Техника 5-4-3-2-1:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n2 запаха\n1 вкус\n\nТревога отступает.",
        ],
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
        "practices": [
            "🌬 Breathing 4-7-8:\nInhale 4 sec, hold 7, exhale 8.\nRepeat 3 times.",
            "✍️ Write 3 things you are grateful for right now.\nEven small things count.",
            "🧘 Technique 5-4-3-2-1:\n5 things you see\n4 sounds you hear\n3 things you can touch\n2 smells\n1 taste\n\nYou are here. You are safe.",
            "🚶 Stand up and take 10 slow steps.\nFocus only on sensations in your feet.",
            "😮‍💨 Box breathing:\nInhale 4, hold 4, exhale 4, hold 4.\nRepeat 4 times.",
            "📝 Write what worries you right now.\nNext to it write one action you can take right now.",
            "👀 Look around and find 3 beautiful things.\nYour brain shifts from threat mode to observation mode.",
            "💪 Progressive relaxation:\nClench fists for 5 seconds — release.\nShoulders up for 5 seconds — release.\nFeel the difference.",
            "🎵 Play your favorite music and just listen for 5 minutes.\nDo nothing else. Just music.",
            "🌿 Go outside for 5 minutes.\nLook at the sky. Breathe slowly.",
            "💧 Drink a glass of water slowly.\nFocus on each sip.\nA simple anchor to the present moment.",
            "🤲 Place your hand on your heart.\nFeel it beating.\nSay to yourself: I am managing.",
        ],
        "reflections": [
            "What took the most energy from you today?",
            "What moment today felt most real and alive?",
            "What did you do for yourself today — not for work, not for others?",
            "If the day repeated — what would you change?",
            "What made you happy today, even a small thing?",
            "Which thoughts took the most energy today?",
            "What did you want to say to someone but didn't?",
            "What did you learn today — about yourself or the world?",
            "What did you do today for the first time?",
            "Who were you grateful for today, even silently?",
        ],
        "lessons": [
            "🧠 LESSON 1: Anxiety\n\nAnxiety is not weakness.\nIt's your brain signaling a possible threat.\n\nWhat to do:\n1. Notice anxiety without judgment\n2. Ask: is this threat real right now?\n3. Breathe slowly\n4. Take one small action",
            "🚪 LESSON 2: Boundaries\n\nA boundary is a door that you open.\n\nWhy it's hard to say no:\n— Fear of losing relationships\n— We need approval from others\n\nStart small: say no to one thing today.",
            "🕯 LESSON 3: Burnout\n\nBurnout is when you gave so much to others that you forgot to give to yourself.\n\nSymptoms:\n— Everything irritates\n— No energy even for what you love\n— Emptiness\n\nSolution: stop and ask — what do I need right now?",
            "💭 LESSON 4: Inner critic\n\nThat voice saying you are not good enough — it's not true.\n\nWhen you hear the critic — ask:\nWould I say this to a friend?\n\nIf not — don't say it to yourself.",
            "💙 LESSON 5: Self-compassion\n\nYou don't have to be productive every day.\nTreat yourself like a friend who is struggling.\nWith warmth. Without judgment.",
            "😤 LESSON 6: Anger\n\nAnger is a normal emotion.\nIt tells you your boundaries were violated.\n\nWhat to do:\n1. Acknowledge it — I am angry and that's okay\n2. Find the cause — what was violated?\n3. Express safely — exercise, writing, conversation",
            "😔 LESSON 7: Sadness\n\nDon't suppress sadness.\nIt comes when we lose something important.\n\nAllow yourself to be sad.\nSadness passes faster when you don't suppress it.",
            "🔄 LESSON 8: Habits\n\nThe brain loves automation.\n20 days — a habit forms.\n66 days — it becomes automatic.\n\nWant to change your life — change one small habit.\nNot ten. One.",
        ],
        "crisis_list": [
            "🌪 Breathing:\n\n1. Breathe in — 4 seconds\n2. Hold — 4 seconds\n3. Breathe out — 6 seconds\nRepeat 5 times.\n\nYou are safe. 💙",
            "🧊 Cold technique:\nHold something cold in your hands.\nIce, cold water, metal.\nFocus on the sensation.",
            "🏃 Physical reset:\nJump 10 times.\nOr do pushups.\nOr shake your hands.\nThe body releases adrenaline through movement.",
            "💬 Name the emotion:\nSay out loud: I feel anxious.\nNaming an emotion reduces its intensity by 30%.",
            "🌿 Grounding:\nFeel your feet on the floor.\nBack on the chair.\nHands on your knees.\nYou are here. You are real. You are safe.",
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
        error_text = "Что-то пошло не так. Попробуй ещё раз." if lang == "ru" else "Something went wrong. Please try again."
        await thinking.edit_text(error_text, reply_markup=menu_keyboard(lang))
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    except Exception as e:
    print(f"GEMINI ERROR: {repr(e)}")  # увидишь в логах Railway
    error_text = "Что-то пошло не так. Попробуй ещё раз." if lang == "ru" else "Something went wrong. Please try again."
    await thinking.edit_text(error_text, reply_markup=menu_keyboard(lang))
