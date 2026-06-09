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
    "Breathing 4-7-8:\nVdoh 4 sek, zaderzhka 7, vydoh 8.\nPovtori 3 raza. Trevoга uhodit.",
    "Zapishi 3 veshi za kotorye ty blagodaren pryamo seychas.\nDazhe melochi schitayutsya.",
    "Tehnika 5-4-3-2-1:\nNazovi 5 veshey kotorye vidish\n4 zvuka kotorye slyshish\n3 veshi kotoryh mozhesh kosnutsya\n2 zapaha\n1 vkus\nTy zdes. Ty v bezopasnosti.",
    "Vstani i sdelai 10 medlennyh shagov.\nFokus tolko na oshushheniyah v nogah.\nMysli utihnut sami.",
    "Napiши chto tebya seychas trevozhit.\nRyadom napishi odno deystvie kotorое ty mozhesh sdelat pryamo seychas.",
    "Kvadratnoe dyhanie:\nVdoh 4, zaderzhka 4, vydoh 4, zaderzhka 4.\nPovtori 4 raza.",
    "Posmotri v okno ili vokrug.\nNaydi 3 krasivye veshi.\nMozg perehodit iz rezhima ugrozy v rezhim nablyudeniya.",
]

REFLECTIONS = [
    "Chto segodnya zabрало u tebya bolshe vsego energii?",
    "Kakoy moment segodnya byl samym zhivym i nastoyashim?",
    "Chto ty sdelal segodnya dlya sebya — ne dlya raboty, ne dlya drugih?",
    "Esli by den povtorilsya — chto by ty izmenil?",
    "Chto tebya poradovalo segodnya, dazhe meloch?",
    "Kakie mysli segodnya zabotali тебя bolshe vsego?",
    "Chto ty hotel skazat komy-to, no ne skazal?",
]

LESSONS = [
    "UROK 1: Trevoга\n\nTrevoga — eto ne slabost. Eto signal mozga o vozmozhnoy ugroze.\n\nProblema v tom chto mozg ne razlichaet realnuyu ugrozu ot voображаемой.\n\nChto delat:\n1. Zameti trevogu bez osuzhdenie\n2. Sprosi sebya: eta ugroza realna pryamo seychas?\n3. Dyshy medlenno — eto signal bezopasnosti dlya mozga\n4. Deystvuy — dazhe malen'koe deystvie snimaet trevogu",
    "UROK 2: Granitsy\n\nGranitsa — eto ne stena. Eto dver kotoruyu otkryvaesh ty.\n\nPochemu tyazhelo govorit net:\n— Nas uchili chto otkaz = egoizm\n— My boymsya poteryat otnosheniya\n— Nam nuzhno odobrenie drugih\n\nNo bez granits ty teryaesh sebya.\n\nNachni s malogo: otkazhi v odnom malom dele segodnya.",
    "UROK 3: Vygoranie\n\nVygoranie — eto kogda ty tak dolgo daval drugim chto zabyl davat sebe.\n\nSimptomy:\n— Vse razdrazhaet\n— Net sil dazhe na to chto ranше nravilos\n— Oshushenie pustoty\n\nVyход:\n1. Ostanovis\n2. Spрosi: chto mne seychas nuzhno?\n3. Day sebe eto bez viny",
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

def menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Practice", callback_data="practice"),
         InlineKeyboardButton(text="Reflection", callback_data="reflection")],
        [InlineKeyboardButton(text="Crisis help", callback_data="crisis"),
         InlineKeyboardButton(text="Lesson", callback_data="lesson")],
        [InlineKeyboardButton(text="Status", callback_data="status")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Psychology in Pocket\n\n"
        "Daily practices for anxiety, burnout and self-development.\n\n"
        "What you get with subscription:\n"
        "- Daily practice\n"
        "- Evening reflection question\n"
        "- Crisis help techniques\n"
        "- Weekly psychology lessons\n\n"
        "50 Stars per month",
        reply_markup=sub_keyboard()
    )

@dp.callback_query(F.data == "practice")
@dp.message(Command("practice"))
async def cmd_practice(update):
    user_id = update.from_user.id
    if not await is_subscribed(user_id):
        if hasattr(update, 'message'):
            await update.message.answer("Subscribers only.", reply_markup=sub_keyboard())
        else:
            await update.answer("Subscribers only.", reply_markup=sub_keyboard(), show_alert=True)
        return
    text = "Practice of the day:\n\n" + random.choice(PRACTICES)
    if hasattr(update, 'message'):
        await update.message.answer(text, reply_markup=menu_keyboard())
    else:
        await update.message.answer(text, reply_markup=menu_keyboard())

@dp.callback_query(F.data == "reflection")
@dp.message(Command("reflection"))
async def cmd_reflection(update):
    user_id = update.from_user.id
    if not await is_subscribed(user_id):
        if hasattr(update, 'message'):
            await update.message.answer("Subscribers only.", reply_markup=sub_keyboard())
        else:
            await update.answer("Subscribers only.", show_alert=True)
        return
    text = "Evening reflection:\n\n" + random.choice(REFLECTIONS)
    if hasattr(update, 'message'):
        await update.message.answer(text, reply_markup=menu_keyboard())
    else:
        await update.message.answer(text, reply_markup=menu_keyboard())

@dp.callback_query(F.data == "crisis")
@dp.message(Command("crisis"))
async def cmd_crisis(update):
    user_id = update.from_user.id
    if not await is_subscribed(user_id):
        if hasattr(update, 'message'):
            await update.message.answer("Subscribers only.", reply_markup=sub_keyboard())
        else:
            await update.answer("Subscribers only.", show_alert=True)
        return
    text = (
        "Crisis help:\n\n"
        "1. Breathe in — 4 seconds\n"
        "2. Hold — 4 seconds\n"
        "3. Breathe out — 6 seconds\n"
        "Repeat 5 times.\n\n"
        "Then name out loud:\n"
        "5 things you see\n"
        "4 sounds you hear\n"
        "3 things you can touch\n\n"
        "You are safe. You will be okay."
    )
    if hasattr(update, 'message'):
        await update.message.answer(text, reply_markup=menu_keyboard())
    else:
        await update.message.answer(text, reply_markup=menu_keyboard())

@dp.callback_query(F.data == "lesson")
@dp.message(Command("lesson"))
async def cmd_lesson(update):
    user_id = update.from_user.id
    if not await is_subscribed(user_id):
        if hasattr(update, 'message'):
            await update.message.answer("Subscribers only.", reply_markup=sub_keyboard())
        else:
            await update.answer("Subscribers only.", show_alert=True)
        return
    text = random.choice(LESSONS)
    if hasattr(update, 'message'):
        await update.message.answer(text, reply_markup=menu_keyboard())
    else:
        await update.message.answer(text, reply_markup=menu_keyboard())

@dp.callback_query(F.data == "status")
@dp.message(Command("status"))
async def cmd_status(update):
    user_id = update.from_user.id
    if await is_subscribed(user_id):
        async with aiosqlite.connect(DB) as db:
            async with db.execute("SELECT expires_at FROM subscribers WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                exp = datetime.fromisoformat(row[0]).strftime("%d.%m.%Y")
        text = f"Subscription active until {exp}"
    else:
        text = "No active subscription."
    if hasattr(update, 'message'):
        await update.message.answer(text, reply_markup=sub_keyboard() if not await is_subscribed(user_id) else menu_keyboard())
    else:
        await update.message.answer(text)

@dp.callback_query(F.data == "subscribe")
async def send_invoice(callback):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Psychology in Pocket - 30 days",
        description="Daily practices, crisis help, reflection and psychology lessons",
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
    await message.answer(
        "Payment successful! Subscription active for 30 days.\n\nChoose what to do:",
        reply_markup=menu_keyboard()
    )

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
