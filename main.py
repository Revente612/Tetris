import logging
import sqlite3
import random
import os
import asyncio
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8400415519:AAETeEt-fAb9JQiXEwSihi1ZYMWaH6U1aUA")

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
            juice_strength INTEGER DEFAULT 0,
            snus_packs INTEGER DEFAULT 0,
            snus_strength INTEGER DEFAULT 0,
            snus_flavor TEXT DEFAULT NULL,
            has_girlfriend INTEGER DEFAULT 0,
            girlfriend_happiness INTEGER DEFAULT 0,
            age INTEGER DEFAULT 14,
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
            has_hookah INTEGER DEFAULT 0,
            hookah_coals INTEGER DEFAULT 0,
            hookah_tobacco TEXT DEFAULT NULL,
            hookah_tobacco_amount INTEGER DEFAULT 0,
            has_burner INTEGER DEFAULT 0,
            disposable_vape_type TEXT DEFAULT NULL,
            disposable_vape_puffs INTEGER DEFAULT 0,
            chapman_cigarettes INTEGER DEFAULT 0,
            on_probation INTEGER DEFAULT 0,
            probation_until TEXT,
            created_at TEXT,
            has_tea_leaf INTEGER DEFAULT 0,
            unconscious_until TEXT,
            stick_flavor TEXT DEFAULT NULL,
            has_nicotine_free_snus INTEGER DEFAULT 0,
            last_smoke_puff_time TEXT,
            consecutive_puffs INTEGER DEFAULT 0,
            has_iphone INTEGER DEFAULT 0,
            has_samsung INTEGER DEFAULT 0,
            parents_angry INTEGER DEFAULT 0,
            parents_angry_until TEXT,
            police_in_school INTEGER DEFAULT 0,
            police_until TEXT,
            winston_cigarettes INTEGER DEFAULT 0,
            parliament_cigarettes INTEGER DEFAULT 0,
            beer INTEGER DEFAULT 0,
            vape_puffs_count INTEGER DEFAULT 0,
            last_uncle_hookah_time TEXT,
            knows_uncle INTEGER DEFAULT 0,
            disposable_vape_defective INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def upgrade_db():
    """Обновляет структуру базы данных если она устарела"""
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = {
            'juice_strength': 'ALTER TABLE players ADD COLUMN juice_strength INTEGER DEFAULT 0',
            'snus_flavor': 'ALTER TABLE players ADD COLUMN snus_flavor TEXT DEFAULT NULL',
            'winston_cigarettes': 'ALTER TABLE players ADD COLUMN winston_cigarettes INTEGER DEFAULT 0',
            'parliament_cigarettes': 'ALTER TABLE players ADD COLUMN parliament_cigarettes INTEGER DEFAULT 0',
            'beer': 'ALTER TABLE players ADD COLUMN beer INTEGER DEFAULT 0',
            'vape_puffs_count': 'ALTER TABLE players ADD COLUMN vape_puffs_count INTEGER DEFAULT 0',
            'last_uncle_hookah_time': 'ALTER TABLE players ADD COLUMN last_uncle_hookah_time TEXT',
            'knows_uncle': 'ALTER TABLE players ADD COLUMN knows_uncle INTEGER DEFAULT 0',
            'disposable_vape_defective': 'ALTER TABLE players ADD COLUMN disposable_vape_defective INTEGER DEFAULT 0'
        }
        
        for column_name, alter_query in new_columns.items():
            if column_name not in columns:
                cursor.execute(alter_query)
        
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении БД: {e}")
    finally:
        conn.close()

def get_player(user_id):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    conn.close()
    
    if player:
        columns = ['user_id', 'username', 'money', 'health', 'happiness', 'education_level', 
                  'job_level', 'has_apartment', 'has_laptop', 'has_vpn', 'food', 'cigarettes',
                  'vape_type', 'vape_juice', 'juice_flavor', 'juice_strength', 'snus_packs', 'snus_strength', 'snus_flavor',
                  'has_girlfriend', 'girlfriend_happiness', 'age', 'has_id', 'last_work_time',
                  'last_school_time', 'last_crime_time', 'last_date_time', 'last_smoke_time',
                  'last_fraud_time', 'has_iqos', 'iqos_sticks', 'iqos_battery', 'vape_battery',
                  'has_hookah', 'hookah_coals', 'hookah_tobacco', 'hookah_tobacco_amount',
                  'has_burner', 'disposable_vape_type', 'disposable_vape_puffs', 'chapman_cigarettes',
                  'on_probation', 'probation_until', 'created_at', 'has_tea_leaf', 'unconscious_until', 
                  'stick_flavor', 'has_nicotine_free_snus', 'last_smoke_puff_time', 'consecutive_puffs',
                  'has_iphone', 'has_samsung', 'parents_angry', 'parents_angry_until', 'police_in_school', 'police_until',
                  'winston_cigarettes', 'parliament_cigarettes', 'beer', 'vape_puffs_count', 'last_uncle_hookah_time', 'knows_uncle', 'disposable_vape_defective']
        
        player_dict = {}
        for i, column in enumerate(columns):
            if i < len(player):
                player_dict[column] = player[i]
            else:
                player_dict[column] = None
        
        # Установка значений по умолчанию
        defaults = {
            'health': 100, 'happiness': 100, 'food': 100, 'age': 14, 'education_level': 0,
            'job_level': 0, 'cigarettes': 0, 'vape_juice': 0, 'snus_packs': 0, 'snus_strength': 0,
            'girlfriend_happiness': 0, 'iqos_sticks': 0, 'iqos_battery': 0, 'vape_battery': 0,
            'has_hookah': 0, 'hookah_coals': 0, 'hookah_tobacco_amount': 0, 'has_burner': 0,
            'disposable_vape_puffs': 0, 'chapman_cigarettes': 0, 'on_probation': 0, 'has_tea_leaf': 0,
            'has_nicotine_free_snus': 0, 'consecutive_puffs': 0, 'has_iphone': 0, 'has_samsung': 0,
            'parents_angry': 0, 'police_in_school': 0, 'winston_cigarettes': 0, 'parliament_cigarettes': 0,
            'beer': 0, 'vape_puffs_count': 0, 'knows_uncle': 0, 'juice_strength': 0, 'disposable_vape_defective': 0
        }
        
        for key, value in defaults.items():
            player_dict.setdefault(key, value)
        
        return player_dict
    return None

def create_player(user_id, username):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO players (user_id, username, age, created_at) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, 14, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_player(user_id, **kwargs):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    try:
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        
        cursor.execute(f'UPDATE players SET {set_clause} WHERE user_id = ?', values)
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении игрока: {e}")
    finally:
        conn.close()

async def check_unconscious(user_id):
    """Проверяет, находится ли игрок в бессознательном состоянии"""
    player = get_player(user_id)
    if player and player['unconscious_until']:
        unconscious_until = datetime.fromisoformat(player['unconscious_until'])
        if datetime.now() < unconscious_until:
            time_left = unconscious_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            return True, seconds_left
        else:
            update_player(user_id, unconscious_until=None)
    return False, 0

async def check_parents_angry(user_id):
    """Проверяет, злы ли родители на игрока"""
    player = get_player(user_id)
    if player and player['parents_angry'] and player['parents_angry_until']:
        angry_until = datetime.fromisoformat(player['parents_angry_until'])
        if datetime.now() < angry_until:
            time_left = angry_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            return True, seconds_left
        else:
            update_player(user_id, parents_angry=0, parents_angry_until=None)
    return False, 0

async def check_police_in_school(user_id):
    """Проверяет, есть ли полиция в школе"""
    player = get_player(user_id)
    if player and player['police_in_school'] and player['police_until']:
        police_until = datetime.fromisoformat(player['police_until'])
        if datetime.now() < police_until:
            time_left = police_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            return True, seconds_left
        else:
            update_player(user_id, police_in_school=0, police_until=None)
    return False, 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    if not player:
        create_player(user_id, user.username)
        player = get_player(user_id)
    
    keyboard = [
        ["🏠 Статус", "💼 Работа", "🏠 Домой"],
        ["🛒 Магазин", "🔫 Криминал", "📱 Телефоны"],
        ["🏫 Школа", "🚬 Курить/Вейпить/Снюс"],
        ["🏡 Квартира", "💕 Девушка"],
        ["🎂 Отметить ДР", "📋 Получить паспорт"],
        ["🍻 Ларек", "💨 Кальянная дяди"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
👋 Добро пожаловать в Симулятор Жизни, {user.first_name}!

🎯 Ваши цели:
• Заработать деньги 💰 (работа или криминал)
• Купить квартиру 🏡
• Найти девушку 💕
• Не умереть от голода 🍖

Нажмите "🏠 Статус" чтобы увидеть свое состояние!
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    # Проверка условного срока
    if player['on_probation'] and player['probation_until']:
        probation_until = datetime.fromisoformat(player['probation_until'])
        if datetime.now() < probation_until:
            time_left = probation_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            await update.message.reply_text(f"⏰ Вы на учете! Курить нельзя еще {seconds_left} секунд.")
            return
        else:
            update_player(user_id, on_probation=0, probation_until=None)
    
    food_decrease = random.randint(5, 15)
    new_food = max(0, player['food'] - food_decrease)
    
    if new_food <= 0:
        health_decrease = 10
        new_health = max(0, player['health'] - health_decrease)
        update_player(user_id, food=new_food, health=new_health)
    else:
        update_player(user_id, food=new_food)
    
    player = get_player(user_id)

    # Информация о вейпе
    vape_info = ""
    if player['vape_type']:
        battery_status = "🔋" if player['vape_battery'] > 0 else "🪫"
        vape_info = f"\n🔋 Вейп: {player['vape_type']} ({battery_status} {player['vape_battery']}%)"
        if player['vape_juice'] > 0 and player['juice_flavor']:
            vape_info += f"\n💧 Жижа: {player['juice_flavor']} ({player['vape_juice']}мл, {player['juice_strength']}мг)"
        if player['vape_puffs_count'] > 0:
            vape_info += f"\n📊 Использовано тяг: {player['vape_puffs_count']}/100"
    
    # Информация о сигаретах
    cigarettes_info = ""
    if player['cigarettes'] > 0:
        cigarettes_info += f"\n🚬 Сигареты: {player['cigarettes']} шт."
    if player['winston_cigarettes'] > 0:
        cigarettes_info += f"\n🚬 Winston: {player['winston_cigarettes']} шт."
    if player['parliament_cigarettes'] > 0:
        cigarettes_info += f"\n🚬 Parliament: {player['parliament_cigarettes']} шт."
    if player['chapman_cigarettes'] > 0:
        cigarettes_info += f"\n🍒 Chapman: {player['chapman_cigarettes']} шт."
    
    # Информация об одноразках
    disposable_info = ""
    if player['disposable_vape_type']:
        defective = "🔴 БРАК" if player['disposable_vape_defective'] else "✅"
        disposable_info = f"\n🚬 Одноразка: {player['disposable_vape_type']} ({player['disposable_vape_puffs']} тяг) {defective}"
    
    # Информация об алкоголе
    alcohol_info = ""
    if player['beer'] > 0:
        alcohol_info = f"\n🍻 Пиво: {player['beer']} банок"
    
    # Остальная информация
    iqos_info = ""
    if player['has_iqos']:
        battery_status = "🔋" if player['iqos_battery'] > 0 else "🪫"
        iqos_info = f"\n🔥 Айкос: {battery_status} {player['iqos_battery']}%"
        if player['iqos_sticks'] > 0:
            stick_type = player.get('stick_flavor', 'обычные')
            iqos_info += f"\n📦 Стики: {player['iqos_sticks']} шт. ({stick_type})"
    
    hookah_info = ""
    if player['has_hookah']:
        hookah_info = f"\n💨 Кальян: ✅ Есть"
        if player['hookah_coals'] > 0:
            hookah_info += f"\n🔥 Угли: {player['hookah_coals']} шт."
        if player['hookah_tobacco']:
            hookah_info += f"\n🌿 Табак: {player['hookah_tobacco']} ({player['hookah_tobacco_amount']}г)"
        if player['has_burner']:
            hookah_info += f"\n🔥 Горелка: ✅ Есть"
    
    snus_info = ""
    if player['snus_packs'] > 0:
        flavor = player.get('snus_flavor', 'обычный')
        snus_info = f"\n📦 Снюс: {player['snus_packs']} пачек ({player['snus_strength']} мг, {flavor})"
    
    nicotine_free_snus_info = ""
    if player['has_nicotine_free_snus']:
        nicotine_free_snus_info = f"\n🌿 Безникотиновый снюс: ✅ Есть"
    
    girlfriend_info = ""
    if player['has_girlfriend']:
        girlfriend_info = f"\n💕 Девушка: счастье {player['girlfriend_happiness']}/100"
    
    tech_info = ""
    if player['has_laptop']:
        tech_info += "\n💻 Ноутбук: ✅ Есть"
    if player['has_vpn']:
        tech_info += "\n🛡️ VPN: ✅ Есть"
    if player['has_iphone']:
        tech_info += "\n📱 iPhone 16 Pro Max: ✅ Есть"
    if player['has_samsung']:
        tech_info += "\n📱 Samsung Galaxy: ✅ Есть"
    
    probation_info = ""
    if player['on_probation']:
        probation_info = "\n🚫 НА УЧЕТЕ: Курить нельзя!"
    
    tea_info = ""
    if player['has_tea_leaf']:
        tea_info = "\n🍃 Бумага с чаем: ✅ Есть"
    
    unconscious_info = ""
    if player['unconscious_until']:
        unconscious_until = datetime.fromisoformat(player['unconscious_until'])
        if datetime.now() < unconscious_until:
            time_left = unconscious_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            unconscious_info = f"\n💫 БЕССОЗНАТЕЛЬНЫЙ: {seconds_left} сек."
    
    parents_angry, parents_seconds = await check_parents_angry(user_id)
    parents_info = ""
    if parents_angry:
        parents_info = f"\n👨‍👩‍👦 РОДИТЕЛИ ЗЛЫ: {parents_seconds} сек."
    
    police_in_school, police_seconds = await check_police_in_school(user_id)
    police_info = ""
    if police_in_school:
        police_info = f"\n🚔 ПОЛИЦИЯ В ШКОЛЕ: {police_seconds} сек."
    
    uncle_info = ""
    if player['knows_uncle']:
        uncle_info = "\n👨‍💼 Дядя: ✅ Знакомы"
    
    status_text = f"""
📊 ВАШ СТАТУС:

🎂 Возраст: {player['age']} лет
📋 Паспорт: {'✅ Есть' if player['has_id'] else '❌ Нет'}

💵 Деньги: {player['money']} руб.
❤️ Здоровье: {player['health']}/100
😊 Счастье: {player['happiness']}/100
🍖 Еда: {player['food']}/100

🎓 Образование: {get_education_level_name(player['education_level'])}
💼 Работа: {get_job_level_name(player['job_level'])}
🏡 Квартира: {'✅ Есть' if player['has_apartment'] else '❌ Нет'}
{tech_info}
{uncle_info}

{cigarettes_info}
{alcohol_info}
{vape_info}
{disposable_info}
{iqos_info}
{hookah_info}
{snus_info}
{nicotine_free_snus_info}
{tea_info}
{girlfriend_info}
{probation_info}
{unconscious_info}
{parents_info}
{police_info}

{'⚠️ ВАЖНО: У вас закончилась еда! Здоровье уменьшается!' if player['food'] <= 0 else ''}
{'💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно поешьте!' if player['health'] <= 20 else ''}
{'🔄 Пора менять картридж в вейпе!' if player['vape_puffs_count'] >= 100 else ''}
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
        8: "Работник ПВЗ (3250 руб.)",
        9: "Рабочий (150 руб.)"
    }
    return jobs.get(level, "Неизвестно")

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['job_level'] == 0:
        await update.message.reply_text("💼 Вам нужна работа! Сначала получите работу в разделе 'Магазин' -> 'Устроиться на работу'")
        return
    
    if player['job_level'] == 7 and not player['has_laptop']:
        await update.message.reply_text("❌ Для работы мошенником нужен ноутбук! Купите ноутбук в магазине.")
        return
    
    earnings = [0, 50, 100, 200, 800, 500, 1000, 600, 3250, 150][player['job_level']]
    new_money = player['money'] + earnings
    
    update_player(
        user_id, 
        money=new_money, 
        last_work_time=datetime.now().isoformat(),
        happiness=max(0, player['happiness'] - 5)
    )
    
    await update.message.reply_text(f"💼 Поработали и заработали {earnings} руб.! 💰 Теперь у вас: {new_money} руб.\n\n😔 Счастье немного уменьшилось...")

async def crime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    keyboard = [
        ["💰 Украсть кошелек", "🏪 Ограбить магазин"],
        ["🏠 Ограбить квартиру", "🚗 Угнать машину"],
        ["🕵️‍♂️ Мошенничество", "📱 Украсть телефон"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("🔫 КРИМИНАЛ:", reply_markup=reply_markup)

async def commit_crime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    crime_type = update.message.text
    success_chance = random.random()
    
    if crime_type == "💰 Украсть кошелек":
        money_min, money_max = 50, 200
        arrest_chance = 0.2
        crime_name = "кража кошелька"
        escape_chance = 0.7
        probation_chance = 0.3
    elif crime_type == "🏪 Ограбить магазин":
        money_min, money_max = 200, 500
        arrest_chance = 0.4
        crime_name = "ограбление магазина" 
        escape_chance = 0.5
        probation_chance = 0.5
    elif crime_type == "🏠 Ограбить квартиру":
        money_min, money_max = 500, 1000
        arrest_chance = 0.6
        crime_name = "ограбление квартиры"
        escape_chance = 0.3
        probation_chance = 0.7
    elif crime_type == "🚗 Угнать машину":
        money_min, money_max = 1000, 2000
        arrest_chance = 0.8
        crime_name = "угон машины"
        escape_chance = 0.2
        probation_chance = 0.9
    elif crime_type == "🕵️‍♂️ Мошенничество":
        if not player['has_laptop']:
            await update.message.reply_text("❌ Для мошенничества нужен ноутбук! Купите в магазине.")
            return
        
        money_min, money_max = 600, 1200
        arrest_chance = 0.3 if player['has_vpn'] else 0.6
        crime_name = "мошенничество"
        escape_chance = 0.8 if player['has_vpn'] else 0.4
        probation_chance = 0.4
    elif crime_type == "📱 Украсть телефон":
        money_min, money_max = 800, 1500
        arrest_chance = 0.5
        crime_name = "кража телефона"
        escape_chance = 0.6
        probation_chance = 0.6
        
        # Шанс получить телефон вместо денег
        if random.random() < 0.3:
            phone_type = random.choice(["iphone", "samsung"])
            if phone_type == "iphone":
                update_player(user_id, has_iphone=1)
                await update.message.reply_text(f"✅ Преступление удалось!\n\n📱 Вы украли iPhone 16 Pro Max 512GB!\n💼 Теперь у вас есть крутой телефон!")
                return
            else:
                update_player(user_id, has_samsung=1)
                await update.message.reply_text(f"✅ Преступление удалось!\n\n📱 Вы украли Samsung Galaxy!\n💼 Теперь у вас есть крутой телефон!")
                return
    else:
        return
    
    if success_chance > arrest_chance:
        stolen_money = random.randint(money_min, money_max)
        new_money = player['money'] + stolen_money
        
        update_player(
            user_id,
            money=new_money,
            last_crime_time=datetime.now().isoformat(),
            happiness=min(100, player['happiness'] + 10)
        )
        
        await update.message.reply_text(f"✅ Преступление удалось!\n\n💰 Вы получили: {stolen_money} руб.\n💵 Теперь у вас: {new_money} руб.\n😊 Счастье: +10")
    else:
        if random.random() < escape_chance:
            if random.random() < probation_chance:
                probation_until = datetime.now() + timedelta(seconds=10)
                update_player(
                    user_id,
                    on_probation=1,
                    probation_until=probation_until.isoformat(),
                    happiness=max(0, player['happiness'] - 15)
                )
                await update.message.reply_text(f"🚨 ВАС ПОЧТИ ПОЙМАЛИ!\n\n😰 Счастье: -15\n\n⚠️ Вас поставили на учет! Курить нельзя 10 секунд!")
            else:
                await update.message.reply_text(f"🏃‍♂️ ВАС ПОЧТИ ПОЙМАЛИ!\n\n😰 Счастье: -15")
                update_player(user_id, happiness=max(0, player['happiness'] - 15))
        else:
            await update.message.reply_text(f"🚨🚨🚨 ВАС ПОЙМАЛИ! 🚨🚨🚨\n\nВас посадили в тюрьму...\n\n💀 Все достижения сброшены!")
            # Сброс игрока
            update_player(
                user_id,
                money=0,
                health=100,
                happiness=50,
                education_level=0,
                job_level=0,
                has_apartment=0,
                has_laptop=0,
                has_vpn=0,
                food=100,
                cigarettes=0,
                vape_type=None,
                vape_juice=0,
                juice_flavor=None,
                juice_strength=0,
                snus_packs=0,
                snus_strength=0,
                snus_flavor=None,
                has_girlfriend=0,
                girlfriend_happiness=0,
                has_id=0,
                has_iqos=0,
                iqos_sticks=0,
                iqos_battery=0,
                vape_battery=0,
                has_hookah=0,
                hookah_coals=0,
                hookah_tobacco=None,
                hookah_tobacco_amount=0,
                has_burner=0,
                disposable_vape_type=None,
                disposable_vape_puffs=0,
                disposable_vape_defective=0,
                chapman_cigarettes=0,
                on_probation=0,
                probation_until=None,
                has_tea_leaf=0,
                unconscious_until=None,
                stick_flavor=None,
                has_nicotine_free_snus=0,
                has_iphone=0,
                has_samsung=0,
                parents_angry=0,
                parents_angry_until=None,
                police_in_school=0,
                police_until=None,
                winston_cigarettes=0,
                parliament_cigarettes=0,
                beer=0,
                vape_puffs_count=0,
                knows_uncle=0
            )

async def school_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    # Проверка полиции в школе
    is_police, police_seconds = await check_police_in_school(user_id)
    if is_police:
        await update.message.reply_text(f"🚔 В школе полиция! Подождите {police_seconds} секунд...")
        return
    
    keyboard = [
        ["📚 Учиться", "🚬 Сходить в туалет покурить"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("🏫 ШКОЛА:", reply_markup=reply_markup)

async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['education_level'] >= 4:
        await update.message.reply_text("🎓 Вы уже достигли максимального уровня образования!")
        return
    
    new_education_level = player['education_level'] + 1
    update_player(
        user_id,
        education_level=new_education_level,
        last_school_time=datetime.now().isoformat(),
        happiness=max(0, player['happiness'] - 3)
    )
    
    education_names = {
        1: "11 классов",
        2: "Колледж", 
        3: "Университет",
        4: "Аспирантура"
    }
    
    await update.message.reply_text(f"🎓 Поздравляем! Вы получили: {education_names[new_education_level]}!\n\n😔 Счастье немного уменьшилось от учебы...")

async def school_smoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    # Проверка полиции в школе
    is_police, police_seconds = await check_police_in_school(user_id)
    if is_police:
        await update.message.reply_text(f"🚔 В школе полиция! Курить нельзя! Подождите {police_seconds} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    # Проверка на учет
    if player['on_probation'] and player['probation_until']:
        probation_until = datetime.fromisoformat(player['probation_until'])
        if datetime.now() < probation_until:
            time_left = probation_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            await update.message.reply_text(f"⏰ Вы на учете! Курить нельзя еще {seconds_left} секунд.")
            return
    
    teacher_catch_chance = 0.4
    
    # Шанс что учитель пожалеет если куришь безникотиновую жидкость
    if player['juice_flavor'] and "безникотиновая" in str(player['juice_flavor']).lower():
        teacher_catch_chance = 0.2
        if random.random() < 0.3:
            await update.message.reply_text(f"👨‍🏫 Учитель увидел вас, но пожалел потому что вы курите безникотиновую жидкость!")
            teacher_catch_chance = 0
    
    if random.random() < teacher_catch_chance:
        await update.message.reply_text(f"🚨 ВАС ПОЙМАЛ УЧИТЕЛЬ! 🚨\n\n😰 Счастье: -20\n\nВас поставили на учет! Курить нельзя 10 секунд!")
        
        probation_until = datetime.now() + timedelta(seconds=10)
        update_player(
            user_id,
            on_probation=1,
            probation_until=probation_until.isoformat(),
            happiness=max(0, player['happiness'] - 20)
        )
    else:
        keyboard = [
            ["🚬 Выкурить сигарету", "🍒 Выкурить Чапман"],
            ["🚬 Выкурить Winston", "🚬 Выкурить Parliament"],
            ["💨 Покурить вейп", "🚬 Покурить одноразку"],
            ["🔥 Покурить айкос", "📦 Закинуть снюс"],
            ["🌿 Закинуть безникотиновый снюс", "🍻 Выпить пиво"],
            ["🍃 Покурить бумагу с чаем"],
            ["⬅️ Выйти из туалета"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update_player(user_id, last_smoke_time=datetime.now().isoformat())
        
        await update.message.reply_text("🚬 Вы успешно пробрались в школьный туалет...\n\nВыберите что хотите сделать:", reply_markup=reply_markup)

async def smoke_vape_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    # Проверка на учет
    if player['on_probation'] and player['probation_until']:
        probation_until = datetime.fromisoformat(player['probation_until'])
        if datetime.now() < probation_until:
            time_left = probation_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            await update.message.reply_text(f"⏰ Вы на учете! Курить нельзя еще {seconds_left} секунд.")
            return
    
    keyboard = [
        ["🚬 Выкурить сигарету", "🍒 Выкурить Чапман"],
        ["🚬 Выкурить Winston", "🚬 Выкурить Parliament"],
        ["💨 Покурить вейп", "🚬 Покурить одноразку"],
        ["🔥 Покурить айкос", "📦 Закинуть снюс"],
        ["🌿 Закинуть безникотиновый снюс", "💨 Покурить кальян"],
        ["🍻 Выпить пиво", "🍃 Покурить бумагу с чаем"],
        ["⚡ Перезарядить одноразку", "🔄 Заменить картридж вейпа"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("🚬 Выберите что хотите использовать:", reply_markup=reply_markup)

async def smoke_cigarette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if player['cigarettes'] <= 0:
        await update.message.reply_text("❌ У вас нет сигарет! Купите в магазине.")
        return
    
    new_cigarettes = player['cigarettes'] - 1
    new_health = max(0, player['health'] - 15)
    new_happiness = min(100, player['happiness'] + 20)
    
    update_player(
        user_id,
        cigarettes=new_cigarettes,
        health=new_health,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🚬 Вы выкурили сигарету...\n\n❤️ Здоровье: -15 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness})\n📦 Сигарет осталось: {new_cigarettes}")

async def smoke_chapman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if player['chapman_cigarettes'] <= 0:
        await update.message.reply_text("❌ У вас нет Чапман! Купите в магазине.")
        return
    
    new_chapman = player['chapman_cigarettes'] - 1
    new_health = max(0, player['health'] - 12)
    new_happiness = min(100, player['happiness'] + 25)
    
    update_player(
        user_id,
        chapman_cigarettes=new_chapman,
        health=new_health,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🍒 Вы выкурили Чапман с вишней...\n\n❤️ Здоровье: -12 (теперь {new_health})\n😊 Счастье: +25 (теперь {new_happiness})\n📦 Чапман осталось: {new_chapman}")

async def smoke_winston(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if player['winston_cigarettes'] <= 0:
        await update.message.reply_text("❌ У вас нет Winston! Купите в магазине.")
        return
    
    new_winston = player['winston_cigarettes'] - 1
    new_health = max(0, player['health'] - 14)
    new_happiness = min(100, player['happiness'] + 18)
    
    update_player(
        user_id,
        winston_cigarettes=new_winston,
        health=new_health,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🚬 Вы выкурили Winston...\n\n❤️ Здоровье: -14 (теперь {new_health})\n😊 Счастье: +18 (теперь {new_happiness})\n📦 Winston осталось: {new_winston}")

async def smoke_parliament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if player['parliament_cigarettes'] <= 0:
        await update.message.reply_text("❌ У вас нет Parliament! Купите в магазине.")
        return
    
    new_parliament = player['parliament_cigarettes'] - 1
    new_health = max(0, player['health'] - 13)
    new_happiness = min(100, player['happiness'] + 22)
    
    update_player(
        user_id,
        parliament_cigarettes=new_parliament,
        health=new_health,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🚬 Вы выкурили Parliament с кнопкой...\n\n❤️ Здоровье: -13 (теперь {new_health})\n😊 Счастье: +22 (теперь {new_happiness})\n📦 Parliament осталось: {new_parliament}")

async def vape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
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
    
    # Проверка картриджа
    if player['vape_puffs_count'] >= 100:
        await update.message.reply_text("🔄 Картридж изношен! Замените картридж перед использованием.")
        return
    
    # Эффекты от крепости жидкости
    juice_strength = player['juice_strength']
    unconscious_time = 0
    health_decrease = 8
    additional_effects = ""
    
    if juice_strength >= 70:
        # Сильная жидкость - шанс потери сознания
        if random.random() < 0.3:
            unconscious_time = random.randint(3, 8)
            if juice_strength >= 85:
                unconscious_time = 19  # Анархия Лесные ягоды
            additional_effects = f"\n💫 ОЙ! Слишком крепко! Вы потеряли сознание на {unconscious_time} секунд!"
    
    if juice_strength >= 50:
        # Средняя крепость - головокружение
        if random.random() < 0.4:
            additional_effects += "\n🌀 Закружилась голова..."
    
    if juice_strength >= 55:
        # Сильная крепость - кашель
        if random.random() < 0.5:
            additional_effects += "\n😷 Сильный кашель! Горло болит..."
    
    new_juice = max(0, player['vape_juice'] - 5)
    new_battery = max(0, player['vape_battery'] - 10)
    new_health = max(0, player['health'] - health_decrease)
    new_happiness = min(100, player['happiness'] + 25)
    new_puffs_count = player['vape_puffs_count'] + 1
    
    update_player(
        user_id,
        vape_juice=new_juice,
        vape_battery=new_battery,
        health=new_health,
        happiness=new_happiness,
        vape_puffs_count=new_puffs_count
    )
    
    # Если это крепкая жидкость, добавляем эффект бессознательного состояния
    if unconscious_time > 0:
        unconscious_until = datetime.now() + timedelta(seconds=unconscious_time)
        update_player(user_id, unconscious_until=unconscious_until.isoformat())
    
    message = f"💨 Вы покурили вейп ({player['vape_type']})...\n\n❤️ Здоровье: -{health_decrease} (теперь {new_health})\n😊 Счастье: +25 (теперь {new_happiness})\n💧 Жидкости осталось: {new_juice}мл\n🔋 Батарея вейпа: {new_battery}%\n📊 Использовано тяг: {new_puffs_count}/100{additional_effects}"
    
    await update.message.reply_text(message)

async def replace_vape_cartridge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    player = get_player(user_id)
    
    if not player['vape_type']:
        await update.message.reply_text("❌ У вас нет вейпа!")
        return
    
    if player['vape_puffs_count'] < 100:
        await update.message.reply_text("❌ Картридж еще не изношен! Можно использовать дальше.")
        return
    
    update_player(user_id, vape_puffs_count=0)
    await update.message.reply_text("🔄 Картридж заменен! Теперь можно снова курить.")

async def use_disposable_vape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['disposable_vape_type'] or player['disposable_vape_puffs'] <= 0:
        await update.message.reply_text("❌ У вас нет одноразки! Купите в магазине.")
        return
    
    # Проверка на взрыв одноразки (если бракованная)
    if player['disposable_vape_defective']:
        explosion_chance = 0.2  # 20% шанс взрыва для бракованных
        if random.random() < explosion_chance:
            # Взрыв одноразки
            update_player(
                user_id,
                disposable_vape_type=None,
                disposable_vape_puffs=0,
                disposable_vape_defective=0,
                health=max(0, player['health'] - 30),
                unconscious_until=(datetime.now() + timedelta(seconds=20)).isoformat(),
                police_in_school=1,
                police_until=(datetime.now() + timedelta(seconds=30)).isoformat()
            )
            
            await update.message.reply_text(f"💥💥💥 ОДНОРАЗКА ВЗОРВАЛАСЬ! 💥💥💥\n\n❤️ Здоровье: -30\n💫 Вы без сознания 20 секунд!\n🚔 В школе полиция 30 секунд!\n\nРодители вызвали полицию в школу!")
            return
        
        # Шанс гарьки
        if random.random() < 0.3:
            await update.message.reply_text(f"🤢 Одноразка с гарью! Противно курить...\n😊 Счастье: -5")
            update_player(user_id, happiness=max(0, player['happiness'] - 5))
            return
    
    # Проверка на быстрые затяжки
    now = datetime.now()
    last_puff_time = player.get('last_smoke_puff_time')
    consecutive_puffs = player.get('consecutive_puffs', 0)
    
    if last_puff_time:
        last_puff = datetime.fromisoformat(last_puff_time)
        time_diff = (now - last_puff).total_seconds()
        
        if time_diff <= 3:
            consecutive_puffs += 1
        else:
            consecutive_puffs = 1
    else:
        consecutive_puffs = 1
    
    # Если куришь больше 5 раз за 3 секунды - взрыв
    if consecutive_puffs >= 5:
        # Взрыв одноразки
        update_player(
            user_id,
            disposable_vape_type=None,
            disposable_vape_puffs=0,
            disposable_vape_defective=0,
            health=max(0, player['health'] - 30),
            consecutive_puffs=0,
            unconscious_until=(datetime.now() + timedelta(seconds=20)).isoformat(),
            police_in_school=1,
            police_until=(datetime.now() + timedelta(seconds=30)).isoformat()
        )
        
        await update.message.reply_text(f"💥💥💥 ОДНОРАЗКА ВЗОРВАЛАСЬ ОТ БЫСТРЫХ ЗАТЯЖЕК! 💥💥💥\n\n❤️ Здоровье: -30\n💫 Вы без сознания 20 секунд!\n🚔 В школе полиция 30 секунд!\n\nРодители вызвали полицию в школу!")
        return
    
    new_puffs = player['disposable_vape_puffs'] - 1
    new_health = max(0, player['health'] - 6)
    new_happiness = min(100, player['happiness'] + 20)
    
    # Эффекты от крепости одноразки
    additional_effects = ""
    if "Fillder" in player['disposable_vape_type']:
        # Fillder Redbull 30mg
        if random.random() < 0.3:
            additional_effects = "\n🌀 Закружилась голова..."
    elif "Magnum" in player['disposable_vape_type']:
        # Magnum Глинтвейн 50mg
        if random.random() < 0.4:
            additional_effects = "\n🤢 Подташнивает от крепкости..."
        new_happiness = min(100, new_happiness + 5)  # +5 к счастью за вкус
    
    update_player(
        user_id,
        disposable_vape_puffs=new_puffs,
        health=new_health,
        happiness=new_happiness,
        last_smoke_puff_time=now.isoformat(),
        consecutive_puffs=consecutive_puffs
    )
    
    if new_puffs <= 0:
        update_player(user_id, disposable_vape_type=None, disposable_vape_defective=0)
        await update.message.reply_text(f"🚬 Вы покурили {player['disposable_vape_type']}...\n\n❤️ Здоровье: -6 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness}){additional_effects}\n\n💀 Одноразка закончилась!")
    else:
        await update.message.reply_text(f"🚬 Вы покурили {player['disposable_vape_type']}...\n\n❤️ Здоровье: -6 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness}){additional_effects}\n📦 Тяг осталось: {new_puffs}")

async def recharge_disposable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['disposable_vape_type']:
        await update.message.reply_text("❌ У вас нет одноразки для перезарядки!")
        return
    
    if player['vape_juice'] <= 0:
        await update.message.reply_text("❌ Нет жидкости для перезаправки! Купите жидкость в магазине.")
        return
    
    # Шанс взрыва при перезарядке (особенно для бракованных)
    explosion_chance = 0.3
    if player['disposable_vape_defective']:
        explosion_chance = 0.6  # 60% шанс для бракованных
    
    if random.random() < explosion_chance:
        # Взрыв при перезарядке
        update_player(
            user_id,
            disposable_vape_type=None,
            disposable_vape_puffs=0,
            disposable_vape_defective=0,
            vape_juice=0,
            health=max(0, player['health'] - 40),
            unconscious_until=(datetime.now() + timedelta(seconds=20)).isoformat(),
            police_in_school=1,
            police_until=(datetime.now() + timedelta(seconds=30)).isoformat()
        )
        
        await update.message.reply_text(f"💥💥💥 ОДНОРАЗКА ВЗОРВАЛАСЬ ПРИ ПЕРЕЗАРЯДКЕ! 💥💥💥\n\n❤️ Здоровье: -40\n💫 Вы без сознания 20 секунд!\n🚔 В школе полиция 30 секунд!\n\nРодители вызвали полицию в школу!")
        return
    
    # Успешная перезарядка
    new_juice = max(0, player['vape_juice'] - 20)
    new_puffs = player['disposable_vape_puffs'] + 300
    
    update_player(
        user_id,
        disposable_vape_puffs=new_puffs,
        vape_juice=new_juice
    )
    
    await update.message.reply_text(f"⚡ Вы перезарядили одноразку!\n\n📦 Тяг стало: {new_puffs}\n💧 Жидкости осталось: {new_juice}мл")

async def use_iqos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_iqos']:
        await update.message.reply_text("❌ У вас нет Айкос! Купите в магазине.")
        return
    
    if player['iqos_battery'] <= 0:
        await update.message.reply_text("🪫 Айкос разряжен! Зарядите устройство в магазине.")
        return
    
    if player['iqos_sticks'] <= 0:
        await update.message.reply_text("❌ У вас нет стиков для Айкос! Купите стики в магазине.")
        return
    
    # Проверяем тип стиков
    stick_type = player.get('stick_flavor', 'обычные')
    unconscious_time = 0
    if "малина лед" in str(stick_type).lower():
        unconscious_time = 2
    
    # Используем 1 стик
    new_sticks = player['iqos_sticks'] - 1
    new_battery = max(0, player['iqos_battery'] - 9)
    new_health = max(0, player['health'] - 10)
    new_happiness = min(100, player['happiness'] + 20)
    
    update_player(
        user_id,
        iqos_sticks=new_sticks,
        iqos_battery=new_battery,
        health=new_health,
        happiness=new_happiness
    )
    
    message = f"🔥 Вы покурили Айкос ({stick_type})...\n\n❤️ Здоровье: -10 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness})\n📦 Стиков осталось: {new_sticks} шт.\n🔋 Батарея Айкос: {new_battery}%"
    
    # Если это крепкие стики, добавляем эффект бессознательного состояния
    if unconscious_time > 0:
        unconscious_until = datetime.now() + timedelta(seconds=unconscious_time)
        update_player(user_id, unconscious_until=unconscious_until.isoformat())
        message += f"\n\n💫 ОЙ! Слишком крепко! Вы потеряли сознание на {unconscious_time} секунды!"
    
    await update.message.reply_text(message)

async def use_snus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if player['snus_packs'] <= 0:
        await update.message.reply_text("❌ У вас нет снюса! Купите в магазине.")
        return
    
    new_snus = player['snus_packs'] - 1
    new_health = max(0, player['health'] - 25)
    new_happiness = min(100, player['happiness'] + 30)
    
    # Эффекты от крепости снюса
    additional_effects = ""
    if player['snus_strength'] >= 500 and "Mad" in str(player.get('snus_flavor', '')):
        # Mad Банан Лёд 500mg - шанс потери сознания
        if random.random() < 0.4:
            unconscious_time = random.randint(5, 10)
            unconscious_until = datetime.now() + timedelta(seconds=unconscious_time)
            update_player(user_id, unconscious_until=unconscious_until.isoformat())
            additional_effects = f"\n💫 СЛИШКОМ КРЕПКО! Потеря сознания на {unconscious_time} секунд!"
    
    update_player(
        user_id,
        snus_packs=new_snus,
        health=new_health,
        happiness=new_happiness
    )
    
    flavor = player.get('snus_flavor', 'обычный')
    await update.message.reply_text(f"📦 Вы закинули снюс {flavor} {player['snus_strength']} мг...\n\n❤️ Здоровье: -25 (теперь {new_health})\n😊 Счастье: +30 (теперь {new_happiness})\n📦 Пачек снюса осталось: {new_snus}{additional_effects}")

async def use_nicotine_free_snus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_nicotine_free_snus']:
        await update.message.reply_text("❌ У вас нет безникотинового снюса! Купите в магазине.")
        return
    
    new_happiness = min(100, player['happiness'] + 15)
    
    update_player(
        user_id,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🌿 Вы закинули безникотиновый снюс...\n\n😊 Счастье: +15 (теперь {new_happiness})\n\n✅ Без вреда для здоровья! В школе на ПДН не поставят!")

async def drink_beer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if player['beer'] <= 0:
        await update.message.reply_text("❌ У вас нет пива! Купите в магазине.")
        return
    
    new_beer = player['beer'] - 1
    new_health = max(0, player['health'] - 8)
    new_happiness = min(100, player['happiness'] + 25)
    
    update_player(
        user_id,
        beer=new_beer,
        health=new_health,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🍻 Вы выпили пиво...\n\n❤️ Здоровье: -8 (теперь {new_health})\n😊 Счастье: +25 (теперь {new_happiness})\n📦 Пива осталось: {new_beer} банок")

async def use_hookah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_apartment']:
        await update.message.reply_text("❌ Кальян можно курить только в своей квартире! Купите квартиру сначала.")
        return
    
    if not player['has_hookah']:
        await update.message.reply_text("❌ У вас нет кальяна! Купите в магазине.")
        return
    
    if player['hookah_coals'] <= 0:
        await update.message.reply_text("❌ У вас нет углей для кальяна! Купите в магазине.")
        return
    
    if not player['has_burner']:
        await update.message.reply_text("❌ У вас нет горелки для углей! Купите в магазине.")
        return
    
    if not player['hookah_tobacco'] or player['hookah_tobacco_amount'] <= 0:
        await update.message.reply_text("❌ У вас нет табака для кальяна! Купите в магазине.")
        return
    
    new_coals = player['hookah_coals'] - 1
    new_tobacco = max(0, player['hookah_tobacco_amount'] - 10)
    new_health = max(0, player['health'] - 5)
    new_happiness = min(100, player['happiness'] + 35)
    
    # Эффекты от крепости табака
    additional_effects = ""
    tobacco = player['hookah_tobacco']
    if "DarkSide" in tobacco and "Голубика" in tobacco:
        # DarkSide Голубика Лёд 8/10
        if random.random() < 0.6:
            additional_effects = "\n🌀 Крепкий табак! Легкое головокружение..."
    
    update_player(
        user_id,
        hookah_coals=new_coals,
        hookah_tobacco_amount=new_tobacco,
        health=new_health,
        happiness=new_happiness
    )
    
    # Если табак закончился, очищаем
    if new_tobacco <= 0:
        update_player(user_id, hookah_tobacco=None)
    
    await update.message.reply_text(f"💨 Вы покурили кальян ({player['hookah_tobacco']})...\n\n❤️ Здоровье: -5 (теперь {new_health})\n😊 Счастье: +35 (теперь {new_happiness})\n🔥 Углей осталось: {new_coals} шт.\n🌿 Табака осталось: {new_tobacco}г{additional_effects}")

async def use_tea_leaf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_tea_leaf']:
        await update.message.reply_text("❌ У вас нет бумаги с чаем! Купите в магазине.")
        return
    
    new_health = max(0, player['health'] - 3)
    new_happiness = min(100, player['happiness'] + 10)
    
    update_player(
        user_id,
        health=new_health,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"🍃 Вы покурили бумагу с чаем...\n\n❤️ Здоровье: -3 (теперь {new_health})\n😊 Счастье: +10 (теперь {new_happiness})")

async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    # Проверка злых родителей
    is_angry, angry_seconds = await check_parents_angry(user_id)
    if is_angry:
        await update.message.reply_text(f"👨‍👩‍👦 Родители злы на вас! Подождите {angry_seconds} секунд...")
        return
    
    # Если у игрока есть своя квартира
    if player['has_apartment']:
        keyboard = [
            ["💨 Покурить кальян"],
            ["⬅️ Назад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🏡 ВАША КВАРТИРА\n\nВы в безопасности, можете курить кальян!", reply_markup=reply_markup)
        return
    
    # Если живет с родителями
    keyboard = [
        ["🚬 Покурить вейп дома", "🍃 Покурить бумагу с чаем"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Шанс что родители учуют запах сигарет
    if player['last_smoke_time']:
        last_smoke = datetime.fromisoformat(player['last_smoke_time'])
        time_diff = (datetime.now() - last_smoke).total_seconds()
        
        if time_diff <= 300:  # 5 минут
            smell_chance = 0.7
            if random.random() < smell_chance:
                await update.message.reply_text("👃 МАМА УЧУЯЛА ЗАПАХ СИГАРЕТ! 😠\n\nРодители злы на вас 30 секунд!")
                angry_until = datetime.now() + timedelta(seconds=30)
                update_player(user_id, parents_angry=1, parents_angry_until=angry_until.isoformat())
                return
    
    await update.message.reply_text("🏠 ДОМ\n\nВы дома. Родители в соседней комнате...", reply_markup=reply_markup)

async def smoke_at_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
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
    
    # Шанс что мама зайдет в комнату
    mom_chance = 0.4
    
    if random.random() < mom_chance:
        keyboard = [
            ["🙈 Спрятать вейп"],
            ["💨 Покурить дальше"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("👩 МАМА ЗАХОДИТ В КОМНАТУ! Что делать?", reply_markup=reply_markup)
        return
    
    # Успешное курение
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
    
    await update.message.reply_text(f"💨 Вы покурили вейп дома...\n\n❤️ Здоровье: -8 (теперь {new_health})\n😊 Счастье: +25 (теперь {new_happiness})\n💧 Жидкости осталось: {new_juice}мл\n🔋 Батарея вейпа: {new_battery}%")

async def hide_vape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Шанс что мама учует запах
    smell_chance = 0.3
    
    if random.random() < smell_chance:
        await update.message.reply_text("👃 МАМА УЧУЯЛА ЗАПАХ! 😠\n\nОна забрала ваш вейп и зла на вас 30 секунд!")
        angry_until = datetime.now() + timedelta(seconds=30)
        update_player(
            user_id, 
            parents_angry=1, 
            parents_angry_until=angry_until.isoformat(),
            vape_type=None,
            vape_juice=0,
            vape_battery=0,
            vape_puffs_count=0
        )
    else:
        await update.message.reply_text("🙈 Вы успешно спрятали вейп! Мама ничего не заметила.")

async def apartment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if not player['has_apartment']:
        await update.message.reply_text("❌ У вас нет квартиры! Купите в магазине.")
        return
    
    keyboard = [
        ["💨 Покурить кальян"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("🏡 ВАША КВАРТИРА\n\nВыберите действие:", reply_markup=reply_markup)

async def buy_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_apartment']:
        await update.message.reply_text("🏡 У вас уже есть квартира!")
        return
    
    if player['money'] < 50000:
        await update.message.reply_text(f"❌ Недостаточно денег для покупки квартиры! Нужно 50000 руб., у вас {player['money']} руб.")
        return
    
    new_money = player['money'] - 50000
    update_player(user_id, money=new_money, has_apartment=1)
    
    await update.message.reply_text(f"🏡 Поздравляем! Вы купили квартиру за 50000 руб.! Теперь у вас есть свой дом.\n\n💵 Осталось денег: {new_money} руб.")

async def celebrate_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    new_age = player['age'] + 1
    update_player(user_id, age=new_age, happiness=min(100, player['happiness'] + 10))
    
    await update.message.reply_text(f"🎂 С Днем Рождения! Вам исполнилось {new_age} лет!\n\n😊 Счастье: +10")

async def get_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_id']:
        await update.message.reply_text("📋 У вас уже есть паспорт!")
        return
    
    if player['age'] < 18:
        await update.message.reply_text(f"❌ Для получения паспорта нужно быть старше 18 лет! Сейчас вам {player['age']} лет.")
        return
    
    update_player(user_id, has_id=1)
    await update.message.reply_text("📋 Вы получили паспорт! Теперь вы официально совершеннолетний.")

async def girlfriend_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    keyboard = []
    if not player['has_girlfriend']:
        keyboard.append(["💕 Найти девушку"])
    else:
        keyboard.append(["💑 Свидание", "🎁 Подарок девушке"])
        keyboard.append(["💔 Расстаться"])
    keyboard.append(["⬅️ Назад"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if player['has_girlfriend']:
        message = f"💕 ВАША ДЕВУШКА\n\nСчастье девушки: {player['girlfriend_happiness']}/100\n\nЧто хотите сделать?"
    else:
        message = "💕 РАЗДЕЛ ДЕВУШКИ\n\nУ вас пока нет девушки. Хотите найти?"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def find_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_girlfriend']:
        await update.message.reply_text("💕 У вас уже есть девушка!")
        return
    
    if player['age'] < 16:
        await update.message.reply_text("❌ Слишком молоды для отношений! Подрастите до 16 лет.")
        return
    
    success_chance = 0.3 + (player['happiness'] / 500) + (min(player['money'], 10000) / 100000)
    
    if random.random() < success_chance:
        update_player(user_id, has_girlfriend=1, girlfriend_happiness=50)
        await update.message.reply_text("💕 Поздравляем! Вы нашли девушку!\n\nОна довольна на 50%. Ухаживайте за ней, чтобы она была счастлива!")
    else:
        update_player(user_id, happiness=max(0, player['happiness'] - 5))
        await update.message.reply_text("😔 Вам отказали... Попробуйте еще раз позже.\n\n😊 Счастье: -5")

async def date_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    if player['money'] < 100:
        await update.message.reply_text("❌ Для свидания нужно минимум 100 руб.!")
        return
    
    new_money = player['money'] - 100
    happiness_increase = random.randint(10, 25)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    
    update_player(
        user_id,
        money=new_money,
        girlfriend_happiness=new_girlfriend_happiness,
        happiness=min(100, player['happiness'] + 15),
        last_date_time=datetime.now().isoformat()
    )
    
    await update.message.reply_text(f"💑 Вы сходили на свидание!\n\n💵 Потрачено: 100 руб.\n💕 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness})\n😊 Ваше счастье: +15\n\n💵 Осталось денег: {new_money} руб.")

async def gift_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    if player['money'] < 200:
        await update.message.reply_text("❌ Для подарка нужно минимум 200 руб.!")
        return
    
    new_money = player['money'] - 200
    happiness_increase = random.randint(20, 40)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    
    update_player(
        user_id,
        money=new_money,
        girlfriend_happiness=new_girlfriend_happiness
    )
    
    await update.message.reply_text(f"🎁 Вы подарили подарок девушке!\n\n💵 Потрачено: 200 руб.\n💕 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness})\n\n💵 Осталось денег: {new_money} руб.")

async def break_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    update_player(
        user_id,
        has_girlfriend=0,
        girlfriend_happiness=0,
        happiness=max(0, player['happiness'] - 30)
    )
    
    await update.message.reply_text("💔 Вы расстались с девушкой...\n\n😔 Ваше счастье: -30")

# МАГАЗИНЫ
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    keyboard = [
        [InlineKeyboardButton("🍖 Еда и здоровье", callback_data="food_health_shop")],
        [InlineKeyboardButton("🚬 Сигареты", callback_data="cigarettes_shop")],
        [InlineKeyboardButton("💨 Вейпы и жидкости", callback_data="vapes_shop")],
        [InlineKeyboardButton("🚬 Одноразки", callback_data="disposables_shop")],
        [InlineKeyboardButton("🔥 Айкос", callback_data="iqos_shop")],
        [InlineKeyboardButton("💨 Кальяны", callback_data="hookah_shop")],
        [InlineKeyboardButton("📦 Снюс", callback_data="snus_shop")],
        [InlineKeyboardButton("🛒 Магазин NurikVape", callback_data="nurik_vape_shop")],
        [InlineKeyboardButton("💼 Работа и технологии", callback_data="work_tech_shop")],
        [InlineKeyboardButton("🏡 Недвижимость", callback_data="real_estate_shop")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🛒 МАГАЗИН - Выберите категорию:", reply_markup=reply_markup)

# ЛАРЕК (для несовершеннолетних)
async def larek_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    # Проверка возраста для ларька (только для несовершеннолетних)
    if player['has_id']:
        await update.message.reply_text("❌ Вам уже есть 18! Покупайте в обычных магазинах.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🚬 Fillder❤️ Redbull 30mg (700 руб.)", callback_data="buy_fillder")],
        [InlineKeyboardButton("🚬 Magnum Глинтвейн 50mg (250 руб.)", callback_data="buy_magnum")],
        [InlineKeyboardButton("🍻 Пиво не крепкое (120 руб.)", callback_data="buy_beer_larek")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🍻 ЛАРЕК (для несовершеннолетних)\n\n⚠️ Товары могут быть бракованными!", reply_markup=reply_markup)

# МАГАЗИН NURIKVAPE
async def nurik_vape_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    keyboard = [
        [InlineKeyboardButton("💨 Charin Baby синий (1500 руб.)", callback_data="buy_charin_baby")],
        [InlineKeyboardButton("💨 Boost 2 черный (1800 руб.)", callback_data="buy_boost_2_black")],
        [InlineKeyboardButton("💨 Hero 3 белый (2000 руб.)", callback_data="buy_hero_3_white")],
        [InlineKeyboardButton("💧 Персиковый залив 90mg (450 руб.)", callback_data="buy_peach_flood")],
        [InlineKeyboardButton("💧 Мятный Шок 50mg (400 руб.)", callback_data="buy_mint_shock")],
        [InlineKeyboardButton("💧 Охлаждающие яблоко 40mg (350 руб.)", callback_data="buy_cool_apple")],
        [InlineKeyboardButton("💧 Виноградный повал 55mg (380 руб.)", callback_data="buy_grape_knockout")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🛒 Магазин NurikVape\n\nКачественные вейпы и жидкости!", reply_markup=reply_markup)

# КАЛЬЯННАЯ ДЯДИ
async def uncle_hookah_bar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    # Проверка знакомства с дядей
    if not player['knows_uncle']:
        # Шанс познакомиться с дядей
        if random.random() < 0.5:
            update_player(user_id, knows_uncle=1)
            message = "👨‍💼 ДЯДЯ: Привет, племянник! Заходи в мою кальянную, все бесплатно!\n\n"
        else:
            await update.message.reply_text("❌ Вы еще не знакомы с дядей. Попробуйте зайти позже.")
            return
    else:
        message = "👨‍💼 ДЯДЯ: Снова привет, племянник! Бери что хочешь!\n\n"
    
    # Проверка кулдауна (раз в 30 минут)
    if player['last_uncle_hookah_time']:
        last_visit = datetime.fromisoformat(player['last_uncle_hookah_time'])
        time_diff = (datetime.now() - last_visit).total_seconds()
        if time_diff < 1800:  # 30 минут
            seconds_left = 1800 - int(time_diff)
            await update.message.reply_text(f"👨‍💼 ДЯДЯ: Ты только что был! Приходи через {seconds_left} секунд.")
            return
    
    keyboard = [
        [InlineKeyboardButton("💨 Покурить кальян Малина и лёд", callback_data="uncle_raspberry_ice")],
        [InlineKeyboardButton("💨 Покурить кальян Лесные ягоды и лёд", callback_data="uncle_forest_berries")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message + "Выберите табак для кальяна:", reply_markup=reply_markup)

async def smoke_uncle_hookah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await query.edit_message_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['knows_uncle']:
        await query.edit_message_text("❌ Вы не знакомы с дядей!")
        return
    
    tobacco_type = query.data
    health_decrease = 3
    happiness_increase = 40
    
    if tobacco_type == "uncle_raspberry_ice":
        tobacco_name = "Малина и лёд"
        # Крепкость 4/10 - минимальные эффекты
    else:  # uncle_forest_berries
        tobacco_name = "Лесные ягоды и лёд" 
        # Крепкость 8/10 - возможны эффекты
        if random.random() < 0.3:
            health_decrease = 5
            happiness_increase = 50
    
    new_health = max(0, player['health'] - health_decrease)
    new_happiness = min(100, player['happiness'] + happiness_increase)
    
    update_player(
        user_id,
        health=new_health,
        happiness=new_happiness,
        last_uncle_hookah_time=datetime.now().isoformat()
    )
    
    message = f"💨 Вы покурили кальян у дяди ({tobacco_name})...\n\n❤️ Здоровье: -{health_decrease} (теперь {new_health})\n😊 Счастье: +{happiness_increase} (теперь {new_happiness})\n\n👨‍💼 ДЯДЯ: Заходи еще, племянник!"
    
    await query.edit_message_text(message)

# КАТЕГОРИИ МАГАЗИНА
async def food_health_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🍖 Еда (50 руб.)", callback_data="buy_food")],
        [InlineKeyboardButton("❤️ Лечение (100 руб.)", callback_data="buy_health")],
        [InlineKeyboardButton("😊 Развлечения (80 руб.)", callback_data="buy_happiness")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🍖 ЕДА И ЗДОРОВЬЕ:", reply_markup=reply_markup)

async def cigarettes_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🚬 Сигареты (30 руб.)", callback_data="buy_cigarettes")],
        [InlineKeyboardButton("🍒 Chapman с вишней (200 руб.)", callback_data="buy_chapman")],
        [InlineKeyboardButton("🚬 Winston (75 руб.)", callback_data="buy_winston")],
        [InlineKeyboardButton("🚬 Parliament с кнопкой (60 руб.)", callback_data="buy_parliament")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🚬 СИГАРЕТЫ:", reply_markup=reply_markup)

async def vapes_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    player = get_player(user_id)
    
    # Проверка возраста для вейпов
    age_check_message = ""
    if not player['has_id'] and player['age'] < 18:
        if player['age'] >= 16:
            age_check_message = "\n\n⚠️ Вам 16-17 лет: 30% шанс что продадут"
        elif player['age'] >= 14:
            age_check_message = "\n\n⚠️ Вам 14-15 лет: 15% шанс что продадут"
        else:
            age_check_message = "\n\n❌ Вам меньше 14 лет: не продадут"
    
    keyboard = [
        [InlineKeyboardButton("💨 Pasito 2 (1200 руб.)", callback_data="buy_pasito_2")],
        [InlineKeyboardButton("💨 Knight (1400 руб.)", callback_data="buy_knight")],
        [InlineKeyboardButton("💨 Minican (1100 руб.)", callback_data="buy_minican")],
        [InlineKeyboardButton("💨 Xros (1300 руб.)", callback_data="buy_xros")],
        [InlineKeyboardButton("💨 Minifit (1000 руб.)", callback_data="buy_minifit")],
        [InlineKeyboardButton("💨 Boost 2 (1500 руб.)", callback_data="buy_boost_2")],
        [InlineKeyboardButton("💨 Hero 3 Pink (1600 руб.)", callback_data="buy_hero_3_pink")],
        [InlineKeyboardButton("💨 Boost 3 (1700 руб.)", callback_data="buy_boost_3")],
        [InlineKeyboardButton("💧 Жидкости", callback_data="vape_juices_shop")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"💨 ВЕЙПЫ И УСТРОЙСТВА:{age_check_message}", reply_markup=reply_markup)

async def vape_juices_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💧 Mad без никотина (150 руб.)", callback_data="buy_mad_nicotine_free")],
        [InlineKeyboardButton("💧 Анархия Виноград лед 🍇 70mg (300 руб.)", callback_data="buy_anarchy_grape_ice")],
        [InlineKeyboardButton("💧 Skala Банан Лёд🍌 30mg (250 руб.)", callback_data="buy_skala_banana_ice")],
        [InlineKeyboardButton("💧 Анархия Лесные ягоды 🍇 85mg (320 руб.)", callback_data="buy_anarchy_forest_berries")],
        [InlineKeyboardButton("⬅️ Назад к вейпам", callback_data="vapes_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💧 ЖИДКОСТИ ДЛЯ ВЕЙПОВ:", reply_markup=reply_markup)

async def disposables_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🚬 Fillder❤️ Redbull 30mg (700 руб.)", callback_data="buy_fillder_shop")],
        [InlineKeyboardButton("🚬 Magnum Глинтвейн🍷 50mg (250 руб.)", callback_data="buy_magnum_shop")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🚬 ОДНОРАЗКИ:", reply_markup=reply_markup)

async def iqos_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔥 Айкос устройство (1500 руб.)", callback_data="buy_iqos_device")],
        [InlineKeyboardButton("📦 Обычные стики (100 руб.)", callback_data="buy_iqos_sticks")],
        [InlineKeyboardButton("🧊 Стики Малина Лёд (300 руб.)", callback_data="buy_iqos_raspberry_ice")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🔥 АЙКОС И СИСТЕМЫ:", reply_markup=reply_markup)

async def hookah_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💨 Кальян (2000 руб.)", callback_data="buy_hookah")],
        [InlineKeyboardButton("🔥 Угли (100 руб.)", callback_data="buy_coals")],
        [InlineKeyboardButton("🔥 Горелка (300 руб.)", callback_data="buy_burner")],
        [InlineKeyboardButton("🌿 DarkSide Голубика Лёд🫐 (500 руб.)", callback_data="buy_darkside_blueberry")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💨 КАЛЬЯНЫ И ТАБАК:", reply_markup=reply_markup)

async def snus_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📦 Mad Банан Лёд🍌 500mg (200 руб.)", callback_data="buy_mad_banana_ice")],
        [InlineKeyboardButton("🌿 Безникотиновый снюс (100 руб.)", callback_data="buy_nicotine_free_snus")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("📦 СНЮС:", reply_markup=reply_markup)

async def work_tech_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💼 Устроиться на работу (200 руб.)", callback_data="buy_job")],
        [InlineKeyboardButton("💻 Ноутбук (5000 руб.)", callback_data="buy_laptop")],
        [InlineKeyboardButton("🛡️ VPN (200 руб.)", callback_data="buy_vpn")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💼 РАБОТА И ТЕХНОЛОГИИ:", reply_markup=reply_markup)

async def real_estate_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏡 Купить квартиру (50000 руб.)", callback_data="buy_apartment_shop")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🏡 НЕДВИЖИМОСТЬ:", reply_markup=reply_markup)

# ОБРАБОТЧИК ПОКУПОК
async def handle_shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await query.edit_message_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player:
        await query.edit_message_text("Сначала запустите бота командой /start")
        return
    
    # Обработка навигации
    if query.data == "back_to_shop":
        await shop(update, context)
        return
    elif query.data == "back_to_main":
        await start(update, context)
        return
    
    # Обработка категорий магазина
    category_handlers = {
        "food_health_shop": food_health_shop,
        "cigarettes_shop": cigarettes_shop,
        "vapes_shop": vapes_shop,
        "vape_juices_shop": vape_juices_shop,
        "disposables_shop": disposables_shop,
        "iqos_shop": iqos_shop,
        "hookah_shop": hookah_shop,
        "snus_shop": snus_shop,
        "nurik_vape_shop": nurik_vape_shop,
        "work_tech_shop": work_tech_shop,
        "real_estate_shop": real_estate_shop
    }
    
    if query.data in category_handlers:
        await category_handlers[query.data](update, context)
        return
    
    # Обработка покупок товаров
    item_data = {
        # Еда и здоровье
        "buy_food": {"price": 50, "type": "food"},
        "buy_health": {"price": 100, "type": "health"},
        "buy_happiness": {"price": 80, "type": "happiness"},
        
        # Сигареты
        "buy_cigarettes": {"price": 30, "type": "cigarettes"},
        "buy_chapman": {"price": 200, "type": "chapman"},
        "buy_winston": {"price": 75, "type": "winston"},
        "buy_parliament": {"price": 60, "type": "parliament"},
        
        # Вейпы
        "buy_pasito_2": {"price": 1200, "type": "vape_device", "device": "Pasito 2"},
        "buy_knight": {"price": 1400, "type": "vape_device", "device": "Knight"},
        "buy_minican": {"price": 1100, "type": "vape_device", "device": "Minican"},
        "buy_xros": {"price": 1300, "type": "vape_device", "device": "Xros"},
        "buy_minifit": {"price": 1000, "type": "vape_device", "device": "Minifit"},
        "buy_boost_2": {"price": 1500, "type": "vape_device", "device": "Boost 2"},
        "buy_hero_3_pink": {"price": 1600, "type": "vape_device", "device": "Hero 3 Pink"},
        "buy_boost_3": {"price": 1700, "type": "vape_device", "device": "Boost 3"},
        
        # Жидкости для вейпов
        "buy_mad_nicotine_free": {"price": 150, "type": "vape_juice", "flavor": "Mad без никотина", "strength": 0},
        "buy_anarchy_grape_ice": {"price": 300, "type": "vape_juice", "flavor": "Анархия Виноград лед 🍇", "strength": 70},
        "buy_skala_banana_ice": {"price": 250, "type": "vape_juice", "flavor": "Skala Банан Лёд🍌", "strength": 30},
        "buy_anarchy_forest_berries": {"price": 320, "type": "vape_juice", "flavor": "Анархия Лесные ягоды 🍇", "strength": 85},
        
        # Одноразки
        "buy_fillder_shop": {"price": 700, "type": "fillder"},
        "buy_magnum_shop": {"price": 250, "type": "magnum"},
        
        # Ларек
        "buy_fillder": {"price": 700, "type": "fillder_defective"},
        "buy_magnum": {"price": 250, "type": "magnum_defective"},
        "buy_beer_larek": {"price": 120, "type": "beer"},
        
        # Айкос
        "buy_iqos_device": {"price": 1500, "type": "iqos_device"},
        "buy_iqos_sticks": {"price": 100, "type": "iqos_sticks"},
        "buy_iqos_raspberry_ice": {"price": 300, "type": "iqos_raspberry_ice"},
        
        # Кальяны
        "buy_hookah": {"price": 2000, "type": "hookah"},
        "buy_coals": {"price": 100, "type": "coals"},
        "buy_burner": {"price": 300, "type": "burner"},
        "buy_darkside_blueberry": {"price": 500, "type": "darkside_blueberry"},
        
        # Снюс
        "buy_mad_banana_ice": {"price": 200, "type": "mad_banana_ice"},
        "buy_nicotine_free_snus": {"price": 100, "type": "nicotine_free_snus"},
        
        # Магазин NurikVape
        "buy_charin_baby": {"price": 1500, "type": "vape_device", "device": "Charin Baby синий"},
        "buy_boost_2_black": {"price": 1800, "type": "vape_device", "device": "Boost 2 черный"},
        "buy_hero_3_white": {"price": 2000, "type": "vape_device", "device": "Hero 3 белый"},
        "buy_peach_flood": {"price": 450, "type": "vape_juice", "flavor": "Персиковый залив 🌊", "strength": 90},
        "buy_mint_shock": {"price": 400, "type": "vape_juice", "flavor": "Мятный Шок ❄️", "strength": 50},
        "buy_cool_apple": {"price": 350, "type": "vape_juice", "flavor": "Охлаждающие яблоко🧊", "strength": 40},
        "buy_grape_knockout": {"price": 380, "type": "vape_juice", "flavor": "Виноградный повал", "strength": 55},
        
        # Работа и технологии
        "buy_job": {"price": 200, "type": "job"},
        "buy_laptop": {"price": 5000, "type": "laptop"},
        "buy_vpn": {"price": 200, "type": "vpn"},
        
        # Недвижимость
        "buy_apartment_shop": {"price": 50000, "type": "apartment"},
        
        # Кальянная дяди
        "uncle_raspberry_ice": {"price": 0, "type": "uncle_hookah", "tobacco": "Малина и лёд"},
        "uncle_forest_berries": {"price": 0, "type": "uncle_hookah", "tobacco": "Лесные ягоды и лёд"}
    }
    
    if query.data not in item_data:
        await query.edit_message_text("Неизвестный товар!")
        return
    
    item_info = item_data[query.data]
    price = item_info["price"]
    item_type = item_info["type"]
    
    # Проверка возраста для вейпов
    if item_type.startswith("vape_device") and not player['has_id']:
        if player['age'] < 14:
            await query.edit_message_text("❌ Вам меньше 14 лет! Вейпы не продаются.")
            return
        elif player['age'] < 16:
            if random.random() > 0.15:  # 15% шанс для 14-15 лет
                await query.edit_message_text("❌ Продавец: Тебе еще рано вейпы покупать! Приходи с паспортом.")
                return
        elif player['age'] < 18:
            if random.random() > 0.3:  # 30% шанс для 16-17 лет
                await query.edit_message_text("❌ Продавец: Покажи паспорт! Без паспорта не продам.")
                return
    
    if player['money'] < price:
        await query.edit_message_text(f"❌ Недостаточно денег! Нужно {price} руб., у вас {player['money']} руб.")
        return
    
    new_money = player['money'] - price
    message = f"✅ Покупка успешна!\n💰 Потрачено: {price} руб.\n💵 Осталось: {new_money} руб.\n\n"
    
    # Обработка разных типов товаров
    if item_type == "food":
        update_player(user_id, money=new_money, food=min(100, player['food'] + 30))
        message += "🍖 +30 к еде"
    elif item_type == "health":
        update_player(user_id, money=new_money, health=min(100, player['health'] + 30))
        message += "❤️ +30 к здоровью"
    elif item_type == "happiness":
        update_player(user_id, money=new_money, happiness=min(100, player['happiness'] + 20))
        message += "😊 +20 к счастью"
    elif item_type == "cigarettes":
        update_player(user_id, money=new_money, cigarettes=player['cigarettes'] + 20)
        message += "🚬 +20 сигарет"
    elif item_type == "chapman":
        update_player(user_id, money=new_money, chapman_cigarettes=player['chapman_cigarettes'] + 10)
        message += "🍒 +10 Chapman с вишней"
    elif item_type == "winston":
        update_player(user_id, money=new_money, winston_cigarettes=player['winston_cigarettes'] + 20)
        message += "🚬 +20 Winston"
    elif item_type == "parliament":
        update_player(user_id, money=new_money, parliament_cigarettes=player['parliament_cigarettes'] + 20)
        message += "🚬 +20 Parliament с кнопкой"
    elif item_type == "vape_device":
        device_name = item_info["device"]
        update_player(user_id, money=new_money, vape_type=device_name, vape_battery=100, vape_puffs_count=0)
        message += f"💨 {device_name} приобретен! Батарея: 100%"
    elif item_type == "vape_juice":
        flavor = item_info["flavor"]
        strength = item_info["strength"]
        update_player(user_id, money=new_money, vape_juice=player['vape_juice'] + 30, juice_flavor=flavor, juice_strength=strength)
        message += f"💧 +30мл жидкости: {flavor} ({strength}мг)"
    elif item_type in ["fillder", "fillder_defective"]:
        defective = 1 if item_type == "fillder_defective" else 0
        update_player(user_id, money=new_money, disposable_vape_type="Fillder❤️ Redbull", disposable_vape_puffs=1000, disposable_vape_defective=defective)
        message += "🚬 Fillder❤️ Redbull 30mg (1000 тяг)"
        if defective:
            message += "\n⚠️ Внимание: Одноразка может быть бракованной!"
    elif item_type in ["magnum", "magnum_defective"]:
        defective = 1 if item_type == "magnum_defective" else 0
        update_player(user_id, money=new_money, disposable_vape_type="Magnum Глинтвейн🍷", disposable_vape_puffs=400, disposable_vape_defective=defective)
        message += "🚬 Magnum Глинтвейн🍷 50mg (400 тяг)"
        if defective:
            message += "\n⚠️ Внимание: Одноразка может быть бракованной!"
    elif item_type == "beer":
        update_player(user_id, money=new_money, beer=player['beer'] + 5)
        message += "🍻 +5 банок пива"
    elif item_type == "iqos_device":
        update_player(user_id, money=new_money, has_iqos=1, iqos_battery=100)
        message += "🔥 Айкос устройство приобретено! Батарея: 100%"
    elif item_type == "iqos_sticks":
        update_player(user_id, money=new_money, iqos_sticks=player['iqos_sticks'] + 10)
        message += "📦 +10 обычных стиков для Айкос"
    elif item_type == "iqos_raspberry_ice":
        update_player(user_id, money=new_money, iqos_sticks=player['iqos_sticks'] + 10, stick_flavor="Малина Лёд 🧊")
        message += "🧊 +10 стиков Малина Лёд для Айкос"
    elif item_type == "hookah":
        update_player(user_id, money=new_money, has_hookah=1)
        message += "💨 Кальян приобретен!"
    elif item_type == "coals":
        update_player(user_id, money=new_money, hookah_coals=player['hookah_coals'] + 5)
        message += "🔥 +5 углей для кальяна"
    elif item_type == "burner":
        update_player(user_id, money=new_money, has_burner=1)
        message += "🔥 Горелка приобретена!"
    elif item_type == "darkside_blueberry":
        update_player(user_id, money=new_money, hookah_tobacco="DarkSide Голубика Лёд🫐", hookah_tobacco_amount=player['hookah_tobacco_amount'] + 50)
        message += "🌿 DarkSide Голубика Лёд🫐 50г (крепкость 8/10)"
    elif item_type == "mad_banana_ice":
        update_player(user_id, money=new_money, snus_packs=player['snus_packs'] + 1, snus_strength=500, snus_flavor="Mad Банан Лёд🍌")
        message += "📦 Mad Банан Лёд🍌 500mg (осторожно: может вызвать потерю сознания!)"
    elif item_type == "nicotine_free_snus":
        update_player(user_id, money=new_money, has_nicotine_free_snus=1)
        message += "🌿 Безникотиновый снюс приобретен!"
    elif item_type == "job":
        if player['education_level'] > player['job_level']:
            new_job_level = player['job_level'] + 1
            update_player(user_id, money=new_money, job_level=new_job_level)
            message += f"💼 Новая работа: {get_job_level_name(new_job_level)}"
        else:
            message = "❌ Для новой работы нужно больше образования!"
            new_money = player['money']
    elif item_type == "laptop":
        update_player(user_id, money=new_money, has_laptop=1)
        message += "💻 Ноутбук приобретен!"
    elif item_type == "vpn":
        update_player(user_id, money=new_money, has_vpn=1)
        message += "🛡️ VPN активирован!"
    elif item_type == "apartment":
        if not player['has_apartment']:
            update_player(user_id, money=new_money, has_apartment=1)
            message += "🏡 Квартира приобретена!"
        else:
            message = "❌ У вас уже есть квартира!"
            new_money = player['money']
    elif item_type == "uncle_hookah":
        # Бесплатно в кальянной дяди
        tobacco = item_info["tobacco"]
        health_decrease = 3
        happiness_increase = 40
        
        if tobacco == "Лесные ягоды и лёд":
            health_decrease = 5
            happiness_increase = 50
        
        new_health = max(0, player['health'] - health_decrease)
        new_happiness = min(100, player['happiness'] + happiness_increase)
        
        update_player(
            user_id,
            health=new_health,
            happiness=new_happiness,
            last_uncle_hookah_time=datetime.now().isoformat()
        )
        
        message = f"💨 Вы покурили кальян у дяди ({tobacco})...\n\n❤️ Здоровье: -{health_decrease} (теперь {new_health})\n😊 Счастье: +{happiness_increase} (теперь {new_happiness})\n\n👨‍💼 ДЯДЯ: Бесплатно для племянника!"
    
    await query.edit_message_text(message)

# ОБРАБОТЧИК СООБЩЕНИЙ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    text = update.message.text
    
    if text == "🏠 Статус":
        await show_status(update, context)
    elif text == "💼 Работа":
        await work(update, context)
    elif text == "🏠 Домой":
        await go_home(update, context)
    elif text == "🔫 Криминал":
        await crime_menu(update, context)
    elif text in ["💰 Украсть кошелек", "🏪 Ограбить магазин", "🏠 Ограбить квартиру", "🚗 Угнать машину", "🕵️‍♂️ Мошенничество", "📱 Украсть телефон"]:
        await commit_crime(update, context)
    elif text == "🛒 Магазин":
        await shop(update, context)
    elif text == "🍻 Ларек":
        await larek_shop(update, context)
    elif text == "💨 Кальянная дяди":
        await uncle_hookah_bar(update, context)
    elif text == "🏫 Школа":
        await school_menu(update, context)
    elif text == "📚 Учиться":
        await study(update, context)
    elif text == "🚬 Сходить в туалет покурить":
        await school_smoke(update, context)
    elif text == "🏡 Квартира":
        await apartment_menu(update, context)
    elif text == "🚬 Курить/Вейпить/Снюс":
        await smoke_vape_menu(update, context)
    elif text == "🚬 Выкурить сигарету":
        await smoke_cigarette(update, context)
    elif text == "🍒 Выкурить Чапман":
        await smoke_chapman(update, context)
    elif text == "🚬 Выкурить Winston":
        await smoke_winston(update, context)
    elif text == "🚬 Выкурить Parliament":
        await smoke_parliament(update, context)
    elif text == "💨 Покурить вейп":
        await vape(update, context)
    elif text == "🚬 Покурить одноразку":
        await use_disposable_vape(update, context)
    elif text == "🔥 Покурить айкос":
        await use_iqos(update, context)
    elif text == "📦 Закинуть снюс":
        await use_snus(update, context)
    elif text == "🌿 Закинуть безникотиновый снюс":
        await use_nicotine_free_snus(update, context)
    elif text == "🍻 Выпить пиво":
        await drink_beer(update, context)
    elif text == "💨 Покурить кальян":
        await use_hookah(update, context)
    elif text == "🍃 Покурить бумагу с чаем":
        await use_tea_leaf(update, context)
    elif text == "⚡ Перезарядить одноразку":
        await recharge_disposable(update, context)
    elif text == "🔄 Заменить картридж вейпа":
        await replace_vape_cartridge(update, context)
    elif text == "🚬 Покурить вейп дома":
        await smoke_at_home(update, context)
    elif text == "🙈 Спрятать вейп":
        await hide_vape(update, context)
    elif text == "💨 Покурить дальше":
        await vape(update, context)
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

def main():
    # Инициализация базы данных
    init_db()
    upgrade_db()
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern=".*"))
    
    print("Бот запущен...")
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()