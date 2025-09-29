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

BOT_TOKEN = os.environ.get('BOT_TOKEN', "8400415519:AAETeEt-fAb9JQiXEwSihi1ZYMWaH6U1aUA")

# БАЗА ДАННЫХ
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
            smoking_years INTEGER DEFAULT 0,
            cigarettes_smoked INTEGER DEFAULT 0,
            nicotine_addiction INTEGER DEFAULT 0,
            withdrawal_level INTEGER DEFAULT 0,
            willpower INTEGER DEFAULT 50,
            intelligence INTEGER DEFAULT 50,
            charisma INTEGER DEFAULT 50,
            endurance INTEGER DEFAULT 50,
            stress INTEGER DEFAULT 0,
            depression INTEGER DEFAULT 0,
            anxiety INTEGER DEFAULT 0,
            has_lung_cancer INTEGER DEFAULT 0,
            has_heart_disease INTEGER DEFAULT 0,
            dental_health INTEGER DEFAULT 100,
            skin_health INTEGER DEFAULT 100,
            last_doctor_visit TEXT,
            treatment_cost INTEGER DEFAULT 0,
            has_family INTEGER DEFAULT 0,
            children INTEGER DEFAULT 0,
            family_happiness INTEGER DEFAULT 0,
            friends_count INTEGER DEFAULT 0,
            last_therapy_time TEXT,
            beer_count INTEGER DEFAULT 0,
            has_alcohol_poisoning INTEGER DEFAULT 0,
            last_drink_time TEXT,
            vape_puffs_count INTEGER DEFAULT 0,
            current_cartridge_puffs INTEGER DEFAULT 0,
            last_meal_time TEXT,
            energy INTEGER DEFAULT 100,
            sleep INTEGER DEFAULT 100,
            reputation INTEGER DEFAULT 0,
            criminal_record INTEGER DEFAULT 0,
            in_jail INTEGER DEFAULT 0,
            jail_until TEXT,
            has_car INTEGER DEFAULT 0,
            car_type TEXT DEFAULT NULL,
            insurance INTEGER DEFAULT 0,
            loan INTEGER DEFAULT 0,
            loan_debt INTEGER DEFAULT 0,
            savings INTEGER DEFAULT 0,
            investments INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def upgrade_db():
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = {
            'beer_count': 'ALTER TABLE players ADD COLUMN beer_count INTEGER DEFAULT 0',
            'has_alcohol_poisoning': 'ALTER TABLE players ADD COLUMN has_alcohol_poisoning INTEGER DEFAULT 0',
            'last_drink_time': 'ALTER TABLE players ADD COLUMN last_drink_time TEXT',
            'vape_puffs_count': 'ALTER TABLE players ADD COLUMN vape_puffs_count INTEGER DEFAULT 0',
            'current_cartridge_puffs': 'ALTER TABLE players ADD COLUMN current_cartridge_puffs INTEGER DEFAULT 0',
            'last_meal_time': 'ALTER TABLE players ADD COLUMN last_meal_time TEXT',
            'energy': 'ALTER TABLE players ADD COLUMN energy INTEGER DEFAULT 100',
            'sleep': 'ALTER TABLE players ADD COLUMN sleep INTEGER DEFAULT 100',
            'reputation': 'ALTER TABLE players ADD COLUMN reputation INTEGER DEFAULT 0',
            'criminal_record': 'ALTER TABLE players ADD COLUMN criminal_record INTEGER DEFAULT 0',
            'in_jail': 'ALTER TABLE players ADD COLUMN in_jail INTEGER DEFAULT 0',
            'jail_until': 'ALTER TABLE players ADD COLUMN jail_until TEXT',
            'has_car': 'ALTER TABLE players ADD COLUMN has_car INTEGER DEFAULT 0',
            'car_type': 'ALTER TABLE players ADD COLUMN car_type TEXT DEFAULT NULL',
            'insurance': 'ALTER TABLE players ADD COLUMN insurance INTEGER DEFAULT 0',
            'loan': 'ALTER TABLE players ADD COLUMN loan INTEGER DEFAULT 0',
            'loan_debt': 'ALTER TABLE players ADD COLUMN loan_debt INTEGER DEFAULT 0',
            'savings': 'ALTER TABLE players ADD COLUMN savings INTEGER DEFAULT 0',
            'investments': 'ALTER TABLE players ADD COLUMN investments INTEGER DEFAULT 0'
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
                  'vape_type', 'vape_juice', 'juice_flavor', 'snus_packs', 'snus_strength',
                  'has_girlfriend', 'girlfriend_happiness', 'age', 'has_id', 'last_work_time',
                  'last_school_time', 'last_crime_time', 'last_date_time', 'last_smoke_time',
                  'last_fraud_time', 'has_iqos', 'iqos_sticks', 'iqos_battery', 'vape_battery',
                  'has_hookah', 'hookah_coals', 'hookah_tobacco', 'hookah_tobacco_amount',
                  'has_burner', 'disposable_vape_type', 'disposable_vape_puffs', 'chapman_cigarettes',
                  'on_probation', 'probation_until', 'created_at', 'has_tea_leaf', 'unconscious_until', 
                  'stick_flavor', 'has_nicotine_free_snus', 'last_smoke_puff_time', 'consecutive_puffs',
                  'has_iphone', 'has_samsung', 'parents_angry', 'parents_angry_until', 'police_in_school', 
                  'police_until', 'smoking_years', 'cigarettes_smoked', 'nicotine_addiction', 'withdrawal_level',
                  'willpower', 'intelligence', 'charisma', 'endurance', 'stress', 'depression', 'anxiety',
                  'has_lung_cancer', 'has_heart_disease', 'dental_health', 'skin_health', 'last_doctor_visit',
                  'treatment_cost', 'has_family', 'children', 'family_happiness', 'friends_count', 'last_therapy_time',
                  'beer_count', 'has_alcohol_poisoning', 'last_drink_time', 'vape_puffs_count', 'current_cartridge_puffs',
                  'last_meal_time', 'energy', 'sleep', 'reputation', 'criminal_record', 'in_jail', 'jail_until',
                  'has_car', 'car_type', 'insurance', 'loan', 'loan_debt', 'savings', 'investments']
        
        player_dict = {}
        for i, column in enumerate(columns):
            if i < len(player):
                player_dict[column] = player[i]
            else:
                player_dict[column] = None
        
        # Установка значений по умолчанию
        defaults = {
            'beer_count': 0, 'has_alcohol_poisoning': 0, 'vape_puffs_count': 0, 'current_cartridge_puffs': 0,
            'energy': 100, 'sleep': 100, 'reputation': 0, 'criminal_record': 0, 'in_jail': 0,
            'has_car': 0, 'insurance': 0, 'loan': 0, 'loan_debt': 0, 'savings': 0, 'investments': 0
        }
        
        for field, default in defaults.items():
            player_dict.setdefault(field, default)
        
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

# ДАННЫЕ МАГАЗИНОВ
VAPE_DEVICES = {
    "Pasito 2": {"price": 1200, "age_required": 18},
    "Knight": {"price": 900, "age_required": 18},
    "Minican": {"price": 800, "age_required": 18},
    "Xros": {"price": 1100, "age_required": 18},
    "Minifit": {"price": 700, "age_required": 18},
    "Boost 2": {"price": 1000, "age_required": 18},
    "Hero 3 Pink": {"price": 950, "age_required": 18},
    "Boost 3": {"price": 1300, "age_required": 18},
    "Charin Baby синий": {"price": 850, "age_required": 18},
    "Boost 2 черный": {"price": 1000, "age_required": 18},
    "Hero 3 белый": {"price": 950, "age_required": 18}
}

VAPE_JUICES = {
    "Mad - без никотина": {"price": 200, "strength": 0, "effects": {"unconscious_chance": 0, "duration": 0}},
    "Анархия Виноград лед 🍇": {"price": 300, "strength": 70, "effects": {"unconscious_chance": 40, "duration": 19}},
    "Skala - Банан Лёд🍌": {"price": 250, "strength": 30, "effects": {"unconscious_chance": 20, "duration": 8}},
    "Анархия - Лесные ягоды 🍇": {"price": 320, "strength": 85, "effects": {"unconscious_chance": 60, "duration": 19}},
    "Персиковый залив 🌊": {"price": 450, "strength": 90, "effects": {"unconscious_chance": 70, "duration": 20}},
    "Мятный Шок ❄️": {"price": 380, "strength": 50, "effects": {"unconscious_chance": 30, "duration": 7, "sore_throat": True}},
    "Охлаждающие яблоко🧊": {"price": 350, "strength": 40, "effects": {"unconscious_chance": 15, "duration": 5}},
    "Виноградный повал": {"price": 400, "strength": 55, "effects": {"unconscious_chance": 25, "duration": 10, "cough_chance": 50}}
}

SNUS_PRODUCTS = {
    "Mad - Банан Лёд🍌": {"price": 180, "strength": 500, "effects": {"unconscious_chance": 50, "duration": 15}},
    "Сибирский - Красная сирень": {"price": 220, "strength": 300, "effects": {"unconscious_chance": 30, "duration": 10}},
    "Corvus - Апельсин": {"price": 200, "strength": 350, "effects": {"unconscious_chance": 35, "duration": 12}}
}

CIGARETTES = {
    "Chapman с вишней 🍒": {"price": 200, "health_decrease": 12, "addiction_increase": 10},
    "Winston": {"price": 75, "health_decrease": 15, "addiction_increase": 12},
    "Парламент с кнопкой": {"price": 60, "health_decrease": 10, "addiction_increase": 8},
    "Marlboro Red": {"price": 90, "health_decrease": 18, "addiction_increase": 15},
    "L&M Blue": {"price": 70, "health_decrease": 12, "addiction_increase": 10}
}

HOOKAH_TOBACCOS = {
    "DarkSide - Со вкусом Голубика Лёд🫐": {"price": 300, "strength": 8, "health_decrease": 8},
    "Малина и лёд": {"price": 250, "strength": 4, "health_decrease": 5},
    "Лесные ягоды и лёд": {"price": 280, "strength": 8, "health_decrease": 8},
    "Ананас с кокосом": {"price": 270, "strength": 6, "health_decrease": 6}
}

DISPOSABLE_VAPES = {
    "Fillder❤️ - Вкус Redbull": {"price": 700, "puffs": 1000, "strength": 30, "effects": {"unconscious_chance": 15, "duration": 5}},
    "Magnum - Вкус Глинтвейн🍷": {"price": 250, "puffs": 400, "strength": 50, "effects": {"unconscious_chance": 25, "duration": 8, "nausea_chance": 30}},
    "HQD - Кулубника": {"price": 400, "puffs": 600, "strength": 25, "effects": {"unconscious_chance": 10, "duration": 3}}
}

ALCOHOL = {
    "Пиво": {"price": 120, "strength": 3, "effects": {"health_decrease": 5, "happiness_increase": 25}},
    "Вино": {"price": 300, "strength": 12, "effects": {"health_decrease": 10, "happiness_increase": 35}},
    "Водка": {"price": 500, "strength": 40, "effects": {"health_decrease": 20, "happiness_increase": 50, "unconscious_chance": 30}}
}

FOOD_ITEMS = {
    "🍔 Бургер": {"price": 150, "energy_restore": 20, "health_restore": 10},
    "🍕 Пицца": {"price": 200, "energy_restore": 25, "health_restore": 15},
    "🥗 Салат": {"price": 100, "energy_restore": 15, "health_restore": 20},
    "🍜 Суп": {"price": 80, "energy_restore": 10, "health_restore": 15},
    "☕ Кофе": {"price": 50, "energy_restore": 30, "health_restore": 5}
}

JOBS = {
    0: {"name": "Безработный", "salary": 0, "requirements": {}},
    1: {"name": "Разносчик газет", "salary": 100, "requirements": {"age": 14}},
    2: {"name": "Кассир", "salary": 200, "requirements": {"age": 16, "education": 2}},
    3: {"name": "Официант", "salary": 150, "requirements": {"age": 16}},
    4: {"name": "Курьер", "salary": 180, "requirements": {"age": 18, "has_car": True}},
    5: {"name": "Менеджер", "salary": 300, "requirements": {"age": 20, "education": 4}},
    6: {"name": "Программист", "salary": 500, "requirements": {"age": 18, "education": 5, "has_laptop": True}}
}

CRIMES = {
    "💰 Украсть кошелек": {"reward": 50, "risk": 20, "jail_chance": 10, "jail_time": 1},
    "🏪 Ограбить магазин": {"reward": 200, "risk": 40, "jail_chance": 30, "jail_time": 6},
    "🏠 Ограбить квартиру": {"reward": 300, "risk": 50, "jail_chance": 40, "jail_time": 12},
    "🚗 Угнать машину": {"reward": 500, "risk": 60, "jail_chance": 50, "jail_time": 24},
    "🕵️‍♂️ Мошенничество": {"reward": 150, "risk": 30, "jail_chance": 25, "jail_time": 4},
    "📱 Украсть телефон": {"reward": 100, "risk": 25, "jail_chance": 20, "jail_time": 2}
}

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
async def check_unconscious(user_id):
    player = get_player(user_id)
    if player and player['unconscious_until']:
        unconscious_until = datetime.fromisoformat(player['unconscious_until'])
        if datetime.now() < unconscious_until:
            seconds_left = int((unconscious_until - datetime.now()).total_seconds())
            return True, seconds_left
    return False, 0

async def check_jail(user_id):
    player = get_player(user_id)
    if player and player['in_jail'] and player['jail_until']:
        jail_until = datetime.fromisoformat(player['jail_until'])
        if datetime.now() < jail_until:
            hours_left = int((jail_until - datetime.now()).total_seconds() / 3600)
            return True, hours_left
        else:
            update_player(user_id, in_jail=0, jail_until=None)
    return False, 0

async def check_parents_angry(user_id):
    player = get_player(user_id)
    if player and player['parents_angry'] and player['parents_angry_until']:
        angry_until = datetime.fromisoformat(player['parents_angry_until'])
        if datetime.now() < angry_until:
            return True
        else:
            update_player(user_id, parents_angry=0, parents_angry_until=None)
    return False

def get_education_level_name(level):
    levels = {
        0: "Нет образования",
        1: "Начальная школа",
        2: "Средняя школа", 
        3: "Старшая школа",
        4: "Колледж",
        5: "Университет",
        6: "Магистратура"
    }
    return levels.get(level, "Неизвестно")

def get_job_level_name(level):
    levels = {
        0: "Безработный",
        1: "Разносчик газет",
        2: "Кассир",
        3: "Официант",
        4: "Курьер",
        5: "Менеджер",
        6: "Программист"
    }
    return levels.get(level, "Неизвестно")

def update_nicotine_addiction(user_id, increase=True, amount=10):
    player = get_player(user_id)
    if not player:
        return
    
    if increase:
        new_addiction = min(100, player['nicotine_addiction'] + amount)
    else:
        withdrawal_decrease = max(1, player['willpower'] // 20)
        new_addiction = max(0, player['nicotine_addiction'] - withdrawal_decrease)
        
        if new_addiction > 30:
            withdrawal_increase = random.randint(5, 10)
            new_withdrawal = min(100, player['withdrawal_level'] + withdrawal_increase)
            update_player(user_id, withdrawal_level=new_withdrawal)
    
    update_player(user_id, nicotine_addiction=new_addiction)

def calculate_health_risks(player):
    risks = {}
    smoking_years = player.get('smoking_years', 0)
    cigarettes_smoked = player.get('cigarettes_smoked', 0)
    
    if smoking_years >= 5:
        base_risk = min(70, (smoking_years - 4) * 10 + (cigarettes_smoked // 1000))
        risks['lung_cancer'] = base_risk
    else:
        risks['lung_cancer'] = 0
    
    risks['heart_disease'] = min(60, smoking_years * 8 + (cigarettes_smoked // 500))
    risks['dental_decay'] = min(80, smoking_years * 12 + (cigarettes_smoked // 200))
    risks['skin_damage'] = min(70, smoking_years * 10 + (cigarettes_smoked // 300))
    
    return risks

def update_smoking_stats(user_id, cigarettes_smoked=0):
    player = get_player(user_id)
    if not player:
        return
    
    new_cigarettes_smoked = player['cigarettes_smoked'] + cigarettes_smoked
    
    if cigarettes_smoked > 0 and random.random() < 0.3:
        update_player(user_id, smoking_years=player['smoking_years'] + 1)
    
    update_player(user_id, cigarettes_smoked=new_cigarettes_smoked)
    
    risks = calculate_health_risks(player)
    
    if not player['has_lung_cancer'] and random.random() * 100 < risks['lung_cancer']:
        update_player(user_id, has_lung_cancer=1)
    
    if not player['has_heart_disease'] and random.random() * 100 < risks['heart_disease']:
        update_player(user_id, has_heart_disease=1)
    
    dental_decrease = risks['dental_decay'] // 20
    skin_decrease = risks['skin_damage'] // 25
    
    update_player(
        user_id,
        dental_health=max(0, player['dental_health'] - dental_decrease),
        skin_health=max(0, player['skin_health'] - skin_decrease)
    )

# ОСНОВНЫЕ КОМАНДЫ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    in_jail, hours_left = await check_jail(user_id)
    if in_jail:
        await update.message.reply_text(f"🚔 Вы в тюрьме! Осталось {hours_left} часов.")
        return
    
    player = get_player(user_id)
    if not player:
        create_player(user_id, user.username)
        player = get_player(user_id)
        await update.message.reply_text(f"🎮 Добро пожаловать в Симулятор Жизни, {user.first_name}!")
    else:
        await update.message.reply_text(f"👋 С возвращением, {user.first_name}!")
    
    keyboard = [
        ["🏠 Статус", "💼 Работа", "🍽️ Еда"],
        ["🛒 Магазин", "🔫 Криминал", "📱 Телефоны"],
        ["🏫 Школа", "🚬 Курить/Вейпить/Снюс", "🍺 Выпить"],
        ["🏡 Квартира", "💕 Девушка", "👨‍👩‍👧‍👦 Семья"],
        ["🚗 Транспорт", "🏦 Банк", "⚖️ Полиция"],
        ["🎂 Отметить ДР", "📋 Паспорт", "🎯 Навыки"],
        ["🏥 Здоровье", "🧠 Психика", "💤 Сон"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    in_jail, hours_left = await check_jail(user_id)
    if in_jail:
        await update.message.reply_text(f"🚔 Вы в тюрьме! Осталось {hours_left} часов.")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    # Основная информация
    status_text = f"""
📊 ВАШ СТАТУС:

👤 {player['username']}
🎂 Возраст: {player['age']} лет
📋 Паспорт: {'✅ Есть' if player['has_id'] else '❌ Нет'}

💵 Деньги: {player['money']} руб.
💰 Сбережения: {player['savings']} руб.
💸 Долг: {player['loan_debt']} руб.

❤️ Здоровье: {player['health']}/100
😊 Счастье: {player['happiness']}/100
⚡ Энергия: {player['energy']}/100
💤 Сон: {player['sleep']}/100
🍖 Еда: {player['food']}/100

🎓 Образование: {get_education_level_name(player['education_level'])}
💼 Работа: {get_job_level_name(player['job_level'])}
🏡 Квартира: {'✅ Есть' if player['has_apartment'] else '❌ Нет'}
🚗 Машина: {'✅ ' + player['car_type'] if player['has_car'] else '❌ Нет'}

🚬 Сигареты: {player['cigarettes']} шт.
💊 Зависимость: {player['nicotine_addiction']}%
🍺 Пиво: {player['beer_count']} шт.
👥 Репутация: {player['reputation']}
📝 Судимости: {player['criminal_record']}
"""
    
    # Информация о вейпе
    if player['vape_type']:
        status_text += f"\n🔋 Вейп: {player['vape_type']}"
        status_text += f"\n💧 Жидкость: {player['juice_flavor']} ({player['vape_juice']} мл)"
        status_text += f"\n🔋 Батарея: {player['vape_battery']}%"
        status_text += f"\n📊 Тяги картриджа: {player['current_cartridge_puffs']}/100"
    
    # Информация об одноразке
    if player['disposable_vape_type']:
        status_text += f"\n💨 Одноразка: {player['disposable_vape_type']} ({player['disposable_vape_puffs']} тяжек)"
    
    # Навыки
    status_text += f"""
💪 Навыки:
Сила воли: {player['willpower']}/100
Интеллект: {player['intelligence']}/100  
Харизма: {player['charisma']}/100
Выносливость: {player['endurance']}/100
"""
    
    # Психическое здоровье
    status_text += f"""
🧠 Психическое здоровье:
Стресс: {player['stress']}/100
Депрессия: {player['depression']}/100
Тревожность: {player['anxiety']}/100
"""
    
    # Детали здоровья
    status_text += f"""
🏥 Детали здоровья:
Зубы: {player['dental_health']}/100
Кожа: {player['skin_health']}/100
"""
    
    if player['has_lung_cancer']:
        status_text += "\n⚠️ РАК ЛЕГКИХ"
    if player['has_heart_disease']:
        status_text += "\n💔 БОЛЕЗНИ СЕРДЦА"
    if player['has_alcohol_poisoning']:
        status_text += "\n🤮 АЛКОГОЛЬНОЕ ОТРАВЛЕНИЕ"
    
    # Семья и отношения
    if player['has_girlfriend']:
        status_text += f"\n💕 Девушка: {player['girlfriend_happiness']}/100 счастья"
    if player['has_family']:
        status_text += f"\n👨‍👩‍👧‍👦 Семья: {player['family_happiness']}/100 счастья"
        if player['children'] > 0:
            status_text += f"\n👶 Дети: {player['children']}"
    
    status_text += f"\n👥 Друзья: {player['friends_count']} человек"
    
    # Предупреждения
    warnings = []
    if player['food'] <= 0:
        warnings.append("⚠️ Закончилась еда! Здоровье уменьшается!")
    if player['health'] <= 20:
        warnings.append("💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно поешьте!")
    if player['energy'] <= 20:
        warnings.append("😴 Низкая энергия! Нужно поспать!")
    if player['sleep'] <= 20:
        warnings.append("🛌 Сильная усталость! Нужно поспать!")
    if player['happiness'] <= 20:
        warnings.append("😔 Очень низкое счастье!")
    if player['withdrawal_level'] > 50:
        warnings.append("😫 Сильная никотиновая ломка!")
    
    if warnings:
        status_text += "\n\n" + "\n".join(warnings)
    
    await update.message.reply_text(status_text)

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    in_jail, hours_left = await check_jail(user_id)
    if in_jail:
        await update.message.reply_text(f"🚔 Вы в тюрьме! Осталось {hours_left} часов.")
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    # Проверка cooldown
    if player['last_work_time']:
        last_work = datetime.fromisoformat(player['last_work_time'])
        if datetime.now() - last_work < timedelta(minutes=5):
            await update.message.reply_text("⏳ Вы уже работали недавно! Подождите 5 минут.")
            return
    
    # Проверка энергии
    if player['energy'] < 20:
        await update.message.reply_text("😴 Слишком устали для работы! Отдохните.")
        return
    
    job_info = JOBS.get(player['job_level'], {"salary": 0})
    
    # Заработок в зависимости от уровня работы
    earnings = job_info["salary"]
    
    # Бонус за образование
    if player['education_level'] >= 4:
        earnings = int(earnings * 1.5)
    
    update_player(
        user_id,
        money=player['money'] + earnings,
        energy=max(0, player['energy'] - 15),
        last_work_time=datetime.now().isoformat()
    )
    
    await update.message.reply_text(f"💼 Вы поработали как {job_info['name']} и заработали {earnings} руб.!\n⚡ Энергия: -15")

async def eat_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    keyboard = []
    for food_name, food_info in FOOD_ITEMS.items():
        keyboard.append([InlineKeyboardButton(f"{food_name} - {food_info['price']} руб.", callback_data=f"eat_{food_name}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍽️ ВЫБЕРИТЕ ЕДУ:", reply_markup=reply_markup)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚬 Сигареты", callback_data="shop_cigarettes")],
        [InlineKeyboardButton("🔋 Вейпы", callback_data="shop_vapes")],
        [InlineKeyboardButton("💧 Жидкости для вейпа", callback_data="shop_juices")],
        [InlineKeyboardButton("📦 Снюс", callback_data="shop_snus")],
        [InlineKeyboardButton("💨 Одноразки", callback_data="shop_disposable")],
        [InlineKeyboardButton("🍺 Алкоголь", callback_data="shop_alcohol")],
        [InlineKeyboardButton("🍽️ Еда", callback_data="shop_food")],
        [InlineKeyboardButton("🚪 Ларёк (для несовершеннолетних)", callback_data="shop_booth")],
        [InlineKeyboardButton("🏪 NurikVape (вейп-шоп)", callback_data="shop_nurikvape")],
        [InlineKeyboardButton("💨 Кальянная дяди", callback_data="hookah_bar")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🛒 ВЫБЕРИТЕ МАГАЗИН:", reply_markup=reply_markup)

# ОБРАБОТЧИКИ ПОКУПОК И ДРУГИЕ ФУНКЦИИ
async def handle_shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    player = get_player(user_id)
    
    if query.data == "shop_cigarettes":
        text = "🚬 СИГАРЕТЫ:\n\n"
        for name, info in CIGARETTES.items():
            text += f"{name} - {info['price']} руб.\n"
        
        keyboard = []
        for name in CIGARETTES.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_cigarette_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_vapes":
        text = "🔋 ВЕЙП-УСТРОЙСТВА:\n\n"
        for name, info in VAPE_DEVICES.items():
            age_req = "🔞" if info["age_required"] == 18 else ""
            text += f"{name} - {info['price']} руб. {age_req}\n"
        
        keyboard = []
        for name in VAPE_DEVICES.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_vape_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_juices":
        text = "💧 ЖИДКОСТИ ДЛЯ ВЕЙПА:\n\n"
        for name, info in VAPE_JUICES.items():
            text += f"{name} - {info['price']} руб. ({info['strength']} мг)\n"
        
        keyboard = []
        for name in VAPE_JUICES.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_juice_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_snus":
        text = "📦 СНЮС:\n\n"
        for name, info in SNUS_PRODUCTS.items():
            text += f"{name} - {info['price']} руб. ({info['strength']} мг)\n"
        
        keyboard = []
        for name in SNUS_PRODUCTS.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_snus_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_disposable":
        text = "💨 ОДНОРАЗОВЫЕ ВЕЙПЫ:\n\n"
        for name, info in DISPOSABLE_VAPES.items():
            text += f"{name} - {info['price']} руб. ({info['puffs']} тяжек, {info['strength']} мг)\n"
        
        keyboard = []
        for name in DISPOSABLE_VAPES.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_disposable_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_alcohol":
        text = "🍺 АЛКОГОЛЬ:\n\n"
        for name, info in ALCOHOL.items():
            age_req = "🔞" if info["strength"] > 10 else ""
            text += f"{name} - {info['price']} руб. {age_req}\n"
        
        keyboard = []
        for name in ALCOHOL.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_alcohol_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_food":
        text = "🍽️ ЕДА:\n\n"
        for name, info in FOOD_ITEMS.items():
            text += f"{name} - {info['price']} руб. (+{info['energy_restore']} энергии)\n"
        
        keyboard = []
        for name in FOOD_ITEMS.keys():
            keyboard.append([InlineKeyboardButton(f"Купить {name}", callback_data=f"buy_food_{name}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "shop_booth":
        await booth_shop(query)
    
    elif query.data == "shop_nurikvape":
        await nurikvape_shop(query)
    
    elif query.data == "hookah_bar":
        await hookah_bar_menu(query)
    
    elif query.data.startswith("eat_"):
        await handle_eat(query)
    
    elif query.data.startswith("buy_"):
        await handle_purchase(query)
    
    elif query.data == "back_to_shop":
        await shop(query._bot, context)
    
    elif query.data == "back_to_main":
        await start(query._bot, context)

async def booth_shop(query):
    text = """🚪 ЛАРЁК (для своих)

⚠️ Товары могут быть бракованными!
Но продают без паспорта!

💨 Одноразки:
• Fillder❤️ (брак) - 500 руб. (может взорваться!)
• Magnum (брак) - 150 руб. (может быть с гарью)

🍺 Пиво - 120 руб.
"""
    
    keyboard = [
        [InlineKeyboardButton("Купить Fillder❤️ (брак)", callback_data="buy_booth_fillder")],
        [InlineKeyboardButton("Купить Magnum (брак)", callback_data="buy_booth_magnum")],
        [InlineKeyboardButton("Купить Пиво", callback_data="buy_booth_beer")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def nurikvape_shop(query):
    text = """🏪 NURIKVAPE

🔋 Вейп-устройства:
• Charin Baby синий - 850 руб.
• Boost 2 черный - 1000 руб. 
• Hero 3 белый - 950 руб.

💧 Жидкости:
• Персиковый залив 🌊 (90 мг) - 450 руб.
• Мятный Шок ❄️ (50 мг) - 380 руб.
• Охлаждающие яблоко🧊 (40 мг) - 350 руб.
• Виноградный повал (55 мг) - 400 руб.
"""
    
    keyboard = [
        [InlineKeyboardButton("Купить Charin Baby", callback_data="buy_vape_Charin Baby синий")],
        [InlineKeyboardButton("Купить Boost 2", callback_data="buy_vape_Boost 2 черный")],
        [InlineKeyboardButton("Купить Hero 3", callback_data="buy_vape_Hero 3 белый")],
        [InlineKeyboardButton("💧 Жидкости", callback_data="nurik_juices")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def hookah_bar_menu(query):
    user_id = query.from_user.id
    player = get_player(user_id)
    
    text = """💨 КАЛЬЯННАЯ ДЯДИ

Дядя разрешает курить кальян бесплатно!
Выбери табак:

• Малина и лёд (крепкость 4/10)
• Лесные ягоды и лёд (крепкость 8/10)
"""
    
    keyboard = [
        [InlineKeyboardButton("🚬 Покурить Малина и лёд", callback_data="hookah_raspberry")],
        [InlineKeyboardButton("🚬 Покурить Лесные ягоды", callback_data="hookah_berries")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_purchase(query):
    user_id = query.from_user.id
    player = get_player(user_id)
    data = query.data
    
    if data.startswith("buy_cigarette_"):
        cig_name = data.replace("buy_cigarette_", "")
        if cig_name in CIGARETTES:
            info = CIGARETTES[cig_name]
            
            if player['money'] < info['price']:
                await query.answer("❌ Недостаточно денег!", show_alert=True)
                return
            
            current_cigarettes = player.get('cigarettes', 0)
            update_player(user_id, money=player['money'] - info['price'], cigarettes=current_cigarettes + 1)
            
            await query.answer(f"✅ Куплены {cig_name}!", show_alert=True)
            await query.edit_message_text(f"✅ Вы купили {cig_name} за {info['price']} руб.")
    
    elif data.startswith("buy_vape_"):
        vape_name = data.replace("buy_vape_", "")
        if vape_name in VAPE_DEVICES:
            info = VAPE_DEVICES[vape_name]
            
            if info["age_required"] == 18 and (player['age'] < 18 or not player['has_id']):
                if player['age'] >= 14 and random.random() < 0.3:
                    pass
                else:
                    await query.answer("❌ Тебе нет 18 лет или нет паспорта!", show_alert=True)
                    return
            
            if player['money'] < info['price']:
                await query.answer("❌ Недостаточно денег!", show_alert=True)
                return
            
            update_player(user_id, money=player['money'] - info['price'], vape_type=vape_name, vape_battery=100)
            await query.answer(f"✅ Куплен {vape_name}!", show_alert=True)
            await query.edit_message_text(f"✅ Вы купили {vape_name} за {info['price']} руб.")
    
    elif data.startswith("buy_juice_"):
        juice_name = data.replace("buy_juice_", "")
        if juice_name in VAPE_JUICES:
            info = VAPE_JUICES[juice_name]
            
            if player['money'] < info['price']:
                await query.answer("❌ Недостаточно денег!", show_alert=True)
                return
            
            current_juice = player.get('vape_juice', 0)
            update_player(
                user_id, 
                money=player['money'] - info['price'], 
                vape_juice=current_juice + 10,
                juice_flavor=juice_name
            )
            
            await query.answer(f"✅ Куплена жидкость {juice_name}!", show_alert=True)
            await query.edit_message_text(f"✅ Вы купили {juice_name} за {info['price']} руб.")
    
    elif data == "buy_booth_fillder":
        if player['money'] < 500:
            await query.answer("❌ Недостаточно денег!", show_alert=True)
            return
        
        is_defective = random.random() < 0.4
        
        update_player(
            user_id, 
            money=player['money'] - 500,
            disposable_vape_type="Fillder❤️ (брак)" if is_defective else "Fillder❤️",
            disposable_vape_puffs=1000
        )
        
        if is_defective:
            await query.answer("⚠️ Куплен бракованный Fillder! Может взорваться!", show_alert=True)
        else:
            await query.answer("✅ Куплен Fillder!", show_alert=True)
        
        await query.edit_message_text(f"✅ Вы купили Fillder❤️ за 500 руб." + (" ⚠️ БРАК!" if is_defective else ""))
    
    elif data == "buy_booth_beer":
        if player['money'] < 120:
            await query.answer("❌ Недостаточно денег!", show_alert=True)
            return
        
        update_player(
            user_id,
            money=player['money'] - 120,
            beer_count=player['beer_count'] + 1
        )
        
        await query.answer("✅ Куплено пиво!", show_alert=True)
        await query.edit_message_text("✅ Вы купили пиво за 120 руб.")
    
    elif data.startswith("buy_alcohol_"):
        alcohol_name = data.replace("buy_alcohol_", "")
        if alcohol_name in ALCOHOL:
            info = ALCOHOL[alcohol_name]
            
            if player['money'] < info['price']:
                await query.answer("❌ Недостаточно денег!", show_alert=True)
                return
            
            if info["strength"] > 10 and player['age'] < 18:
                await query.answer("❌ Тебе нет 18 лет!", show_alert=True)
                return
            
            update_player(
                user_id,
                money=player['money'] - info['price'],
                beer_count=player['beer_count'] + 1
            )
            
            await query.answer(f"✅ Куплено {alcohol_name}!", show_alert=True)
            await query.edit_message_text(f"✅ Вы купили {alcohol_name} за {info['price']} руб.")
    
    elif data.startswith("buy_food_"):
        food_name = data.replace("buy_food_", "")
        if food_name in FOOD_ITEMS:
            info = FOOD_ITEMS[food_name]
            
            if player['money'] < info['price']:
                await query.answer("❌ Недостаточно денег!", show_alert=True)
                return
            
            update_player(
                user_id,
                money=player['money'] - info['price'],
                food=min(100, player['food'] + 20),
                energy=min(100, player['energy'] + info['energy_restore']),
                health=min(100, player['health'] + info['health_restore'])
            )
            
            await query.answer(f"✅ Куплено {food_name}!", show_alert=True)
            await query.edit_message_text(f"✅ Вы купили {food_name} за {info['price']} руб.")
    
    elif data == "hookah_raspberry":
        await smoke_hookah_tobacco(query, "Малина и лёд", 4)
    
    elif data == "hookah_berries":
        await smoke_hookah_tobacco(query, "Лесные ягоды и лёд", 8)

async def handle_eat(query):
    user_id = query.from_user.id
    player = get_player(user_id)
    data = query.data
    
    food_name = data.replace("eat_", "")
    if food_name in FOOD_ITEMS:
        info = FOOD_ITEMS[food_name]
        
        if player['money'] < info['price']:
            await query.answer("❌ Недостаточно денег!", show_alert=True)
            return
        
        update_player(
            user_id,
            money=player['money'] - info['price'],
            food=min(100, player['food'] + 20),
            energy=min(100, player['energy'] + info['energy_restore']),
            health=min(100, player['health'] + info['health_restore']),
            last_meal_time=datetime.now().isoformat()
        )
        
        await query.answer(f"✅ Съедено {food_name}!", show_alert=True)
        await query.edit_message_text(f"✅ Вы съели {food_name} за {info['price']} руб.\n+{info['energy_restore']} энергии, +20 сытости")

async def smoke_hookah_tobacco(query, tobacco_name, strength):
    user_id = query.from_user.id
    player = get_player(user_id)
    
    health_decrease = strength * 2
    happiness_increase = strength * 3
    
    unconscious_chance = strength * 5
    if random.random() * 100 < unconscious_chance:
        unconscious_until = datetime.now() + timedelta(seconds=10)
        update_player(user_id, unconscious_until=unconscious_until.isoformat())
        await query.edit_message_text(f"💨 Вы покурили кальян с табаком '{tobacco_name}'...\n\n💫 Потерял сознание от крепости! Придешь в себя через 10 секунд.")
        return
    
    update_player(
        user_id,
        health=max(0, player['health'] - health_decrease),
        happiness=min(100, player['happiness'] + happiness_increase)
    )
    
    await query.edit_message_text(
        f"💨 Вы покурили кальян с табаком '{tobacco_name}'\n\n"
        f"❤️ Здоровье: -{health_decrease}\n"
        f"😊 Счастье: +{happiness_increase}\n"
        f"💪 Крепость: {strength}/10"
    )

async def drink_beer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['beer_count'] <= 0:
        await update.message.reply_text("❌ У вас нет алкоголя! Купите в магазине.")
        return
    
    health_decrease = 5
    happiness_increase = 25
    
    poison_chance = 10
    if random.random() * 100 < poison_chance:
        update_player(
            user_id,
            has_alcohol_poisoning=1,
            health=max(0, player['health'] - 20),
            beer_count=player['beer_count'] - 1,
            last_drink_time=datetime.now().isoformat()
        )
        await update.message.reply_text("🤮 Алкогольное отравление! Здоровье -20")
        return
    
    update_player(
        user_id,
        beer_count=player['beer_count'] - 1,
        health=max(0, player['health'] - health_decrease),
        happiness=min(100, player['happiness'] + happiness_increase),
        last_drink_time=datetime.now().isoformat()
    )
    
    await update.message.reply_text(
        f"🍻 Вы выпили пиво...\n\n"
        f"❤️ Здоровье: -{health_decrease}\n"
        f"😊 Счастье: +{happiness_increase}\n"
        f"🍺 Осталось пива: {player['beer_count'] - 1}"
    )

async def vape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['vape_type']:
        await update.message.reply_text("❌ У вас нет вейпа! Купите в магазине.")
        return
    
    if player['vape_juice'] <= 0:
        await update.message.reply_text("❌ Закончилась жидкость! Купите в магазине.")
        return
    
    if player['vape_battery'] <= 0:
        await update.message.reply_text("❌ Сел аккумулятор! Зарядите вейп.")
        return
    
    if player['current_cartridge_puffs'] >= 100:
        await update.message.reply_text("❌ Картридж изношен! Замените его (купите новую жидкость).")
        return
    
    juice_info = VAPE_JUICES.get(player['juice_flavor'], {"strength": 20, "effects": {}})
    strength = juice_info["strength"]
    effects = juice_info["effects"]
    
    health_decrease = max(3, strength // 10)
    happiness_increase = min(25, strength // 2)
    
    effect_text = ""
    if random.random() * 100 < effects.get("unconscious_chance", 0):
        duration = effects.get("duration", 5)
        unconscious_until = datetime.now() + timedelta(seconds=duration)
        update_player(user_id, unconscious_until=unconscious_until.isoformat())
        await update.message.reply_text(f"💨 Вы покурили вейп...\n\n💫 Потерял сознание от крепости! Придешь в себя через {duration} секунд.")
        return
    
    if effects.get("sore_throat", False) and random.random() < 0.3:
        effect_text += "\n🤢 Болит горло от крепости!"
        health_decrease += 5
    
    if effects.get("cough_chance", 0) > 0 and random.random() * 100 < effects["cough_chance"]:
        effect_text += "\n😷 Сильный кашель!"
        health_decrease += 3
    
    update_player(
        user_id,
        vape_juice=player['vape_juice'] - 1,
        vape_battery=player['vape_battery'] - 5,
        health=max(0, player['health'] - health_decrease),
        happiness=min(100, player['happiness'] + happiness_increase),
        current_cartridge_puffs=player['current_cartridge_puffs'] + 1,
        vape_puffs_count=player['vape_puffs_count'] + 1,
        last_smoke_time=datetime.now().isoformat()
    )
    
    update_nicotine_addiction(user_id, increase=True, amount=strength//10)
    
    await update.message.reply_text(
        f"💨 Вы покурили вейп ({player['juice_flavor']})...\n\n"
        f"❤️ Здоровье: -{health_decrease}\n"
        f"😊 Счастье: +{happiness_increase}\n"
        f"💧 Жидкости: {player['vape_juice'] - 1} мл\n"
        f"🔋 Батарея: {player['vape_battery'] - 5}%\n"
        f"📊 Тяги картриджа: {player['current_cartridge_puffs'] + 1}/100{effect_text}"
    )

async def smoke_cigarette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['cigarettes'] <= 0:
        await update.message.reply_text("❌ У вас нет сигарет! Купите в магазине.")
        return
    
    # Определяем тип сигарет для расчета эффектов
    cig_type = "Winston"  # По умолчанию
    cig_info = CIGARETTES.get(cig_type, {"health_decrease": 15, "addiction_increase": 10})
    
    health_decrease = cig_info["health_decrease"]
    happiness_increase = 20
    addiction_increase = cig_info["addiction_increase"]
    
    update_player(
        user_id,
        cigarettes=player['cigarettes'] - 1,
        health=max(0, player['health'] - health_decrease),
        happiness=min(100, player['happiness'] + happiness_increase),
        last_smoke_time=datetime.now().isoformat()
    )
    
    update_nicotine_addiction(user_id, increase=True, amount=addiction_increase)
    update_smoking_stats(user_id, cigarettes_smoked=1)
    
    await update.message.reply_text(
        f"🚬 Вы выкурили сигарету...\n\n"
        f"❤️ Здоровье: -{health_decrease}\n"
        f"😊 Счастье: +{happiness_increase}\n"
        f"📦 Сигарет осталось: {player['cigarettes'] - 1}\n"
        f"💊 Зависимость: +{addiction_increase}%"
    )

async def smoke_vape_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚬 Выкурить сигарету", "🍒 Выкурить Чапман"],
        ["💨 Покурить вейп", "🚬 Покурить одноразку"],
        ["📦 Закинуть снюс", "🍺 Выпить пиво"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🚬 ВЫБЕРИТЕ ЧТО ПОКУРИТЬ:", reply_markup=reply_markup)

async def school_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📚 Учиться", "🚬 Сходить в туалет покурить"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🏫 ШКОЛА:", reply_markup=reply_markup)

async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['last_school_time']:
        last_study = datetime.fromisoformat(player['last_school_time'])
        if datetime.now() - last_study < timedelta(minutes=10):
            await update.message.reply_text("⏳ Вы уже учились недавно! Подождите 10 минут.")
            return
    
    if player['energy'] < 30:
        await update.message.reply_text("😴 Слишком устали для учебы! Отдохните.")
        return
    
    education_increase = 1
    if player['education_level'] < 6:
        update_player(
            user_id,
            education_level=player['education_level'] + education_increase,
            energy=max(0, player['energy'] - 20),
            intelligence=min(100, player['intelligence'] + 2),
            last_school_time=datetime.now().isoformat()
        )
        await update.message.reply_text(f"📚 Вы поучились! Уровень образования: {get_education_level_name(player['education_level'] + 1)}\n⚡ Энергия: -20")
    else:
        await update.message.reply_text("🎓 Вы уже достигли максимального уровня образования!")

async def school_smoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['cigarettes'] <= 0 and not player['vape_type']:
        await update.message.reply_text("❌ У вас нечего курить!")
        return
    
    caught_chance = 30
    if random.random() * 100 < caught_chance:
        update_player(
            user_id,
            parents_angry=1,
            parents_angry_until=(datetime.now() + timedelta(hours=2)).isoformat(),
            reputation=max(-10, player['reputation'] - 5)
        )
        await update.message.reply_text("🚨 Вас поймали в туалете с сигаретой! Родители злы на вас 2 часа! Репутация -5")
        return
    
    await update.message.reply_text("🚬 Вы успешно покурили в туалете и не попались!")

async def crime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    in_jail, hours_left = await check_jail(user_id)
    if in_jail:
        await update.message.reply_text(f"🚔 Вы в тюрьме! Осталось {hours_left} часов.")
        return
    
    keyboard = []
    for crime_name, crime_info in CRIMES.items():
        keyboard.append([f"{crime_name} (💰{crime_info['reward']} руб.)"])
    keyboard.append(["⬅️ Назад"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🔫 ВЫБЕРИТЕ ПРЕСТУПЛЕНИЕ:", reply_markup=reply_markup)

async def commit_crime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    in_jail, hours_left = await check_jail(user_id)
    if in_jail:
        await update.message.reply_text(f"🚔 Вы в тюрьме! Осталось {hours_left} часов.")
        return
    
    crime_name = text.split(' (')[0]  # Убираем часть с деньгами
    crime_info = CRIMES.get(crime_name)
    
    if not crime_info:
        await update.message.reply_text("❌ Неизвестное преступление!")
        return
    
    player = get_player(user_id)
    
    # Проверка cooldown
    if player['last_crime_time']:
        last_crime = datetime.fromisoformat(player['last_crime_time'])
        if datetime.now() - last_crime < timedelta(minutes=30):
            await update.message.reply_text("⏳ Вы уже совершали преступление недавно! Подождите 30 минут.")
            return
    
    # Шанс успеха
    success_chance = 100 - crime_info['risk']
    if random.random() * 100 < success_chance:
        # Успех
        reward = crime_info['reward']
        update_player(
            user_id,
            money=player['money'] + reward,
            last_crime_time=datetime.now().isoformat(),
            criminal_record=player['criminal_record'] + 1,
            reputation=max(-100, player['reputation'] - 3)
        )
        await update.message.reply_text(f"✅ Преступление удалось! Вы получили {reward} руб.\n📝 Судимость +1, Репутация -3")
    else:
        # Провал
        if random.random() * 100 < crime_info['jail_chance']:
            # Попадание в тюрьму
            jail_time = crime_info['jail_time']
            jail_until = datetime.now() + timedelta(hours=jail_time)
            update_player(
                user_id,
                in_jail=1,
                jail_until=jail_until.isoformat(),
                criminal_record=player['criminal_record'] + 1,
                reputation=max(-100, player['reputation'] - 10)
            )
            await update.message.reply_text(f"🚔 Вас поймали! Тюрьма на {jail_time} часов.\n📝 Судимость +1, Репутация -10")
        else:
            # Просто провал
            update_player(
                user_id,
                last_crime_time=datetime.now().isoformat(),
                reputation=max(-100, player['reputation'] - 2)
            )
            await update.message.reply_text("❌ Преступление провалилось, но вас не поймали!\n📉 Репутация -2")

async def celebrate_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['age'] >= 100:
        await update.message.reply_text("🎉 Вы достигли максимального возраста!")
        return
    
    update_player(
        user_id, 
        age=player['age'] + 1,
        happiness=min(100, player['happiness'] + 10),
        money=player['money'] + 100  # Подарок на день рождения
    )
    await update.message.reply_text(f"🎂 С днем рождения! Теперь вам {player['age'] + 1} лет!\n💵 Получено 100 руб. в подарок!")

async def get_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['age'] < 14:
        await update.message.reply_text("❌ Вам нет 14 лет! Паспорт выдают с 14 лет.")
        return
    
    if player['has_id']:
        await update.message.reply_text("✅ У вас уже есть паспорт!")
        return
    
    update_player(user_id, has_id=1)
    await update.message.reply_text("📋 Вы получили паспорт! Теперь можете покупать вейпы и крепкий алкоголь.")

async def sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['sleep'] >= 80:
        await update.message.reply_text("😴 Вы не хотите спать!")
        return
    
    sleep_restore = random.randint(30, 50)
    energy_restore = random.randint(20, 40)
    
    update_player(
        user_id,
        sleep=min(100, player['sleep'] + sleep_restore),
        energy=min(100, player['energy'] + energy_restore),
        health=min(100, player['health'] + 5)
    )
    
    await update.message.reply_text(
        f"💤 Вы поспали...\n\n"
        f"💤 Сон: +{sleep_restore}\n"
        f"⚡ Энергия: +{energy_restore}\n"
        f"❤️ Здоровье: +5"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_unconscious, seconds_left = await check_unconscious(user_id)
    if is_unconscious:
        await update.message.reply_text(f"💫 Вы без сознания! Подождите {seconds_left} секунд...")
        return
    
    in_jail, hours_left = await check_jail(user_id)
    if in_jail:
        await update.message.reply_text(f"🚔 Вы в тюрьме! Осталось {hours_left} часов.")
        return
    
    text = update.message.text
    
    if text == "🏠 Статус":
        await show_status(update, context)
    elif text == "💼 Работа":
        await work(update, context)
    elif text == "🍽️ Еда":
        await eat_food(update, context)
    elif text == "🛒 Магазин":
        await shop(update, context)
    elif text == "🔫 Криминал":
        await crime_menu(update, context)
    elif text in CRIMES:
        await commit_crime(update, context)
    elif text == "🏫 Школа":
        await school_menu(update, context)
    elif text == "📚 Учиться":
        await study(update, context)
    elif text == "🚬 Сходить в туалет покурить":
        await school_smoke(update, context)
    elif text == "🚬 Курить/Вейпить/Снюс":
        await smoke_vape_menu(update, context)
    elif text == "🚬 Выкурить сигарету":
        await smoke_cigarette(update, context)
    elif text == "💨 Покурить вейп":
        await vape(update, context)
    elif text == "🍺 Выпить":
        await drink_beer(update, context)
    elif text == "🎂 Отметить ДР":
        await celebrate_birthday(update, context)
    elif text == "📋 Паспорт":
        await get_passport(update, context)
    elif text == "💤 Сон":
        await sleep(update, context)
    elif text in ["⬅️ Назад", "🏠 Домой"]:
        await start(update, context)
    else:
        await update.message.reply_text("Используйте кнопки меню для управления игрой!")

def main():
    init_db()
    upgrade_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern=".*"))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
