import logging
import sqlite3
import random
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
BOT_TOKEN = "8400415519:AAETeEt-fAb9JQiXEwSihi1ZYMWaH6U1aUA"

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            money INTEGER DEFAULT 0,
            health INTEGER DEFAULT 100,
            happiness INTEGER DEFAULT 100,
            education_level INTEGER DEFAULT 0,
            job_level INTEGER DEFAULT 0,
            has_apartment INTEGER DEFAULT 0,
            has_laptop INTEGER DEFAULT 0,
            has_vpn INTEGER DEFAULT 0,
            food INTEGER DEFAULT 100,
            cigarettes INTEGER DEFAULT 0,
            vape_type TEXT DEFAULT NULL,
            vape_juice INTEGER DEFAULT 0,
            juice_flavor TEXT DEFAULT NULL,
            snus_packs INTEGER DEFAULT 0,
            snus_strength INTEGER DEFAULT 0,
            has_girlfriend INTEGER DEFAULT 0,
            girlfriend_happiness INTEGER DEFAULT 0,
            age INTEGER DEFAULT 0,
            has_id INTEGER DEFAULT 0,
            last_work_time TEXT,
            last_school_time TEXT,
            last_crime_time TEXT,
            last_date_time TEXT,
            last_smoke_time TEXT,
            last_fraud_time TEXT,
            has_iqos INTEGER DEFAULT 0,
            iqos_sticks INTEGER DEFAULT 0,
            iqos_battery INTEGER DEFAULT 0,
            vape_battery INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def upgrade_db():
    """Обновляет структуру базы данных если она устарела"""
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    new_columns = {
        'has_laptop': 'ALTER TABLE players ADD COLUMN has_laptop INTEGER DEFAULT 0',
        'has_vpn': 'ALTER TABLE players ADD COLUMN has_vpn INTEGER DEFAULT 0',
        'last_smoke_time': 'ALTER TABLE players ADD COLUMN last_smoke_time TEXT',
        'last_fraud_time': 'ALTER TABLE players ADD COLUMN last_fraud_time TEXT',
        'snus_packs': 'ALTER TABLE players ADD COLUMN snus_packs INTEGER DEFAULT 0',
        'snus_strength': 'ALTER TABLE players ADD COLUMN snus_strength INTEGER DEFAULT 0',
        'has_girlfriend': 'ALTER TABLE players ADD COLUMN has_girlfriend INTEGER DEFAULT 0',
        'girlfriend_happiness': 'ALTER TABLE players ADD COLUMN girlfriend_happiness INTEGER DEFAULT 0',
        'has_iqos': 'ALTER TABLE players ADD COLUMN has_iqos INTEGER DEFAULT 0',
        'iqos_sticks': 'ALTER TABLE players ADD COLUMN iqos_sticks INTEGER DEFAULT 0',
        'iqos_battery': 'ALTER TABLE players ADD COLUMN iqos_battery INTEGER DEFAULT 0',
        'vape_battery': 'ALTER TABLE players ADD COLUMN vape_battery INTEGER DEFAULT 0'
    }
    
    for column_name, alter_query in new_columns.items():
        if column_name not in columns:
            cursor.execute(alter_query)
    
    conn.commit()
    conn.close()
    print("База данных успешно обновлена")

def get_player(user_id):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    conn.close()
    
    if player:
        # Безопасное создание словаря с проверкой длины кортежа
        player_dict = {
            'user_id': player[0],
            'username': player[1] if len(player) > 1 else None,
            'money': player[2] if len(player) > 2 else 0,
            'health': player[3] if len(player) > 3 else 100,
            'happiness': player[4] if len(player) > 4 else 100,
            'education_level': player[5] if len(player) > 5 else 0,
            'job_level': player[6] if len(player) > 6 else 0,
            'has_apartment': player[7] if len(player) > 7 else 0,
            'has_laptop': player[8] if len(player) > 8 else 0,
            'has_vpn': player[9] if len(player) > 9 else 0,
            'food': player[10] if len(player) > 10 else 100,
            'cigarettes': player[11] if len(player) > 11 else 0,
            'vape_type': player[12] if len(player) > 12 else None,
            'vape_juice': player[13] if len(player) > 13 else 0,
            'juice_flavor': player[14] if len(player) > 14 else None,
            'snus_packs': player[15] if len(player) > 15 else 0,
            'snus_strength': player[16] if len(player) > 16 else 0,
            'has_girlfriend': player[17] if len(player) > 17 else 0,
            'girlfriend_happiness': player[18] if len(player) > 18 else 0,
            'age': player[19] if len(player) > 19 else 16,
            'has_id': player[20] if len(player) > 20 else 0,
            'last_work_time': player[21] if len(player) > 21 else None,
            'last_school_time': player[22] if len(player) > 22 else None,
            'last_crime_time': player[23] if len(player) > 23 else None,
            'last_date_time': player[24] if len(player) > 24 else None,
            'last_smoke_time': player[25] if len(player) > 25 else None,
            'last_fraud_time': player[26] if len(player) > 26 else None,
            'has_iqos': player[27] if len(player) > 27 else 0,
            'iqos_sticks': player[28] if len(player) > 28 else 0,
            'iqos_battery': player[29] if len(player) > 29 else 0,
            'vape_battery': player[30] if len(player) > 30 else 0,
            'created_at': player[31] if len(player) > 31 else datetime.now().isoformat()
        }
        return player_dict
    return None

def create_player(user_id, username):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO players (user_id, username, age, created_at) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, 16, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_player(user_id, **kwargs):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    
    cursor.execute(f'UPDATE players SET {set_clause} WHERE user_id = ?', values)
    conn.commit()
    conn.close()

def reset_player(user_id, username):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE players SET 
            money = 0,
            health = 100,
            happiness = 50,
            education_level = 0,
            job_level = 0,
            has_apartment = 0,
            has_laptop = 0,
            has_vpn = 0,
            food = 100,
            cigarettes = 0,
            vape_type = NULL,
            vape_juice = 0,
            juice_flavor = NULL,
            snus_packs = 0,
            snus_strength = 0,
            has_girlfriend = 0,
            girlfriend_happiness = 0,
            has_id = 0,
            last_work_time = NULL,
            last_school_time = NULL,
            last_crime_time = NULL,
            last_date_time = NULL,
            last_smoke_time = NULL,
            last_fraud_time = NULL,
            has_iqos = 0,
            iqos_sticks = 0,
            iqos_battery = 0,
            vape_battery = 0
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    player = get_player(user_id)
    if not player:
        create_player(user_id, user.username)
        player = get_player(user_id)
    
    keyboard = [
        ["🏠 Статус", "💼 Работа"],
        ["🛒 Магазин", "🔫 Криминал"],
        ["🏫 Школа", "🚬 Курить/Вейпить/Снюс"],
        ["🏡 Купить квартиру", "💕 Девушка"],
        ["🎂 Отметить ДР", "📋 Получить паспорт"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
👋 Добро пожаловать в Симулятор Жизни, {user.first_name}!

🎯 Ваши цели:
• Заработать деньги 💰 (работа или криминал)
• Купить квартиру 🏡
• Найти девушку 💕
• Не умереть от голода 🍖

📝 Особенности:
- Работать можно с любого возраста
- Можно заниматься криминалом и мошенничеством
- В школе можно курить в туалете (осторожно!)
- Девушка увеличивает счастье
- Можно купить ноутбук для удаленной работы

⚠️ Внимание: курение, вейпинг и снюс в реальной жизни вредят здоровью!
Это всего лишь игра.

Нажмите "🏠 Статус" чтобы увидеть свое состояние!
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    food_decrease = random.randint(5, 15)
    new_food = max(0, player['food'] - food_decrease)
    
    if new_food <= 0:
        health_decrease = 10
        new_health = max(0, player['health'] - health_decrease)
        update_player(user_id, food=new_food, health=new_health)
    else:
        update_player(user_id, food=new_food)
    
    player = get_player(user_id)

    vape_info = ""
    if player['vape_type']:
        battery_status = "🔋" if player['vape_battery'] > 0 else "🪫"
        vape_info = f"\n🔋 Вейп: {player['vape_type']} ({battery_status} {player['vape_battery']}%)"
    if player['vape_juice'] > 0 and player['juice_flavor']:
        vape_info += f"\n💧 Жижа: {player['juice_flavor']} ({player['vape_juice']}мл)"
    
    iqos_info = ""
    if player['has_iqos']:
        battery_status = "🔋" if player['iqos_battery'] > 0 else "🪫"
        iqos_info = f"\n🔥 Айкос: {battery_status} {player['iqos_battery']}%"
        if player['iqos_sticks'] > 0:
            iqos_info += f"\n📦 Стики: {player['iqos_sticks']} шт. (мятные)"
    
    snus_info = ""
    if player['snus_packs'] > 0:
        snus_info = f"\n📦 Снюс: {player['snus_packs']} пачек ({player['snus_strength']} мг)"
    
    girlfriend_info = ""
    if player['has_girlfriend']:
        girlfriend_info = f"\n💕 Девушка: счастье {player['girlfriend_happiness']}/100"
    
    tech_info = ""
    if player['has_laptop']:
        tech_info += "\n💻 Ноутбук: ✅ Есть"
    if player['has_vpn']:
        tech_info += "\n🛡️ VPN: ✅ Есть"
    
    status_text = f"""
📊 ВАШ СТАТУС:

🎂 Возраст: {player['age']} лет
📋 Паспорт: {'✅ Есть' if player['has_id'] else '❌ Нет (нужно 18 лет)'}

💵 Деньги: {player['money']} руб.
❤️ Здоровье: {player['health']}/100
😊 Счастье: {player['happiness']}/100
🍖 Еда: {player['food']}/100

🎓 Образование: {get_education_level_name(player['education_level'])}
💼 Работа: {get_job_level_name(player['job_level'])}
🏡 Квартира: {'✅ Есть' if player['has_apartment'] else '❌ Нет'}
{tech_info}

🚬 Сигареты: {player['cigarettes']} шт.
{vape_info}
{iqos_info}
{snus_info}
{girlfriend_info}

{'⚠️ ВАЖНО: У вас закончилась еда! Здоровье уменьшается!' if player['food'] <= 0 else ''}
{'💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно поешьте!' if player['health'] <= 20 else ''}
    """
    
    await update.message.reply_text(status_text)

def get_education_level_name(level):
    levels = {
        0: "9 классов",
        1: "11 классов", 
        2: "Колледж",
        3: "Университет",
        4: "Аспирантура"
    }
    return levels.get(level, "Неизвестно")

def get_job_level_name(level):
    jobs = {
        0: "Безработный",
        1: "Разнорабочий (50 руб.)",
        2: "Продавец (100 руб.)",
        3: "Офисный работник (200 руб.)", 
        4: "Дальнобойщик (800 руб.)",
        5: "Менеджер (500 руб.)",
        6: "Директор (1000 руб.)",
        7: "Мошенник (600 руб.)",
        8: "Работник ПВЗ (3250 руб.)"  # Новая работа
    }
    return jobs.get(level, "Неизвестно")

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['job_level'] == 0:
        await update.message.reply_text("""
💼 Вам нужна работа!
Сначала получите работу в разделе "Магазин" -> "Устроиться на работу"
        """)
        return
    
    if player['job_level'] == 7 and not player['has_laptop']:
        await update.message.reply_text("""
❌ Для работы мошенником нужен ноутбук!
Купите ноутбук в магазине.
        """)
        return
    
    last_work = datetime.fromisoformat(player['last_work_time']) if player['last_work_time'] else None
    work_cooldown = timedelta(minutes=1)
    
    if last_work and (datetime.now() - last_work) < work_cooldown:
        time_left = work_cooldown - (datetime.now() - last_work)
        await update.message.reply_text(f"⏰ Вы устали! Отдохните {int(time_left.total_seconds() / 60)} минут перед следующей работой.")
        return
    
    earnings = [0, 50, 100, 200, 800, 500, 1000, 600, 3250][player['job_level']]  # Добавлена зарплата ПВЗ
    new_money = player['money'] + earnings
    
    update_player(
        user_id, 
        money=new_money, 
        last_work_time=datetime.now().isoformat(),
        happiness=max(0, player['happiness'] - 5)
    )
    
    job_names = {
        7: "🕵️‍♂️ Провели аферу",
        8: "📦 Поработали в ПВЗ",  # Новая работа
    }
    
    job_name = job_names.get(player['job_level'], "💼 Поработали")
    
    await update.message.reply_text(f"""
{job_name} и заработали {earnings} руб.!
💰 Теперь у вас: {new_money} руб.

😔 Счастье немного уменьшилось...
    """)

# ... (остальные функции остаются без изменений до магазина) ...

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍖 Еда (50 руб.)", callback_data="buy_food")],
        [InlineKeyboardButton("🚬 Сигареты (30 руб.)", callback_data="buy_cigarettes")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить сигареты (100 руб.)", callback_data="buy_cigarettes_adult")],
        [InlineKeyboardButton("💨 Вейпы и жижи", callback_data="vape_shop")],
        [InlineKeyboardButton("🔥 Айкос и стики", callback_data="iqos_shop")],
        [InlineKeyboardButton("⚡ Зарядка устройств (120 руб.)", callback_data="charge_devices")],
        [InlineKeyboardButton("📦 Снюс 500 мг (150 руб.)", callback_data="buy_snus")],
        [InlineKeyboardButton("❤️ Лечение (100 руб.)", callback_data="buy_health")],
        [InlineKeyboardButton("😊 Развлечения (80 руб.)", callback_data="buy_happiness")],
        [InlineKeyboardButton("💼 Устроиться на работу (200 руб.)", callback_data="buy_job")],
        [InlineKeyboardButton("💻 Ноутбук (5000 руб.)", callback_data="buy_laptop")],
        [InlineKeyboardButton("🛡️ VPN (200 руб.)", callback_data="buy_vpn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("""
🛒 МАГАЗИН:

🍖 Еда (50 руб.) - +50 к еде
🚬 Сигареты (30 руб.) - пачка сигарет (только с 18 лет)
🔞 Попросить взрослых (100 руб.) - дороже, но без паспорта
💨 Вейпы и жижи - электронные сигареты и жидкости
🔥 Айкос и стики - системы нагревания табака
⚡ Зарядка устройств (120 руб.) - зарядить вейп/айкос
📦 Снюс 500 мг (150 руб.) - крепкий снюс
❤️ Лечение (100 руб.) - +30 к здоровью
😊 Развлечения (80 руб.) - +40 к счастью
💼 Устроиться на работу (200 руб.) - получить работу
💻 Ноутбук (5000 руб.) - для удаленной работы и мошенничества
🛡️ VPN (200 руб.) - анонимность для мошенничества

Выберите что хотите купить:
    """, reply_markup=reply_markup)

async def vape_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔋 Вейп устройства", callback_data="vape_devices")],
        [InlineKeyboardButton("💧 Жидкости для вейпа", callback_data="vape_juices")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить вейп (300 руб.)", callback_data="buy_vape_adult")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить жижу (250 руб.)", callback_data="buy_juice_adult")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
💨 МАГАЗИН ВЕЙПОВ И ЖИДКОСТЕЙ:

🔋 Вейп устройства - одноразовые и многоразовые
💧 Жидкости - разные вкусы
🔞 Попросить взрослых купить вейп - купить без паспорта
🔞 Попросить взрослых купить жижу - купить без паспорта

⚠️ Для покупки вейпов нужно быть 18+ или попросить взрослых
    """, reply_markup=reply_markup)

async def iqos_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔥 Айкос устройство (800 руб.)", callback_data="buy_iqos")],
        [InlineKeyboardButton("📦 Мятные стики (150 руб.)", callback_data="buy_iqos_sticks")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить айкос (1000 руб.)", callback_data="buy_iqos_adult")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
🔥 МАГАЗИН АЙКОС:

🔥 Айкос устройство - 800 руб. (система нагревания табака)
📦 Мятные стики - 150 руб. (пачка стиков)
🔞 Попросить взрослых купить айкос - 1000 руб. (без паспорта)

⚠️ Для покупки айкос нужно быть 18+ или попросить взрослых
    """, reply_markup=reply_markup)

async def vape_devices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Pasito 2 (400 руб.)", callback_data="buy_pasito2")],
        [InlineKeyboardButton("Xros (350 руб.)", callback_data="buy_xros")],
        [InlineKeyboardButton("Boost 2 (450 руб.)", callback_data="buy_boost2")],
        [InlineKeyboardButton("Minican (300 руб.)", callback_data="buy_minican")],
        [InlineKeyboardButton("Knight (380 руб.)", callback_data="buy_knight")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="vape_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
🔋 ВЕЙП УСТРОЙСТВА:

Pasito 2 - 400 руб. (мощный, многоразовый)
Xros - 350 руб. (компактный)
Boost 2 - 450 руб. (профессиональный)
Minican - 300 руб. (одноразовый)
Knight - 380 руб. (стильный)

Выберите устройство:
    """, reply_markup=reply_markup)

async def vape_juices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🍉 Арбуз и мята (200 руб.)", callback_data="buy_juice_watermelon")],
        [InlineKeyboardButton("🌿 Лесные ягоды и мята (220 руб.)", callback_data="buy_juice_berries")],
        [InlineKeyboardButton("🍌 Анархия: Банан-Малина 70мг (300 руб.)", callback_data="buy_juice_anarchy")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="vape_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
💧 ЖИДКОСТИ ДЛЯ ВЕЙПА:

🍉 Арбуз и мята - 200 руб. (30мл)
🌿 Лесные ягоды и мята - 220 руб. (30мл)
🍌 Анархия: Банан-Малина 70мг - 300 руб. (30мл) - ОЧЕНЬ КРЕПКАЯ!

Жидкости добавляют 30мл к вашему вейпу
    """, reply_markup=reply_markup)

async def handle_shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    player = get_player(user_id)
    
    if not player:
        await query.edit_message_text("Сначала запустите бота командой /start")
        return
    
    if query.data == "vape_shop":
        await vape_shop_menu(update, context)
        return
    elif query.data == "iqos_shop":
        await iqos_shop_menu(update, context)
        return
    elif query.data == "vape_devices":
        await vape_devices_menu(update, context)
        return
    elif query.data == "vape_juices":
        await vape_juices_menu(update, context)
        return
    elif query.data == "back_to_shop":
        await shop_callback(update, context)
        return
    
    item_data = {
        "buy_food": {"price": 50, "type": "food"},
        "buy_cigarettes": {"price": 30, "type": "cigarettes"},
        "buy_cigarettes_adult": {"price": 100, "type": "cigarettes_adult"},
        "buy_health": {"price": 100, "type": "health"},
        "buy_happiness": {"price": 80, "type": "happiness"},
        "buy_job": {"price": 200, "type": "job"},
        "buy_snus": {"price": 150, "type": "snus"},
        "buy_laptop": {"price": 5000, "type": "laptop"},
        "buy_vpn": {"price": 200, "type": "vpn"},
        "buy_pasito2": {"price": 400, "type": "vape_device", "name": "Pasito 2", "battery": 100},
        "buy_xros": {"price": 350, "type": "vape_device", "name": "Xros", "battery": 100},
        "buy_boost2": {"price": 450, "type": "vape_device", "name": "Boost 2", "battery": 100},
        "buy_minican": {"price": 300, "type": "vape_device", "name": "Minican", "battery": 100},
        "buy_knight": {"price": 380, "type": "vape_device", "name": "Knight", "battery": 100},
        "buy_juice_watermelon": {"price": 200, "type": "vape_juice", "flavor": "Арбуз и мята"},
        "buy_juice_berries": {"price": 220, "type": "vape_juice", "flavor": "Лесные ягоды и мята"},
        "buy_juice_anarchy": {"price": 300, "type": "vape_juice", "flavor": "Анархия: Банан-Малина 70мг"},
        "buy_vape_adult": {"price": 300, "type": "vape_adult"},
        "buy_juice_adult": {"price": 250, "type": "juice_adult"},
        "buy_iqos": {"price": 800, "type": "iqos_device", "battery": 100},
        "buy_iqos_sticks": {"price": 150, "type": "iqos_sticks"},
        "buy_iqos_adult": {"price": 1000, "type": "iqos_adult"},
        "charge_devices": {"price": 120, "type": "charge"}
    }
    
    item_info = item_data.get(query.data)
    if not item_info:
        return
    
    price = item_info["price"]
    item_type = item_info["type"]
    
    if item_type in ["cigarettes", "vape_device", "vape_juice", "iqos_device", "iqos_sticks"] and (player['age'] < 18 or not player['has_id']):
        await query.edit_message_text("❌ Для покупки этого товара нужно быть 18+ и иметь паспорт!")
        return
    
    if player['money'] < price:
        await query.edit_message_text(f"❌ Недостаточно денег! Нужно {price} руб., а у вас {player['money']} руб.")
        return
    
    new_money = player['money'] - price
    message = f"✅ Покупка совершена за {price} руб.\n💰 Осталось: {new_money} руб.\n"
    
    if item_type == "food":
        update_player(user_id, money=new_money, food=min(100, player['food'] + 50))
        message += "🍖 +50 к еде"
    elif item_type == "cigarettes":
        update_player(user_id, money=new_money, cigarettes=player['cigarettes'] + 20)
        message += "🚬 +20 сигарет"
    elif item_type == "cigarettes_adult":
        update_player(user_id, money=new_money, cigarettes=player['cigarettes'] + 20)
        message += "🚬 +20 сигарет (через взрослых)"
    elif item_type == "health":
        update_player(user_id, money=new_money, health=min(100, player['health'] + 30))
        message += "❤️ +30 к здоровью"
    elif item_type == "happiness":
        update_player(user_id, money=new_money, happiness=min(100, player['happiness'] + 40))
        message += "😊 +40 к счастью"
    elif item_type == "job":
        if player['job_level'] < 8:  # Теперь максимум 8 уровней работы
            new_job_level = player['job_level'] + 1
            update_player(user_id, money=new_money, job_level=new_job_level)
            message += f"💼 Теперь вы: {get_job_level_name(new_job_level)}"
        else:
            message += "💼 У вас уже максимальный уровень работы!"
    elif item_type == "snus":
        update_player(user_id, money=new_money, snus_packs=player['snus_packs'] + 1, snus_strength=500)
        message += "📦 +1 пачка снюса 500 мг"
    elif item_type == "laptop":
        update_player(user_id, money=new_money, has_laptop=1)
        message += "💻 Вы купили ноутбук! Теперь можете работать удаленно и заниматься мошенничеством"
    elif item_type == "vpn":
        update_player(user_id, money=new_money, has_vpn=1)
        message += "🛡️ Вы купили VPN! Теперь вы более анонимны в интернете"
    elif item_type == "vape_device":
        update_player(user_id, money=new_money, vape_type=item_info["name"], vape_battery=item_info["battery"])
        message += f"🔋 Приобретен вейп: {item_info['name']} (батарея: {item_info['battery']}%)"
    elif item_type == "vape_juice":
        update_player(user_id, money=new_money, vape_juice=player['vape_juice'] + 30, juice_flavor=item_info["flavor"])
        message += f"💧 +30мл жидкости: {item_info['flavor']}"
    elif item_type == "vape_adult":
        vapes = ["Pasito 2", "Xros", "Boost 2", "Minican", "Knight"]
        random_vape = random.choice(vapes)
        update_player(user_id, money=new_money, vape_type=random_vape, vape_battery=100)
        message += f"🔋 Взрослые купили вам вейп: {random_vape} (батарея: 100%)"
    elif item_type == "juice_adult":
        juices = ["Арбуз и мята", "Лесные ягоды и мята", "Анархия: Банан-Малина 70мг"]
        random_juice = random.choice(juices)
        update_player(user_id, money=new_money, vape_juice=player['vape_juice'] + 30, juice_flavor=random_juice)
        message += f"💧 Взрослые купили вам жидкость: {random_juice} (30мл)"
    elif item_type == "iqos_device":
        update_player(user_id, money=new_money, has_iqos=1, iqos_battery=item_info["battery"])
        message += f"🔥 Приобретен Айкос! (батарея: {item_info['battery']}%)"
    elif item_type == "iqos_sticks":
        update_player(user_id, money=new_money, iqos_sticks=player['iqos_sticks'] + 10)
        message += "📦 +10 мятных стиков для Айкос"
    elif item_type == "iqos_adult":
        update_player(user_id, money=new_money, has_iqos=1, iqos_battery=100)
        message += "🔥 Взрослые купили вам Айкос! (батарея: 100%)"
    elif item_type == "charge":
        # Заряжаем оба устройства если они есть
        charge_message = ""
        if player['vape_type'] and player['vape_battery'] < 100:
            update_player(user_id, vape_battery=100)
            charge_message += "🔋 Вейп заряжен до 100%\n"
        if player['has_iqos'] and player['iqos_battery'] < 100:
            update_player(user_id, iqos_battery=100)
            charge_message += "🔥 Айкос заряжен до 100%\n"
        
        if charge_message:
            update_player(user_id, money=new_money)
            message += f"⚡ Устройства заряжены!\n{charge_message}"
        else:
            message = "❌ Нет устройств для зарядки или они уже полностью заряжены!"
            new_money = player['money']  # Не списываем деньги
    
    await query.edit_message_text(message)

# Добавляем новые функции для использования айкос
async def smoke_vape_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    keyboard = [
        ["🚬 Выкурить сигарету", "💨 Покурить вейп"],
        ["🔥 Покурить айкос", "📦 Закинуть снюс"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("""
🚬 Выберите что хотите использовать:

🚬 Сигарета - больше вреда, но дешевле
💨 Вейп - меньше вреда, но нужен вейп и жидкость
🔥 Айкос - система нагревания табака, меньше вреда чем сигареты
📦 Снюс - очень крепкий, большой вред здоровью

⚠️ Помните: в реальной жизни и то и другое вредно для здоровья!
    """, reply_markup=reply_markup)

async def use_iqos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_iqos']:
        await update.message.reply_text("❌ У вас нет Айкос! Купите в магазине.")
        return
    
    if player['iqos_battery'] <= 0:
        await update.message.reply_text("🪫 Айкос разряжен! Зарядите устройство в магазине.")
        return
    
    if player['iqos_sticks'] <= 0:
        await update.message.reply_text("❌ У вас нет стиков для Айкос! Купите в магазине.")
        return
    
    new_sticks = player['iqos_sticks'] - 1
    new_battery = max(0, player['iqos_battery'] - 15)
    new_health = max(0, player['health'] - 10)
    new_happiness = min(100, player['happiness'] + 20)
    
    update_player(
        user_id,
        iqos_sticks=new_sticks,
        iqos_battery=new_battery,
        health=new_health,
        happiness=new_happiness
    )
    
    battery_warning = "🪫 Айкос почти разряжен! Зарядите устройство." if new_battery <= 20 else ""
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно лечитесь!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"""
🔥 Вы покурили Айкос (мятные стики)...

❤️ Здоровье: -10 (теперь {new_health})
😊 Счастье: +20 (теперь {new_happiness})
📦 Стиков осталось: {new_sticks}
🔋 Батарея Айкос: {new_battery}%

{battery_warning}
{health_warning}
⚠️ Курение в реальной жизни вредит здоровью!
    """)

# Обновляем обработчик сообщений для новой функции
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🏠 Статус":
        await show_status(update, context)
    elif text == "💼 Работа":
        await work(update, context)
    elif text == "🔫 Криминал":
        await crime_menu(update, context)
    elif text in ["💰 Украсть кошелек", "🏪 Ограбить магазин", "🏠 Ограбить квартиру", "🚗 Угнать машину", "🕵️‍♂️ Мошенничество"]:
        await commit_crime(update, context)
    elif text == "🛒 Магазин":
        await shop(update, context)
    elif text == "🏫 Школа":
        await school_menu(update, context)
    elif text == "📚 Учиться":
        await study(update, context)
    elif text == "🚬 Сходить в туалет покурить":
        await school_smoke(update, context)
    elif text == "🏡 Купить квартиру":
        await buy_apartment(update, context)
    elif text == "🚬 Курить/Вейпить/Снюс":
        await smoke_vape_menu(update, context)
    elif text == "🚬 Выкурить сигарету":
        await smoke_cigarette(update, context)
    elif text == "💨 Покурить вейп":
        await vape(update, context)
    elif text == "🔥 Покурить айкос":
        await use_iqos(update, context)
    elif text == "📦 Закинуть снюс":
        await use_snus(update, context)
    elif text == "🎂 Отметить ДР":
        await celebrate_birthday(update, context)
    elif text == "📋 Получить паспорт":
        await get_passport(update, context)
    elif text == "💕 Девушка":
        await girlfriend_menu(update, context)
    elif text == "💕 Найти девушку":
        await find_girlfriend(update, context)
    elif text == "💑 Свидание":
        await date_girlfriend(update, context)
    elif text == "🎁 Подарок девушке":
        await gift_girlfriend(update, context)
    elif text == "💔 Расстаться":
        await break_up(update, context)
    elif text in ["⬅️ Назад", "⬅️ Выйти из туалета"]:
        await start(update, context)
    else:
        await update.message.reply_text("Используйте кнопки меню для управления игрой!")

# Обновляем функцию vape для проверки батареи
async def vape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['vape_type']:
        await update.message.reply_text("❌ У вас нет вейпа! Купите в магазине.")
        return
    
    if player['vape_battery'] <= 0:
        await update.message.reply_text("🪫 Вейп разряжен! Зарядите устройство в магазине.")
        return
    
    if player['vape_juice'] <= 0:
        await update.message.reply_text("❌ В вейпе закончилась жидкость! Купите жидкость в магазине.")
        return
    
    new_juice = max(0, player['vape_juice'] - 5)
    new_battery = max(0, player['vape_battery'] - 10)
    new_health = max(0, player['health'] - 8)
    new_happiness = min(100, player['happiness'] + 25)
    
    update_player(
        user_id,
        vape_juice=new_juice,
        vape_battery=new_battery,
        health=new_health,
        happiness=new_happiness
    )
    
    battery_warning = "🪫 Вейп почти разряжен! Зарядите устройство." if new_battery <= 20 else ""
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно лечитесь!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"""
💨 Вы покурили вейп ({player['vape_type']})...

❤️ Здоровье: -8 (теперь {new_health})
😊 Счастье: +25 (теперь {new_happiness})
💧 Жидкости осталось: {new_juice}мл
🔋 Батарея вейпа: {new_battery}%
🎯 Вкус: {player['juice_flavor']}

{battery_warning}
{health_warning}
⚠️ Вейпинг в реальной жизни тоже вреден для здоровья!
    """)

def main():
    init_db()
    upgrade_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^vape_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^iqos_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^charge_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^back_to_shop"))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
