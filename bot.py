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

# ============================================================
# КОНТЕНТ — РУССКИЙ
# ============================================================
PRACTICES_RU = [
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
    "🕯 Зажги свечу или включи тёплый свет.\nПосиди 3 минуты, просто наблюдая за пламенем или светом.\nЭто снижает уровень возбуждения нервной системы.",
    "🖐 Техника заземления через руки:\nПотри ладони друг о друга 10 секунд.\nПочувствуй тепло.\nПрижми их к щекам.",
    "📞 Напиши сообщение человеку, которому давно не писал.\nНе обязательно важное — просто «привет, думаю о тебе».\nСвязь снижает тревогу.",
    "🎯 Выбери одну маленькую задачу на 5 минут и сделай её прямо сейчас.\nЗавершённое действие даёт мозгу ощущение контроля.",
    "🌳 Найди глазами что-то зелёное — растение, дерево, траву.\nСмотри на это 1 минуту.\nЗелёный цвет физиологически успокаивает.",
    "✋ Сожми и разожми кулаки 10 раз медленно.\nС каждым разжатием представляй, что отпускаешь напряжение.",
    "📋 Составь список из 3 дел на сегодня — не больше.\nВычеркни то, что не обязательно делать именно сегодня.\nМеньше пунктов — меньше тревоги.",
    "🛁 Умойся прохладной водой.\nЗадержи внимание на ощущении воды на коже 10 секунд.\nЭто быстрый сброс возбуждения.",
    "🪑 Сядь прямо, расправь плечи, подними подбородок на 5 градусов.\nТело влияет на эмоции не меньше, чем эмоции на тело.",
    "📓 Допиши предложение: «Сейчас мне нужно...»\nНе думай долго — пиши первое, что пришло.\nЧасто ответ удивляет своей простотой.",
    "🌙 Перед сном вспомни 1 хороший момент дня.\nДаже если день был тяжёлым — момент найдётся.",
    "🔄 Смени позу или место, где сидишь.\nФизическая смена положения помогает прервать цикл навязчивых мыслей.",
    "🎨 Нарисуй что угодно 2 минуты — не для результата, для процесса.\nДвижение руки переключает мозг с тревоги на действие.",
    "💌 Напиши себе одно доброе предложение, как будто пишешь лучшему другу.\nПрочитай его вслух.",
    "🧩 Назови вслух 5 предметов одного цвета вокруг себя.\nПростая задача занимает внимание и снижает тревогу.",
    "⏸ Сделай паузу на 60 секунд — просто ничего не делай.\nНе телефон, не музыка. Просто пауза.\nЭто сложнее, чем кажется, и в этом смысл.",
    "🌤 Подумай о завтрашнем дне и выбери ОДНО, чего ты хочешь от него.\nНе план — просто намерение.",
]

REFLECTIONS_RU = [
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
    "Какое решение сегодня было самым трудным?",
    "Что бы ты сказал себе утренним сегодняшнего дня, если бы мог?",
    "Был ли момент, когда ты гордился собой сегодня?",
    "Что ты делал на автомате, не замечая этого?",
    "Какая эмоция была сегодня самой сильной?",
    "Что бы изменилось, если бы ты позволил себе чуть больше отдыха сегодня?",
    "Кого ты сегодня избегал и почему?",
    "Какой маленький шаг ты сделал в сторону того, чего хочешь?",
    "Что сегодня показало тебе, что ты сильнее, чем думаешь?",
    "Где ты сегодня сказал «да», хотя хотел сказать «нет»?",
    "Что в твоём теле говорило тебе сегодня — усталость, напряжение, лёгкость?",
    "Какую мысль ты сегодня повторял чаще остальных?",
    "Что тебе хочется отпустить перед тем как заснуть?",
    "Какой момент дня ты хотел бы сохранить дольше?",
    "Что сегодня напомнило тебе, кто ты на самом деле?",
    "Если бы завтра был последний обычный день — что бы ты сделал иначе сегодня?",
]

LESSONS_RU_NEW = [
    "🔥 УРОК 11: Мотивация\n\nМотивация не приходит первой — она приходит ПОСЛЕ действия, а не до него.\n\nОшибка: «я начну, когда появится настрой».\nПравда: настрой появляется через 5-10 минут после старта.\n\nПравило двух минут: начни на 2 минуты. Дальше мозг сам втянется.",
    "⏳ УРОК 12: Прокрастинация\n\nПрокрастинация — это не лень. Это избегание неприятного чувства, связанного с задачей (страх, скука, перегруз).\n\nЧто делать:\n1. Назови чувство — что именно я избегаю?\n2. Уменьши задачу до смешного маленького шага\n3. Сделай только этот шаг",
    "🏝 УРОК 13: Одиночество\n\nОдиночество — это не количество людей рядом, а ощущение непонятости.\n\nМожно быть одиноким в толпе и не одиноким в тишине одного.\n\nШаг: напиши одному человеку честное сообщение о том, как ты на самом деле. Связь начинается с честности.",
    "🎯 УРОК 14: Перфекционизм\n\nПерфекционизм маскируется под высокие стандарты, но на деле — это страх быть недостаточно хорошим.\n\nВопрос себе: что будет, если это будет «достаточно хорошо», а не «идеально»?\n\nЧасто ответ: ничего страшного не произойдёт.",
    "🪞 УРОК 15: Самооценка\n\nСамооценка — не «я хороший» или «я плохой». Это способность видеть себя реалистично, с сильными и слабыми сторонами.\n\nУпражнение: напиши 3 своих сильных стороны и 1 зону роста. Без преувеличения в обе стороны.",
    "🌊 УРОК 16: Эмоциональная регуляция\n\nЭмоция длится в среднем 90 секунд, если её не подкармливать мыслями.\n\nКогда накатывает: не подавляй и не раздувай. Просто наблюдай, как волна — она поднимается и опускается сама.",
    "🧱 УРОК 17: Контроль\n\nТревога часто растёт из попытки контролировать то, что неподконтрольно.\n\nРаздели лист на 2 колонки: «Что я могу контролировать» и «Что не могу».\nЭнергию вкладывай только в первую колонку.",
    "💬 УРОК 18: Конфликты\n\nЗдоровый конфликт — это не отсутствие разногласий, а способность их обсуждать без потери уважения.\n\nФормула: «Я чувствую [эмоция], когда [ситуация], потому что [причина]».\nЭто снижает защитную реакцию у собеседника.",
    "🎭 УРОК 19: Синдром самозванца\n\nЧувство «я тут случайно, скоро все поймут что я не справляюсь» — испытывают даже эксперты с 20-летним стажем.\n\nФакт: компетентность не убирает это чувство полностью. Действуй вопреки нему, а не жди, когда оно исчезнет.",
    "🪢 УРОК 20: Созависимость\n\nЗабота о другом не должна стирать заботу о себе.\n\nПризнак нездоровой динамики: твоё спокойствие полностью зависит от настроения другого человека.\n\nШаг: спроси себя ежедневно — а что нужно мне сегодня?",
    "🌱 УРОК 21: Рост через дискомфорт\n\nВсё, что важно в жизни, находится за пределами зоны комфорта — но не далеко за ней, а чуть-чуть.\n\nЗона роста — это лёгкий дискомфорт, не паника. Если страшно очень сильно — шаг слишком большой, уменьши его.",
    "🕰 УРОК 22: Прошлое и настоящее\n\nМозг иногда реагирует на сегодняшнюю ситуацию реакцией из прошлого опыта — это называется триггер.\n\nКогда реакция кажется слишком сильной для ситуации: спроси — это про сейчас, или про что-то старое?",
    "🎁 УРОК 23: Благодарность как практика\n\nБлагодарность — не позитивное мышление и не отрицание трудностей.\n\nЭто способность видеть и трудность, и хорошее одновременно. Оба правда. Тренировка благодарности меняет структуру внимания за 3 недели регулярной практики.",
    "🚪 УРОК 24: Перемены\n\nЛюбая перемена, даже хорошая, вызывает стресс — потому что мозг теряет предсказуемость.\n\nЕсли тебе тревожно перед хорошим изменением в жизни — это нормально, не знак того, что решение неверное.",
    "🧭 УРОК 25: Ценности vs цели\n\nЦель — это пункт назначения. Ценность — это направление, в котором можно двигаться всегда.\n\nЦели достигаются и заканчиваются. Ценности (честность, забота, рост) — можно проживать каждый день, независимо от результата.",
    "🛑 УРОК 26: Эмоциональное выгорание vs усталость\n\nУсталость проходит после отдыха. Выгорание не проходит после выходных — потому что причина не в нехватке сна, а в нехватке смысла или контроля.\n\nЕсли отдых не помогает — ищи не больше сна, а источник истощения.",
    "🎻 УРОК 27: Чувствительность\n\nВысокая чувствительность — не слабость. Это особенность нервной системы обрабатывать больше информации глубже.\n\nЕсли тебя называли «слишком чувствительным» — это часто означает «достаточно глубоким для тех, кто привык к поверхности».",
    "🪨 УРОК 28: Устойчивость (резильентность)\n\nУстойчивость — не отсутствие падений, а скорость возвращения после них.\n\nЕё можно тренировать, как мышцу: каждый раз, когда ты восстанавливаешься после трудного дня, ты укрепляешь именно этот навык.",
    "🌑 УРОК 29: Принятие того, что нельзя изменить\n\nПринятие — не согласие, что всё нормально. Это признание реальности такой, какая она есть, чтобы перестать тратить силы на борьбу с фактом.\n\nЭнергия, которая уходила на «не должно было быть так», освобождается для «что теперь делать».",
    "🌟 УРОК 30: Твой прогресс\n\nЗа эти 30 дней ты прикасался к тревоге, границам, выгоранию, критику внутри себя, злости, грусти, привычкам, отношениям, мотивации, перфекционизму и многому другому.\n\nЭто не значит, что всё решено — но ты теперь знаешь больше языков для разговора с собой. Возвращайся к любому уроку снова, когда понадобится.",
]

CRISIS_RU_NEW = [
    "🌪 Дыхание:\n\n1. Вдох — 4 секунды\n2. Задержка — 4 секунды\n3. Выдох — 6 секунд\nПовтори 5 раз.\n\nТы в безопасности. 💙",
    "🧊 Техника холода:\nВозьми что-то холодное в руки.\nЛёд, холодная вода, металл.\nФокус на ощущении — мозг переключается.",
    "🏃 Физический сброс:\nПрыгни 10 раз.\nИли отожмись.\nИли потряси руками.\nТело сбрасывает адреналин через движение.",
    "💬 Назови эмоцию:\nСкажи вслух: я чувствую тревогу.\nНазывание эмоции снижает её интенсивность на 30%.\nЭто доказано нейронауками.",
    "🌿 Заземление:\nПочувствуй ноги на полу.\nСпина на стуле.\nРуки на коленях.\nТы здесь. Ты реален. Ты в безопасности.",
    "👁 Техника 5-4-3-2-1:\n5 вещей которые видишь\n4 звука которые слышишь\n3 вещи которых можешь коснуться\n2 запаха\n1 вкус\n\nТревога отступает.",
    "🤲 Бабочка-объятие:\nСкрести руки на груди, ладони на плечах.\nМедленно похлопывай попеременно левой и правой рукой.\nЭто билатеральная стимуляция, снижает остроту переживания.",
    "🧴 Резкий запах:\nПонюхай что-то с сильным запахом — кофе, мяту, эфирное масло.\nРезкий сенсорный сигнал прерывает спираль тревожных мыслей.",
    "🔢 Счёт в обратном порядке:\nСчитай от 100 назад через 7: 100, 93, 86...\nЗадача требует концентрации и не оставляет места тревоге.",
    "🖼 Безопасное место:\nЗакрой глаза. Представь место, где тебе спокойно.\nКакие звуки там? Какой свет? Подержи картинку 30 секунд.",
    "💧 Холодная вода на запястья:\nДержи запястья под холодной водой 20 секунд.\nЭто быстро снижает физиологическое возбуждение.",
    "🗣 Позвони или напиши близкому человеку:\nДаже простое «мне тревожно, можешь побыть на связи» — снижает интенсивность переживания.",
]

# ============================================================
# КОНТЕНТ — АНГЛИЙСКИЙ
# ============================================================
PRACTICES_EN = [
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
    "📖 Write 3 sentences about how you feel.\nNo judgment. Just facts.",
    "🌅 Recall a moment when you felt good.\nHold it in your mind for 30 seconds.\nThe brain doesn't fully distinguish memory from reality.",
    "🕯 Light a candle or turn on warm light.\nSit for 3 minutes, just watching the flame or light.\nThis lowers nervous system arousal.",
    "🖐 Grounding through hands:\nRub your palms together for 10 seconds.\nFeel the warmth.\nPress them to your cheeks.",
    "📞 Text someone you haven't talked to in a while.\nNot necessarily important — just \"hey, thinking of you\".\nConnection lowers anxiety.",
    "🎯 Pick one tiny task and do it right now, for 5 minutes.\nA completed action gives the brain a sense of control.",
    "🌳 Find something green with your eyes — a plant, tree, grass.\nLook at it for 1 minute.\nGreen is physiologically calming.",
    "✋ Clench and release your fists 10 times slowly.\nWith each release, imagine letting go of tension.",
    "📋 Make a list of just 3 things to do today.\nCross out anything that doesn't have to happen today.\nFewer items, less anxiety.",
    "🛁 Wash your face with cool water.\nFocus on the sensation on your skin for 10 seconds.\nA fast way to reset arousal.",
    "🪑 Sit up straight, relax your shoulders, lift your chin slightly.\nThe body influences emotion as much as emotion influences the body.",
    "📓 Finish the sentence: \"Right now I need...\"\nDon't overthink — write the first thing that comes.\nThe answer is often surprisingly simple.",
    "🌙 Before sleep, recall one good moment from today.\nEven on hard days, there's always one.",
    "🔄 Change your posture or where you're sitting.\nA physical shift can interrupt a loop of repetitive thoughts.",
    "🎨 Draw anything for 2 minutes — not for the result, for the process.\nMoving your hand shifts the brain from anxiety to action.",
    "💌 Write yourself one kind sentence, as if writing to your best friend.\nRead it out loud.",
    "🧩 Name 5 objects of the same color around you out loud.\nA simple task occupies attention and lowers anxiety.",
    "⏸ Pause for 60 seconds — do nothing.\nNo phone, no music. Just pause.\nHarder than it sounds, and that's the point.",
    "🌤 Think about tomorrow and pick ONE thing you want from it.\nNot a plan — just an intention.",
]

REFLECTIONS_EN = [
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
    "What surprised you today?",
    "What did you put off doing, and why?",
    "Where were you honest with yourself today?",
    "What gave you energy today?",
    "What decision today was the hardest?",
    "What would you tell yourself this morning if you could?",
    "Was there a moment today you felt proud of yourself?",
    "What did you do on autopilot without noticing?",
    "Which emotion was strongest today?",
    "What would change if you allowed yourself a bit more rest today?",
    "Who did you avoid today, and why?",
    "What small step did you take toward something you want?",
    "What showed you today that you're stronger than you think?",
    "Where did you say \"yes\" today when you wanted to say \"no\"?",
    "What was your body telling you today — tiredness, tension, ease?",
    "Which thought did you repeat most often today?",
    "What do you want to let go of before falling asleep?",
    "Which part of today would you want to keep a little longer?",
    "What reminded you today of who you really are?",
    "If tomorrow were the last ordinary day, what would you do differently today?",
]

LESSONS_EN_NEW = [
    "🔥 LESSON 11: Motivation\n\nMotivation doesn't come first — it comes AFTER action, not before.\n\nThe trap: \"I'll start once I feel motivated.\"\nThe truth: motivation usually shows up 5-10 minutes after you start.\n\nThe two-minute rule: begin for just 2 minutes. The brain takes it from there.",
    "⏳ LESSON 12: Procrastination\n\nProcrastination isn't laziness. It's avoidance of an uncomfortable feeling tied to the task (fear, boredom, overwhelm).\n\nWhat to do:\n1. Name the feeling — what am I actually avoiding?\n2. Shrink the task to a ridiculously small step\n3. Do only that step",
    "🏝 LESSON 13: Loneliness\n\nLoneliness isn't about how many people are around you — it's the feeling of not being understood.\n\nYou can feel lonely in a crowd and not lonely in quiet solitude.\n\nTry this: send one honest message to someone about how you really feel. Connection starts with honesty.",
    "🎯 LESSON 14: Perfectionism\n\nPerfectionism disguises itself as high standards, but underneath it's often fear of not being good enough.\n\nAsk yourself: what would happen if this were \"good enough\" instead of \"perfect\"?\n\nOften: nothing bad at all.",
    "🪞 LESSON 15: Self-esteem\n\nSelf-esteem isn't \"I'm good\" or \"I'm bad\". It's the ability to see yourself realistically — strengths and growth areas both.\n\nExercise: write 3 strengths and 1 growth area. No exaggeration either way.",
    "🌊 LESSON 16: Emotional regulation\n\nAn emotion lasts about 90 seconds on average if you don't feed it with thoughts.\n\nWhen it hits: don't suppress, don't amplify. Just watch it like a wave — it rises and falls on its own.",
    "🧱 LESSON 17: Control\n\nAnxiety often grows from trying to control what can't be controlled.\n\nSplit a page into two columns: \"What I can control\" and \"What I can't\".\nPut your energy only into the first column.",
    "💬 LESSON 18: Conflict\n\nHealthy conflict isn't the absence of disagreement — it's the ability to discuss it without losing respect.\n\nFormula: \"I feel [emotion] when [situation] because [reason].\"\nThis lowers defensiveness in the other person.",
    "🎭 LESSON 19: Impostor syndrome\n\nThe feeling \"I'm here by accident, soon everyone will realize I can't actually do this\" — even 20-year experts feel it.\n\nFact: competence doesn't fully erase this feeling. Act despite it rather than waiting for it to disappear.",
    "🪢 LESSON 20: Codependency\n\nCaring for someone shouldn't erase caring for yourself.\n\nA sign of unhealthy dynamics: your calm depends entirely on someone else's mood.\n\nTry asking yourself daily — what do I need today?",
    "🌱 LESSON 21: Growth through discomfort\n\nEverything meaningful in life lives just outside your comfort zone — not far outside, just slightly.\n\nThe growth zone feels like mild discomfort, not panic. If it feels like panic, the step is too big — shrink it.",
    "🕰 LESSON 22: Past and present\n\nSometimes the brain reacts to today's situation with a reaction from past experience — that's called a trigger.\n\nWhen a reaction feels too big for the situation, ask: is this about now, or about something old?",
    "🎁 LESSON 23: Gratitude as practice\n\nGratitude isn't positive thinking or denial of hardship.\n\nIt's the ability to hold both the hard thing and the good thing at once. Both are true. Regular gratitude practice reshapes attention within about 3 weeks.",
    "🚪 LESSON 24: Change\n\nAny change, even a good one, creates stress — because the brain loses predictability.\n\nIf you feel anxious before a good life change, that's normal — not a sign the decision is wrong.",
    "🧭 LESSON 25: Values vs goals\n\nA goal is a destination. A value is a direction you can move toward at any time.\n\nGoals get reached and end. Values (honesty, care, growth) can be lived every day, regardless of outcome.",
    "🛑 LESSON 26: Burnout vs tiredness\n\nTiredness goes away after rest. Burnout doesn't go away after a weekend — because the cause isn't lack of sleep, it's lack of meaning or control.\n\nIf rest isn't helping, look for the source of depletion, not more sleep.",
    "🎻 LESSON 27: Sensitivity\n\nHigh sensitivity isn't weakness. It's a nervous system that processes more information, more deeply.\n\nIf you've been called \"too sensitive\", it often means \"too deep for people used to the surface\".",
    "🪨 LESSON 28: Resilience\n\nResilience isn't the absence of falling — it's the speed of getting back up.\n\nIt can be trained like a muscle: every time you recover from a hard day, you strengthen exactly this skill.",
    "🌑 LESSON 29: Accepting what can't be changed\n\nAcceptance isn't agreeing that everything is fine. It's acknowledging reality as it is, so you stop spending energy fighting the fact itself.\n\nThe energy that went into \"this shouldn't be happening\" becomes free for \"what now\".",
    "🌟 LESSON 30: Your progress\n\nOver these 30 days you've touched anxiety, boundaries, burnout, your inner critic, anger, sadness, habits, relationships, motivation, perfectionism, and more.\n\nThis doesn't mean everything is solved — but you now have more language for talking to yourself. Come back to any lesson whenever you need it.",
]

CRISIS_EN_NEW = [
    "🌪 Breathing:\n\n1. Breathe in — 4 seconds\n2. Hold — 4 seconds\n3. Breathe out — 6 seconds\nRepeat 5 times.\n\nYou are safe. 💙",
    "🧊 Cold technique:\nHold something cold in your hands.\nIce, cold water, metal.\nFocus on the sensation.",
    "🏃 Physical reset:\nJump 10 times.\nOr do pushups.\nOr shake your hands.\nThe body releases adrenaline through movement.",
    "💬 Name the emotion:\nSay out loud: I feel anxious.\nNaming an emotion reduces its intensity by 30%.",
    "🌿 Grounding:\nFeel your feet on the floor.\nBack on the chair.\nHands on your knees.\nYou are here. You are real. You are safe.",
    "👁 Technique 5-4-3-2-1:\n5 things you see\n4 sounds you hear\n3 things you can touch\n2 smells\n1 taste\n\nAnxiety recedes.",
    "🤲 Butterfly hug:\nCross your arms over your chest, hands on shoulders.\nTap alternately, left and right, slowly.\nThis is bilateral stimulation — it softens intensity.",
    "🧴 Strong scent:\nSmell something with a strong scent — coffee, mint, essential oil.\nA sharp sensory cue interrupts the anxiety spiral.",
    "🔢 Count backwards:\nCount down from 100 by 7s: 100, 93, 86...\nThe task demands focus and leaves no room for anxious thoughts.",
    "🖼 Safe place:\nClose your eyes. Picture a place where you feel calm.\nWhat sounds are there? What light? Hold the image for 30 seconds.",
    "💧 Cold water on wrists:\nHold your wrists under cold water for 20 seconds.\nThis quickly lowers physiological arousal.",
    "🗣 Call or text someone close:\nEven a simple \"I'm anxious, can you stay on the line\" lowers the intensity of what you're feeling.",
]

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
            "🧠 LESSON 1: Anxiety\n\nAnxiety is not weakness.\nIt's your brain signaling a possible threat.\n\nWhat to do:\n1. Notice anxiety without judgment\n2. Ask: is this threat real right now?\n3. Breathe slowly\n4. Take one small action",
            "🚪 LESSON 2: Boundaries\n\nA boundary is a door that you open.\n\nWhy it's hard to say no:\n— Fear of losing relationships\n— We need approval from others\n\nStart small: say no to one thing today.",
            "🕯 LESSON 3: Burnout\n\nBurnout is when you gave so much to others that you forgot to give to yourself.\n\nSymptoms:\n— Everything irritates\n— No energy even for what you love\n— Emptiness\n\nSolution: stop and ask — what do I need right now?",
            "💭 LESSON 4: Inner critic\n\nThat voice saying you are not good enough — it's not true.\n\nWhen you hear the critic — ask:\nWould I say this to a friend?\n\nIf not — don't say it to yourself.",
            "💙 LESSON 5: Self-compassion\n\nYou don't have to be productive every day.\nTreat yourself like a friend who is struggling.\nWith warmth. Without judgment.",
            "😤 LESSON 6: Anger\n\nAnger is a normal emotion.\nIt tells you your boundaries were violated.\n\nWhat to do:\n1. Acknowledge it — I am angry and that's okay\n2. Find the cause — what was violated?\n3. Express safely — exercise, writing, conversation",
            "😔 LESSON 7: Sadness\n\nDon't suppress sadness.\nIt comes when we lose something important.\n\nAllow yourself to be sad.\nSadness passes faster when you don't suppress it.",
            "🔄 LESSON 8: Habits\n\nThe brain loves automation.\n20 days — a habit forms.\n66 days — it becomes automatic.\n\nWant to change your life — change one small habit.\nNot ten. One.",
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