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
            disposable_vape_defective INTEGER DEFAULT 0,
            has_car INTEGER DEFAULT 0,
            car_type TEXT DEFAULT NULL,
            has_dog INTEGER DEFAULT 0,
            dog_happiness INTEGER DEFAULT 0,
            last_walk_time TEXT,
            crypto_money INTEGER DEFAULT 0,
            has_crypto_wallet INTEGER DEFAULT 0,
            gym_level INTEGER DEFAULT 0,
            last_gym_time TEXT,
            reputation INTEGER DEFAULT 0,
            completed_quests INTEGER DEFAULT 0
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
            'disposable_vape_defective': 'ALTER TABLE players ADD COLUMN disposable_vape_defective INTEGER DEFAULT 0',
            'has_car': 'ALTER TABLE players ADD COLUMN has_car INTEGER DEFAULT 0',
            'car_type': 'ALTER TABLE players ADD COLUMN car_type TEXT DEFAULT NULL',
            'has_dog': 'ALTER TABLE players ADD COLUMN has_dog INTEGER DEFAULT 0',
            'dog_happiness': 'ALTER TABLE players ADD COLUMN dog_happiness INTEGER DEFAULT 0',
            'last_walk_time': 'ALTER TABLE players ADD COLUMN last_walk_time TEXT',
            'crypto_money': 'ALTER TABLE players ADD COLUMN crypto_money INTEGER DEFAULT 0',
            'has_crypto_wallet': 'ALTER TABLE players ADD COLUMN has_crypto_wallet INTEGER DEFAULT 0',
            'gym_level': 'ALTER TABLE players ADD COLUMN gym_level INTEGER DEFAULT 0',
            'last_gym_time': 'ALTER TABLE players ADD COLUMN last_gym_time TEXT',
            'reputation': 'ALTER TABLE players ADD COLUMN reputation INTEGER DEFAULT 0',
            'completed_quests': 'ALTER TABLE players ADD COLUMN completed_quests INTEGER DEFAULT 0'
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
                  'winston_cigarettes', 'parliament_cigarettes', 'beer', 'vape_puffs_count', 'last_uncle_hookah_time', 'knows_uncle', 'disposable_vape_defective',
                  'has_car', 'car_type', 'has_dog', 'dog_happiness', 'last_walk_time', 'crypto_money', 'has_crypto_wallet',
                  'gym_level', 'last_gym_time', 'reputation', 'completed_quests']
        
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
            'beer': 0, 'vape_puffs_count': 0, 'knows_uncle': 0, 'juice_strength': 0, 'disposable_vape_defective': 0,
            'has_car': 0, 'has_dog': 0, 'dog_happiness': 0, 'crypto_money': 0, 'has_crypto_wallet': 0,
            'gym_level': 0, 'reputation': 0, 'completed_quests': 0
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

# СИСТЕМА ПРОВЕРОК
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

async def check_probation(user_id):
    """Проверяет, находится ли игрок на учете"""
    player = get_player(user_id)
    if player and player['on_probation'] and player['probation_until']:
        probation_until = datetime.fromisoformat(player['probation_until'])
        if datetime.now() < probation_until:
            time_left = probation_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            return True, seconds_left
        else:
            update_player(user_id, on_probation=0, probation_until=None)
    return False, 0

# ОСНОВНЫЕ КОМАНДЫ
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
        ["🍻 Ларек", "💨 Кальянная дяди"],
        ["🚗 Транспорт", "🐶 Питомец"],
        ["💰 Крипта", "💪 Спортзал"],
        ["🎯 Квесты", "⭐ Репутация"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
👋 Добро пожаловать в Симулятор Жизни, {user.first_name}!

🎯 Ваши цели:
• Заработать деньги 💰 (работа или криминал)
• Купить квартиру 🏡
• Найти девушку 💕
• Не умереть от голода 🍖
• Прокачать персонажа 🎯

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
    is_probation, probation_seconds = await check_probation(user_id)
    if is_probation:
        await update.message.reply_text(f"⏰ Вы на учете! Курить нельзя еще {probation_seconds} секунд.")
        return
    
    # Уменьшение еды со временем
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
    
    # Информация об айкос
    iqos_info = ""
    if player['has_iqos']:
        battery_status = "🔋" if player['iqos_battery'] > 0 else "🪫"
        iqos_info = f"\n🔥 Айкос: {battery_status} {player['iqos_battery']}%"
        if player['iqos_sticks'] > 0:
            stick_type = player.get('stick_flavor', 'обычные')
            iqos_info += f"\n📦 Стики: {player['iqos_sticks']} шт. ({stick_type})"
    
    # Информация о кальяне
    hookah_info = ""
    if player['has_hookah']:
        hookah_info = f"\n💨 Кальян: ✅ Есть"
        if player['hookah_coals'] > 0:
            hookah_info += f"\n🔥 Угли: {player['hookah_coals']} шт."
        if player['hookah_tobacco']:
            hookah_info += f"\n🌿 Табак: {player['hookah_tobacco']} ({player['hookah_tobacco_amount']}г)"
        if player['has_burner']:
            hookah_info += f"\n🔥 Горелка: ✅ Есть"
    
    # Информация о снюсе
    snus_info = ""
    if player['snus_packs'] > 0:
        flavor = player.get('snus_flavor', 'обычный')
        snus_info = f"\n📦 Снюс: {player['snus_packs']} пачек ({player['snus_strength']} мг, {flavor})"
    
    nicotine_free_snus_info = ""
    if player['has_nicotine_free_snus']:
        nicotine_free_snus_info = f"\n🌿 Безникотиновый снюс: ✅ Есть"
    
    # Информация о девушке
    girlfriend_info = ""
    if player['has_girlfriend']:
        girlfriend_info = f"\n💕 Девушка: счастье {player['girlfriend_happiness']}/100"
    
    # Технологии
    tech_info = ""
    if player['has_laptop']:
        tech_info += "\n💻 Ноутбук: ✅ Есть"
    if player['has_vpn']:
        tech_info += "\n🛡️ VPN: ✅ Есть"
    if player['has_iphone']:
        tech_info += "\n📱 iPhone 16 Pro Max: ✅ Есть"
    if player['has_samsung']:
        tech_info += "\n📱 Samsung Galaxy: ✅ Есть"
    
    # НОВЫЕ ФУНКЦИИ
    car_info = ""
    if player['has_car']:
        car_info = f"\n🚗 Машина: {player['car_type']}"
    
    dog_info = ""
    if player['has_dog']:
        dog_info = f"\n🐶 Собака: счастье {player['dog_happiness']}/100"
    
    crypto_info = ""
    if player['has_crypto_wallet']:
        crypto_info = f"\n💰 Крипто-кошелек: {player['crypto_money']} USD"
    
    gym_info = ""
    if player['gym_level'] > 0:
        gym_info = f"\n💪 Уровень спортзала: {player['gym_level']}"
    
    reputation_info = ""
    if player['reputation'] > 0:
        reputation_info = f"\n⭐ Репутация: {player['reputation']}"
    
    quests_info = ""
    if player['completed_quests'] > 0:
        quests_info = f"\n🎯 Выполнено квестов: {player['completed_quests']}"
    
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

{car_info}
{dog_info}
{crypto_info}
{gym_info}
{reputation_info}
{quests_info}

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
{'🐶 Собака хочет гулять!' if player['has_dog'] and player['dog_happiness'] < 30 else ''}
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

# РАБОТА
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

# КРИМИНАЛ
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
        ["💻 Взлом банка", "🔐 Крипто-кража"],
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
    elif crime_type == "💻 Взлом банка":
        if not player['has_laptop'] or not player['has_vpn']:
            await update.message.reply_text("❌ Для взлома банка нужен ноутбук и VPN!")
            return
        
        money_min, money_max = 5000, 10000
        arrest_chance = 0.7
        crime_name = "взлом банка"
        escape_chance = 0.4
        probation_chance = 0.8
    elif crime_type == "🔐 Крипто-кража":
        if not player['has_crypto_wallet']:
            await update.message.reply_text("❌ Для крипто-кражи нужен крипто-кошелек!")
            return
        
        crypto_min, crypto_max = 100, 500
        arrest_chance = 0.6
        crime_name = "крипто-кража"
        escape_chance = 0.5
        probation_chance = 0.6
    else:
        return
    
    if success_chance > arrest_chance:
        if crime_type == "🔐 Крипто-кража":
            stolen_crypto = random.randint(crypto_min, crypto_max)
            new_crypto = player['crypto_money'] + stolen_crypto
            update_player(
                user_id,
                crypto_money=new_crypto,
                last_crime_time=datetime.now().isoformat(),
                happiness=min(100, player['happiness'] + 15)
            )
            await update.message.reply_text(f"✅ Преступление удалось!\n\n💰 Вы получили: {stolen_crypto} USD в крипте\n💵 Теперь у вас: {new_crypto} USD\n😊 Счастье: +15")
        else:
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
                knows_uncle=0,
                crypto_money=0,
                has_crypto_wallet=0
            )

# ШКОЛА
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
        ["💪 Заняться спортом", "🎒 Собрать портфель"],
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

async def school_sport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    new_health = min(100, player['health'] + 5)
    new_happiness = max(0, player['happiness'] - 2)
    
    update_player(user_id, health=new_health, happiness=new_happiness)
    
    await update.message.reply_text(f"💪 Позанимались спортом в школе!\n\n❤️ Здоровье: +5 (теперь {new_health})\n😔 Счастье: -2 (теперь {new_happiness})")

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
    is_probation, probation_seconds = await check_probation(user_id)
    if is_probation:
        await update.message.reply_text(f"⏰ Вы на учете! Курить нельзя еще {probation_seconds} секунд.")
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

# КУРЕНИЕ И ВЕЙПИНГ
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
    is_probation, probation_seconds = await check_probation(user_id)
    if is_probation:
        await update.message.reply_text(f"⏰ Вы на учете! Курить нельзя еще {probation_seconds} секунд.")
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
            if juice_strength >= 90:
                unconscious_time = 20  # Персиковый залив
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

# ДОМ И КВАРТИРА
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
            ["💨 Покурить кальян", "🍻 Выпить пиво"],
            ["💻 Поработать за ноутбуком", "😊 Отдохнуть"],
            ["🐶 Выгулять собаку", "💪 Потренироваться дома"],
            ["⬅️ Назад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🏡 ВАША КВАРТИРА\n\nВы в безопасности, можете заниматься чем угодно!", reply_markup=reply_markup)
        return
    
    # Если живет с родителями
    keyboard = [
        ["🚬 Покурить вейп дома", "🍃 Покурить бумагу с чаем"],
        ["💻 Поработать за ноутбуком", "😊 Отдохнуть"],
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
        ["💨 Покурить кальян", "🍻 Выпить пиво"],
        ["💻 Поработать за ноутбуком", "😊 Отдохнуть"],
        ["🐶 Выгулять собаку", "💪 Потренироваться дома"],
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

async def work_from_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_laptop']:
        await update.message.reply_text("❌ У вас нет ноутбука для работы!")
        return
    
    earnings = 100
    new_money = player['money'] + earnings
    
    update_player(user_id, money=new_money, happiness=min(100, player['happiness'] + 5))
    
    await update.message.reply_text(f"💻 Поработали из дома!\n\n💰 Заработано: {earnings} руб.\n💵 Теперь у вас: {new_money} руб.\n😊 Счастье: +5")

async def rest_at_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    new_health = min(100, player['health'] + 10)
    new_happiness = min(100, player['happiness'] + 15)
    
    update_player(user_id, health=new_health, happiness=new_happiness)
    
    await update.message.reply_text(f"😊 Хорошо отдохнули дома!\n\n❤️ Здоровье: +10 (теперь {new_health})\n😊 Счастье: +15 (теперь {new_happiness})")

# ДЕВУШКА
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
        keyboard.append(["💬 Поговорить", "💔 Расстаться"])
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

async def talk_to_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    happiness_increase = random.randint(5, 15)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    new_happiness = min(100, player['happiness'] + 5)
    
    update_player(
        user_id,
        girlfriend_happiness=new_girlfriend_happiness,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"💬 Поговорили с девушкой!\n\n💕 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness})\n😊 Ваше счастье: +5 (теперь {new_happiness})")

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

# ПАСПОРТ И ДР
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
        [InlineKeyboardButton("🚗 Транспорт", callback_data="transport_shop")],
        [InlineKeyboardButton("🐶 Питомцы", callback_data="pets_shop")],
        [InlineKeyboardButton("💰 Крипта", callback_data="crypto_shop")],
        [InlineKeyboardButton("💪 Спорт", callback_data="sport_shop")],
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
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await query.edit_message_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
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
    
    await query.edit_message_text(
        "🛒 Магазин NurikVape\n\n"
        "💨 Вейпы:\n"
        "• Charin Baby синий - 1500 руб.\n"
        "• Boost 2 черный - 1800 руб.\n" 
        "• Hero 3 белый - 2000 руб.\n\n"
        "💧 Жидкости:\n"
        "• Персиковый залив 🌊 90mg - 450 руб.\n"
        "• Мятный Шок ❄️ 50mg - 400 руб.\n"
        "• Охлаждающие яблоко🧊 40mg - 350 руб.\n"
        "• Виноградный повал 55mg - 380 руб.",
        reply_markup=reply_markup
    )

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

# НОВЫЕ ФУНКЦИИ

# ТРАНСПОРТ
async def transport_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    keyboard = []
    if player['has_car']:
        keyboard.append(["🚗 Поехать на машине"])
    else:
        keyboard.append(["🚗 Купить машину"])
    keyboard.append(["⬅️ Назад"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if player['has_car']:
        message = f"🚗 ВАШ ТРАНСПОРТ\n\nМашина: {player['car_type']}\n\nЧто хотите сделать?"
    else:
        message = "🚗 ТРАНСПОРТ\n\nУ вас пока нет машины. Хотите купить?"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def drive_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_car']:
        await update.message.reply_text("❌ У вас нет машины!")
        return
    
    new_happiness = min(100, player['happiness'] + 10)
    update_player(user_id, happiness=new_happiness)
    
    await update.message.reply_text(f"🚗 Покатались на {player['car_type']}!\n\n😊 Счастье: +10 (теперь {new_happiness})")

# ПИТОМЕЦ
async def pet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    keyboard = []
    if player['has_dog']:
        keyboard.append(["🐶 Выгулять собаку", "🍖 Покормить собаку"])
        keyboard.append(["💕 Поиграть с собакой"])
    else:
        keyboard.append(["🐶 Купить собаку"])
    keyboard.append(["⬅️ Назад"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if player['has_dog']:
        message = f"🐶 ВАШ ПИТОМЕЦ\n\nСчастье собаки: {player['dog_happiness']}/100\n\nЧто хотите сделать?"
    else:
        message = "🐶 ПИТОМЕЦ\n\nУ вас пока нет питомца. Хотите купить собаку?"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def walk_dog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_dog']:
        await update.message.reply_text("❌ У вас нет собаки!")
        return
    
    new_dog_happiness = min(100, player['dog_happiness'] + 20)
    new_happiness = min(100, player['happiness'] + 5)
    
    update_player(
        user_id,
        dog_happiness=new_dog_happiness,
        happiness=new_happiness,
        last_walk_time=datetime.now().isoformat()
    )
    
    await update.message.reply_text(f"🐶 Выгуляли собаку!\n\n💕 Счастье собаки: +20 (теперь {new_dog_happiness})\n😊 Ваше счастье: +5 (теперь {new_happiness})")

async def feed_dog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_dog']:
        await update.message.reply_text("❌ У вас нет собаки!")
        return
    
    if player['food'] < 10:
        await update.message.reply_text("❌ Недостаточно еды для собаки!")
        return
    
    new_food = player['food'] - 10
    new_dog_happiness = min(100, player['dog_happiness'] + 15)
    
    update_player(
        user_id,
        food=new_food,
        dog_happiness=new_dog_happiness
    )
    
    await update.message.reply_text(f"🍖 Покормили собаку!\n\n💕 Счастье собаки: +15 (теперь {new_dog_happiness})\n🍖 Еды осталось: {new_food}")

async def play_with_dog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_dog']:
        await update.message.reply_text("❌ У вас нет собаки!")
        return
    
    new_dog_happiness = min(100, player['dog_happiness'] + 10)
    new_happiness = min(100, player['happiness'] + 8)
    
    update_player(
        user_id,
        dog_happiness=new_dog_happiness,
        happiness=new_happiness
    )
    
    await update.message.reply_text(f"💕 Поиграли с собакой!\n\n💕 Счастье собаки: +10 (теперь {new_dog_happiness})\n😊 Ваше счастье: +8 (теперь {new_happiness})")

# КРИПТА
async def crypto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    keyboard = []
    if player['has_crypto_wallet']:
        keyboard.append(["💰 Инвестировать в крипту", "📈 Продать крипту"])
        keyboard.append(["🔐 Заработать на майнинге"])
    else:
        keyboard.append(["💰 Создать крипто-кошелек"])
    keyboard.append(["⬅️ Назад"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if player['has_crypto_wallet']:
        message = f"💰 КРИПТА\n\nБаланс: {player['crypto_money']} USD\n\nЧто хотите сделать?"
    else:
        message = "💰 КРИПТА\n\nУ вас пока нет крипто-кошелька. Хотите создать?"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def invest_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    if not player['has_crypto_wallet']:
        await update.message.reply_text("❌ У вас нет крипто-кошелька!")
        return
    
    if player['money'] < 1000:
        await update.message.reply_text("❌ Для инвестиций нужно минимум 1000 руб.!")
        return
    
    # Шанс успеха инвестиции
    if random.random() < 0.6:
        profit = random.randint(100, 500)
        new_crypto = player['crypto_money'] + profit
        new_money = player['money'] - 1000
        
        update_player(
            user_id,
            crypto_money=new_crypto,
            money=new_money
        )
        
        await update.message.reply_text(f"💰 Успешная инвестиция!\n\n💵 Потрачено: 1000 руб.\n💰 Заработано: {profit} USD\n💳 Теперь у вас: {new_crypto} USD\n💵 Денег осталось: {new_money} руб.")
    else:
        new_money = player['money'] - 1000
        update_player(user_id, money=new_money)
        await update.message.reply_text(f"❌ Инвестиция провалилась!\n\n💵 Потеряно: 1000 руб.\n💵 Денег осталось: {new_money} руб.")

# СПОРТЗАЛ
async def gym_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    keyboard = [
        ["💪 Тренироваться в зале", "🥊 Боксировать"],
        ["🏋️‍♂️ Качать железо", "🧘‍♂️ Йога"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message = f"💪 СПОРТЗАЛ\n\nУровень: {player['gym_level']}\n\nВыберите тренировку:"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def train_at_gym(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    new_health = min(100, player['health'] + 8)
    new_happiness = max(0, player['happiness'] - 3)
    
    # Шанс повышения уровня
    if random.random() < 0.3:
        new_gym_level = player['gym_level'] + 1
        update_player(
            user_id,
            health=new_health,
            happiness=new_happiness,
            gym_level=new_gym_level,
            last_gym_time=datetime.now().isoformat()
        )
        await update.message.reply_text(f"💪 Отлично потренировались!\n\n❤️ Здоровье: +8 (теперь {new_health})\n😔 Счастье: -3 (теперь {new_happiness})\n🎯 Уровень спортзала повышен до {new_gym_level}!")
    else:
        update_player(
            user_id,
            health=new_health,
            happiness=new_happiness,
            last_gym_time=datetime.now().isoformat()
        )
        await update.message.reply_text(f"💪 Потренировались в зале!\n\n❤️ Здоровье: +8 (теперь {new_health})\n😔 Счастье: -3 (теперь {new_happiness})")

# КВЕСТЫ И РЕПУТАЦИЯ
async def quests_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    player = get_player(user_id)
    
    keyboard = [
        ["🎯 Взять простой квест", "⭐ Взять сложный квест"],
        ["🏆 Проверить выполнение", "📊 Статистика квестов"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message = f"🎯 КВЕСТЫ\n\nВыполнено: {player['completed_quests']} квестов\nРепутация: {player['reputation']}\n\nВыберите действие:"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def take_easy_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    # Простой квест - 70% шанс успеха
    if random.random() < 0.7:
        reward = random.randint(200, 500)
        reputation_gain = 1
        new_money = get_player(user_id)['money'] + reward
        new_reputation = get_player(user_id)['reputation'] + reputation_gain
        new_completed_quests = get_player(user_id)['completed_quests'] + 1
        
        update_player(
            user_id,
            money=new_money,
            reputation=new_reputation,
            completed_quests=new_completed_quests
        )
        
        await update.message.reply_text(f"🎯 Квест выполнен!\n\n💰 Награда: {reward} руб.\n⭐ Репутация: +{reputation_gain}\n💵 Теперь у вас: {new_money} руб.\n🎯 Выполнено квестов: {new_completed_quests}")
    else:
        await update.message.reply_text("❌ Не удалось выполнить квест... Попробуйте еще раз!")

# ОБРАБОТЧИК КНОПОК МАГАЗИНА
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
    
    callback_data = query.data
    
    # Навигация по магазинам
    if callback_data == "back_to_main":
        await start(update, context)
        return
    elif callback_data == "back_to_shop":
        await shop(update, context)
        return
    elif callback_data == "food_health_shop":
        await show_food_health_shop(query)
    elif callback_data == "cigarettes_shop":
        await show_cigarettes_shop(query)
    elif callback_data == "vapes_shop":
        await show_vapes_shop(query)
    elif callback_data == "disposables_shop":
        await show_disposables_shop(query)
    elif callback_data == "iqos_shop":
        await show_iqos_shop(query)
    elif callback_data == "hookah_shop":
        await show_hookah_shop(query)
    elif callback_data == "snus_shop":
        await show_snus_shop(query)
    elif callback_data == "nurik_vape_shop":
        await nurik_vape_shop(update, context)
    elif callback_data == "work_tech_shop":
        await show_work_tech_shop(query)
    elif callback_data == "real_estate_shop":
        await show_real_estate_shop(query)
    elif callback_data == "transport_shop":
        await show_transport_shop(query)
    elif callback_data == "pets_shop":
        await show_pets_shop(query)
    elif callback_data == "crypto_shop":
        await show_crypto_shop(query)
    elif callback_data == "sport_shop":
        await show_sport_shop(query)
    
    # Обработка покупок
    elif callback_data.startswith("buy_"):
        await handle_purchase(query, callback_data, player)
    elif callback_data.startswith("get_job_"):
        await handle_job_purchase(query, callback_data, player)
    elif callback_data.startswith("uncle_"):
        await smoke_uncle_hookah(update, context)

async def show_food_health_shop(query):
    keyboard = [
        [InlineKeyboardButton("🍖 Еда (+50) - 100 руб.", callback_data="buy_food")],
        [InlineKeyboardButton("❤️ Лечение (+30 здоровья) - 200 руб.", callback_data="buy_health")],
        [InlineKeyboardButton("😊 Антидепрессанты (+20 счастья) - 150 руб.", callback_data="buy_happiness")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🍖 ЕДА И ЗДОРОВЬЕ:", reply_markup=reply_markup)

async def show_cigarettes_shop(query):
    keyboard = [
        [InlineKeyboardButton("🚬 Сигареты (20 шт.) - 300 руб.", callback_data="buy_cigarettes")],
        [InlineKeyboardButton("🍒 Chapman (20 шт.) - 350 руб.", callback_data="buy_chapman")],
        [InlineKeyboardButton("🚬 Winston (20 шт.) - 400 руб.", callback_data="buy_winston")],
        [InlineKeyboardButton("🚬 Parliament (20 шт.) - 450 руб.", callback_data="buy_parliament")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🚬 СИГАРЕТЫ:", reply_markup=reply_markup)

async def show_vapes_shop(query):
    keyboard = [
        [InlineKeyboardButton("💨 Вейп обычный - 1000 руб.", callback_data="buy_vape")],
        [InlineKeyboardButton("💧 Жидкость 30ml - 300 руб.", callback_data="buy_juice")],
        [InlineKeyboardButton("🔋 Зарядка вейпа - 50 руб.", callback_data="charge_vape")],
        [InlineKeyboardButton("💧 Безникотиновая жидкость - 250 руб.", callback_data="buy_nicotine_free_juice")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💨 ВЕЙПЫ И ЖИДКОСТИ:", reply_markup=reply_markup)

async def show_disposables_shop(query):
    keyboard = [
        [InlineKeyboardButton("🚬 Одноразка HQD 1500 тяг - 800 руб.", callback_data="buy_disposable_hqd")],
        [InlineKeyboardButton("🚬 Одноразка Elf Bar 2000 тяг - 1000 руб.", callback_data="buy_disposable_elfbar")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🚬 ОДНОРАЗКИ:", reply_markup=reply_markup)

async def show_iqos_shop(query):
    keyboard = [
        [InlineKeyboardButton("🔥 Айкос устройство - 2000 руб.", callback_data="buy_iqos")],
        [InlineKeyboardButton("📦 Стики HEETS (20 шт.) - 400 руб.", callback_data="buy_heets")],
        [InlineKeyboardButton("🔋 Зарядка Айкос - 100 руб.", callback_data="charge_iqos")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🔥 АЙКОС:", reply_markup=reply_markup)

async def show_hookah_shop(query):
    keyboard = [
        [InlineKeyboardButton("💨 Кальян - 1500 руб.", callback_data="buy_hookah")],
        [InlineKeyboardButton("🔥 Угли (10 шт.) - 100 руб.", callback_data="buy_coals")],
        [InlineKeyboardButton("🌿 Табак DarkSide (50г) - 600 руб.", callback_data="buy_darkside_tobacco")],
        [InlineKeyboardButton("🔥 Горелка - 200 руб.", callback_data="buy_burner")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💨 КАЛЬЯНЫ:", reply_markup=reply_markup)

async def show_snus_shop(query):
    keyboard = [
        [InlineKeyboardButton("📦 Снюс обычный 150mg - 300 руб.", callback_data="buy_snus")],
        [InlineKeyboardButton("📦 Снюс крепкий 500mg - 500 руб.", callback_data="buy_strong_snus")],
        [InlineKeyboardButton("🌿 Безникотиновый снюс - 200 руб.", callback_data="buy_nicotine_free_snus")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📦 СНЮС:", reply_markup=reply_markup)

async def show_work_tech_shop(query):
    keyboard = [
        [InlineKeyboardButton("💼 Устроиться разнорабочим - бесплатно", callback_data="get_job_1")],
        [InlineKeyboardButton("💼 Устроиться продавцом - 500 руб.", callback_data="get_job_2")],
        [InlineKeyboardButton("💼 Устроиться офисным работником - 1000 руб.", callback_data="get_job_3")],
        [InlineKeyboardButton("💼 Устроиться дальнобойщиком - 3000 руб.", callback_data="get_job_4")],
        [InlineKeyboardButton("💼 Устроиться менеджером - 2000 руб.", callback_data="get_job_5")],
        [InlineKeyboardButton("💼 Устроиться директором - 5000 руб.", callback_data="get_job_6")],
        [InlineKeyboardButton("💼 Устроиться мошенником - 1500 руб.", callback_data="get_job_7")],
        [InlineKeyboardButton("💼 Устроиться работником ПВЗ - 8000 руб.", callback_data="get_job_8")],
        [InlineKeyboardButton("💼 Устроиться рабочим - 300 руб.", callback_data="get_job_9")],
        [InlineKeyboardButton("💻 Ноутбук - 5000 руб.", callback_data="buy_laptop")],
        [InlineKeyboardButton("🛡️ VPN - 1000 руб.", callback_data="buy_vpn")],
        [InlineKeyboardButton("📱 iPhone 16 Pro Max - 15000 руб.", callback_data="buy_iphone")],
        [InlineKeyboardButton("📱 Samsung Galaxy - 12000 руб.", callback_data="buy_samsung")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💼 РАБОТА И ТЕХНОЛОГИИ:", reply_markup=reply_markup)

async def show_real_estate_shop(query):
    keyboard = [
        [InlineKeyboardButton("🏡 Купить квартиру - 50000 руб.", callback_data="buy_apartment_shop")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🏡 НЕДВИЖИМОСТЬ:", reply_markup=reply_markup)

async def show_transport_shop(query):
    keyboard = [
        [InlineKeyboardButton("🚗 Купить машину - 30000 руб.", callback_data="buy_car")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🚗 ТРАНСПОРТ:", reply_markup=reply_markup)

async def show_pets_shop(query):
    keyboard = [
        [InlineKeyboardButton("🐶 Купить собаку - 5000 руб.", callback_data="buy_dog")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🐶 ПИТОМЦЫ:", reply_markup=reply_markup)

async def show_crypto_shop(query):
    keyboard = [
        [InlineKeyboardButton("💰 Создать крипто-кошелек - 2000 руб.", callback_data="buy_crypto_wallet")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💰 КРИПТА:", reply_markup=reply_markup)

async def show_sport_shop(query):
    keyboard = [
        [InlineKeyboardButton("💪 Абонемент в спортзал - 1000 руб.", callback_data="buy_gym")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💪 СПОРТ:", reply_markup=reply_markup)

async def handle_purchase(query, callback_data, player):
    user_id = query.from_user.id
    purchase_made = False
    
    if callback_data == "buy_food":
        if player['money'] >= 100:
            new_money = player['money'] - 100
            new_food = min(100, player['food'] + 50)
            update_player(user_id, money=new_money, food=new_food)
            await query.edit_message_text(f"🍖 Купили еду!\n\n💵 Потрачено: 100 руб.\n🍖 Еда: +50 (теперь {new_food})\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки еды!")
    
    elif callback_data == "buy_health":
        if player['money'] >= 200:
            new_money = player['money'] - 200
            new_health = min(100, player['health'] + 30)
            update_player(user_id, money=new_money, health=new_health)
            await query.edit_message_text(f"❤️ Прошли лечение!\n\n💵 Потрачено: 200 руб.\n❤️ Здоровье: +30 (теперь {new_health})\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для лечения!")
    
    elif callback_data == "buy_happiness":
        if player['money'] >= 150:
            new_money = player['money'] - 150
            new_happiness = min(100, player['happiness'] + 20)
            update_player(user_id, money=new_money, happiness=new_happiness)
            await query.edit_message_text(f"😊 Купили антидепрессанты!\n\n💵 Потрачено: 150 руб.\n😊 Счастье: +20 (теперь {new_happiness})\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для антидепрессантов!")
    
    elif callback_data == "buy_cigarettes":
        if player['money'] >= 300:
            new_money = player['money'] - 300
            new_cigarettes = player['cigarettes'] + 20
            update_player(user_id, money=new_money, cigarettes=new_cigarettes)
            await query.edit_message_text(f"🚬 Купили сигареты!\n\n💵 Потрачено: 300 руб.\n🚬 Сигарет: +20 (теперь {new_cigarettes})\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки сигарет!")
    
    elif callback_data == "buy_chapman":
        if player['money'] >= 350:
            new_money = player['money'] - 350
            new_chapman = player['chapman_cigarettes'] + 20
            update_player(user_id, money=new_money, chapman_cigarettes=new_chapman)
            await query.edit_message_text(f"🍒 Купили Чапман!\n\n💵 Потрачено: 350 руб.\n🍒 Чапман: +20 (теперь {new_chapman})\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Чапман!")
    
    elif callback_data == "buy_vape":
        if player['money'] >= 1000:
            new_money = player['money'] - 1000
            update_player(user_id, money=new_money, vape_type="Обычный вейп", vape_battery=100)
            await query.edit_message_text(f"💨 Купили вейп!\n\n💵 Потрачено: 1000 руб.\n💨 Теперь у вас есть вейп!\n🔋 Батарея: 100%\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки вейпа!")
    
    elif callback_data == "buy_juice":
        if player['money'] >= 300:
            new_money = player['money'] - 300
            new_juice = player['vape_juice'] + 30
            update_player(user_id, money=new_money, vape_juice=new_juice, juice_flavor="Обычная", juice_strength=20)
            await query.edit_message_text(f"💧 Купили жидкость для вейпа!\n\n💵 Потрачено: 300 руб.\n💧 Жидкости: +30мл (теперь {new_juice}мл)\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки жидкости!")
    
    elif callback_data == "buy_apartment_shop":
        if player['money'] >= 50000:
            new_money = player['money'] - 50000
            update_player(user_id, money=new_money, has_apartment=1)
            await query.edit_message_text(f"🏡 Купили квартиру!\n\n💵 Потрачено: 50000 руб.\n🏡 Теперь у вас есть своя квартира!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки квартиры!")
    
    elif callback_data == "buy_laptop":
        if player['money'] >= 5000:
            new_money = player['money'] - 5000
            update_player(user_id, money=new_money, has_laptop=1)
            await query.edit_message_text(f"💻 Купили ноутбук!\n\n💵 Потрачено: 5000 руб.\n💻 Теперь у вас есть ноутбук!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки ноутбука!")
    
    elif callback_data == "buy_vpn":
        if player['money'] >= 1000:
            new_money = player['money'] - 1000
            update_player(user_id, money=new_money, has_vpn=1)
            await query.edit_message_text(f"🛡️ Купили VPN!\n\n💵 Потрачено: 1000 руб.\n🛡️ Теперь у вас есть VPN!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки VPN!")
    
    elif callback_data == "buy_iphone":
        if player['money'] >= 15000:
            new_money = player['money'] - 15000
            update_player(user_id, money=new_money, has_iphone=1)
            await query.edit_message_text(f"📱 Купили iPhone 16 Pro Max!\n\n💵 Потрачено: 15000 руб.\n📱 Теперь у вас есть крутой телефон!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки iPhone!")
    
    elif callback_data == "buy_samsung":
        if player['money'] >= 12000:
            new_money = player['money'] - 12000
            update_player(user_id, money=new_money, has_samsung=1)
            await query.edit_message_text(f"📱 Купили Samsung Galaxy!\n\n💵 Потрачено: 12000 руб.\n📱 Теперь у вас есть крутой телефон!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Samsung!")
    
    elif callback_data == "buy_crypto_wallet":
        if player['money'] >= 2000:
            new_money = player['money'] - 2000
            update_player(user_id, money=new_money, has_crypto_wallet=1)
            await query.edit_message_text(f"💰 Создали крипто-кошелек!\n\n💵 Потрачено: 2000 руб.\n💰 Теперь у вас есть крипто-кошелек!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для создания крипто-кошелька!")
    
    elif callback_data == "buy_car":
        if player['money'] >= 30000:
            new_money = player['money'] - 30000
            update_player(user_id, money=new_money, has_car=1, car_type="Обычная машина")
            await query.edit_message_text(f"🚗 Купили машину!\n\n💵 Потрачено: 30000 руб.\n🚗 Теперь у вас есть машина!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки машины!")
    
    elif callback_data == "buy_dog":
        if player['money'] >= 5000:
            new_money = player['money'] - 5000
            update_player(user_id, money=new_money, has_dog=1, dog_happiness=50)
            await query.edit_message_text(f"🐶 Купили собаку!\n\n💵 Потрачено: 5000 руб.\n🐶 Теперь у вас есть питомец!\n💕 Счастье собаки: 50/100\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки собаки!")
    
    elif callback_data == "buy_gym":
        if player['money'] >= 1000:
            new_money = player['money'] - 1000
            update_player(user_id, money=new_money, gym_level=1)
            await query.edit_message_text(f"💪 Купили абонемент в спортзал!\n\n💵 Потрачено: 1000 руб.\n💪 Теперь вы можете тренироваться в спортзале!\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки абонемента!")
    
    # Товары из NurikVape
    elif callback_data == "buy_charin_baby":
        if player['money'] >= 1500:
            new_money = player['money'] - 1500
            update_player(user_id, money=new_money, vape_type="Charin Baby синий", vape_battery=100)
            await query.edit_message_text(f"💨 Купили Charin Baby синий!\n\n💵 Потрачено: 1500 руб.\n💨 Теперь у вас есть новый вейп!\n🔋 Батарея: 100%\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Charin Baby!")
    
    elif callback_data == "buy_boost_2_black":
        if player['money'] >= 1800:
            new_money = player['money'] - 1800
            update_player(user_id, money=new_money, vape_type="Boost 2 черный", vape_battery=100)
            await query.edit_message_text(f"💨 Купили Boost 2 черный!\n\n💵 Потрачено: 1800 руб.\n💨 Теперь у вас есть новый вейп!\n🔋 Батарея: 100%\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Boost 2!")
    
    elif callback_data == "buy_hero_3_white":
        if player['money'] >= 2000:
            new_money = player['money'] - 2000
            update_player(user_id, money=new_money, vape_type="Hero 3 белый", vape_battery=100)
            await query.edit_message_text(f"💨 Купили Hero 3 белый!\n\n💵 Потрачено: 2000 руб.\n💨 Теперь у вас есть новый вейп!\n🔋 Батарея: 100%\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Hero 3!")
    
    elif callback_data == "buy_peach_flood":
        if player['money'] >= 450:
            new_money = player['money'] - 450
            new_juice = player['vape_juice'] + 30
            update_player(user_id, money=new_money, vape_juice=new_juice, juice_flavor="Персиковый залив", juice_strength=90)
            await query.edit_message_text(f"💧 Купили Персиковый залив 90mg!\n\n💵 Потрачено: 450 руб.\n💧 Жидкости: +30мл (теперь {new_juice}мл)\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки жидкости!")
    
    elif callback_data == "buy_mint_shock":
        if player['money'] >= 400:
            new_money = player['money'] - 400
            new_juice = player['vape_juice'] + 30
            update_player(user_id, money=new_money, vape_juice=new_juice, juice_flavor="Мятный Шок", juice_strength=50)
            await query.edit_message_text(f"💧 Купили Мятный Шок 50mg!\n\n💵 Потрачено: 400 руб.\n💧 Жидкости: +30мл (теперь {new_juice}мл)\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки жидкости!")
    
    elif callback_data == "buy_cool_apple":
        if player['money'] >= 350:
            new_money = player['money'] - 350
            new_juice = player['vape_juice'] + 30
            update_player(user_id, money=new_money, vape_juice=new_juice, juice_flavor="Охлаждающие яблоко", juice_strength=40)
            await query.edit_message_text(f"💧 Купили Охлаждающие яблоко 40mg!\n\n💵 Потрачено: 350 руб.\n💧 Жидкости: +30мл (теперь {new_juice}мл)\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки жидкости!")
    
    elif callback_data == "buy_grape_knockout":
        if player['money'] >= 380:
            new_money = player['money'] - 380
            new_juice = player['vape_juice'] + 30
            update_player(user_id, money=new_money, vape_juice=new_juice, juice_flavor="Виноградный повал", juice_strength=55)
            await query.edit_message_text(f"💧 Купили Виноградный повал 55mg!\n\n💵 Потрачено: 380 руб.\n💧 Жидкости: +30мл (теперь {new_juice}мл)\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки жидкости!")
    
    # Товары из ларька
    elif callback_data == "buy_fillder":
        if player['money'] >= 700:
            new_money = player['money'] - 700
            # Шанс брака 30%
            defective = random.random() < 0.3
            update_player(user_id, money=new_money, disposable_vape_type="Fillder❤️ Redbull 30mg", disposable_vape_puffs=1500, disposable_vape_defective=1 if defective else 0)
            if defective:
                await query.edit_message_text(f"🚬 Купили Fillder❤️ Redbull 30mg!\n\n💵 Потрачено: 700 руб.\n⚠️ Осторожно! Одноразка может быть бракованной!\n📦 Тяг: 1500\n💵 Осталось: {new_money} руб.")
            else:
                await query.edit_message_text(f"🚬 Купили Fillder❤️ Redbull 30mg!\n\n💵 Потрачено: 700 руб.\n📦 Тяг: 1500\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Fillder!")
    
    elif callback_data == "buy_magnum":
        if player['money'] >= 250:
            new_money = player['money'] - 250
            # Шанс брака 40%
            defective = random.random() < 0.4
            update_player(user_id, money=new_money, disposable_vape_type="Magnum Глинтвейн 50mg", disposable_vape_puffs=1200, disposable_vape_defective=1 if defective else 0)
            if defective:
                await query.edit_message_text(f"🚬 Купили Magnum Глинтвейн 50mg!\n\n💵 Потрачено: 250 руб.\n⚠️ Осторожно! Одноразка может быть бракованной!\n📦 Тяг: 1200\n💵 Осталось: {new_money} руб.")
            else:
                await query.edit_message_text(f"🚬 Купили Magnum Глинтвейн 50mg!\n\n💵 Потрачено: 250 руб.\n📦 Тяг: 1200\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки Magnum!")
    
    elif callback_data == "buy_beer_larek":
        if player['money'] >= 120:
            new_money = player['money'] - 120
            new_beer = player['beer'] + 1
            update_player(user_id, money=new_money, beer=new_beer)
            await query.edit_message_text(f"🍻 Купили пиво!\n\n💵 Потрачено: 120 руб.\n🍻 Пиво: +1 (теперь {new_beer})\n💵 Осталось: {new_money} руб.")
            purchase_made = True
        else:
            await query.edit_message_text("❌ Недостаточно денег для покупки пива!")
    
    if not purchase_made:
        if "Недостаточно" not in query.message.text:
            await query.edit_message_text("❌ Недостаточно денег для покупки!")
    
    elif purchase_made:
        # После покупки возвращаем в магазин через 2 секунды
        await asyncio.sleep(2)
        await shop(query, context)

async def handle_job_purchase(query, callback_data, player):
    user_id = query.from_user.id
    purchase_made = False
    
    job_prices = {
        "get_job_1": 0,      # Разнорабочий
        "get_job_2": 500,    # Продавец
        "get_job_3": 1000,   # Офисный работник
        "get_job_4": 3000,   # Дальнобойщик
        "get_job_5": 2000,   # Менеджер
        "get_job_6": 5000,   # Директор
        "get_job_7": 1500,   # Мошенник
        "get_job_8": 8000,   # Работник ПВЗ
        "get_job_9": 300     # Рабочий
    }
    
    job_names = {
        "get_job_1": "разнорабочим",
        "get_job_2": "продавцом", 
        "get_job_3": "офисным работником",
        "get_job_4": "дальнобойщиком",
        "get_job_5": "менеджером",
        "get_job_6": "директором",
        "get_job_7": "мошенником",
        "get_job_8": "работником ПВЗ",
        "get_job_9": "рабочим"
    }
    
    job_levels = {
        "get_job_1": 1,
        "get_job_2": 2,
        "get_job_3": 3,
        "get_job_4": 4,
        "get_job_5": 5,
        "get_job_6": 6,
        "get_job_7": 7,
        "get_job_8": 8,
        "get_job_9": 9
    }
    
    job_salaries = {
        "get_job_1": 50,
        "get_job_2": 100,
        "get_job_3": 200,
        "get_job_4": 800,
        "get_job_5": 500,
        "get_job_6": 1000,
        "get_job_7": 600,
        "get_job_8": 3250,
        "get_job_9": 150
    }
    
    if callback_data in job_prices:
        job_level = job_levels[callback_data]
        job_price = job_prices[callback_data]
        job_name = job_names[callback_data]
        salary = job_salaries[callback_data]
        
        if player['job_level'] >= job_level:
            await query.edit_message_text("❌ У вас уже есть работа этого уровня или выше!")
            return
        
        if player['money'] >= job_price:
            new_money = player['money'] - job_price
            update_player(user_id, money=new_money, job_level=job_level)
            
            if job_price == 0:
                await query.edit_message_text(f"💼 Устроились {job_name}!\n\n💰 Зарплата: {salary} руб. за работу\n💼 Теперь вы можете работать!")
            else:
                await query.edit_message_text(f"💼 Устроились {job_name}!\n\n💵 Потрачено: {job_price} руб.\n💰 Зарплата: {salary} руб. за работу\n💵 Осталось: {new_money} руб.")
            
            purchase_made = True
        else:
            await query.edit_message_text(f"❌ Недостаточно денег для устройства на работу! Нужно {job_price} руб.")
    
    if purchase_made:
        await asyncio.sleep(2)
        await shop(query, context)

# ОБРАБОТЧИК СООБЩЕНИЙ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверка бессознательного состояния
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    text = update.message.text
    
    # Основное меню
    if text == "🏠 Статус":
        await show_status(update, context)
    elif text == "💼 Работа":
        await work(update, context)
    elif text == "🏠 Домой":
        await go_home(update, context)
    elif text == "🔫 Криминал":
        await crime_menu(update, context)
    elif text in ["💰 Украсть кошелек", "🏪 Ограбить магазин", "🏠 Ограбить квартиру", "🚗 Угнать машину", "🕵️‍♂️ Мошенничество", "📱 Украсть телефон", "💻 Взлом банка", "🔐 Крипто-кража"]:
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
    elif text == "💪 Заняться спортом":
        await school_sport(update, context)
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
    elif text == "💻 Поработать за ноутбуком":
        await work_from_home(update, context)
    elif text == "😊 Отдохнуть":
        await rest_at_home(update, context)
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
    elif text == "💬 Поговорить":
        await talk_to_girlfriend(update, context)
    elif text == "💔 Расстаться":
        await break_up(update, context)
    
    # Новые функции
    elif text == "🚗 Транспорт":
        await transport_menu(update, context)
    elif text == "🚗 Поехать на машине":
        await drive_car(update, context)
    elif text == "🐶 Питомец":
        await pet_menu(update, context)
    elif text == "🐶 Выгулять собаку":
        await walk_dog(update, context)
    elif text == "🍖 Покормить собаку":
        await feed_dog(update, context)
    elif text == "💕 Поиграть с собакой":
        await play_with_dog(update, context)
    elif text == "💰 Крипта":
        await crypto_menu(update, context)
    elif text == "💰 Инвестировать в крипту":
        await invest_crypto(update, context)
    elif text == "💪 Спортзал":
        await gym_menu(update, context)
    elif text == "💪 Тренироваться в зале":
        await train_at_gym(update, context)
    elif text == "🎯 Квесты":
        await quests_menu(update, context)
    elif text == "🎯 Взять простой квест":
        await take_easy_quest(update, context)
    elif text == "⭐ Репутация":
        await quests_menu(update, context)
    
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