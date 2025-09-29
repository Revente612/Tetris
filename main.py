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
            unconscious_until TEXT
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
            'vape_battery': 'ALTER TABLE players ADD COLUMN vape_battery INTEGER DEFAULT 0',
            'has_hookah': 'ALTER TABLE players ADD COLUMN has_hookah INTEGER DEFAULT 0',
            'hookah_coals': 'ALTER TABLE players ADD COLUMN hookah_coals INTEGER DEFAULT 0',
            'hookah_tobacco': 'ALTER TABLE players ADD COLUMN hookah_tobacco TEXT DEFAULT NULL',
            'hookah_tobacco_amount': 'ALTER TABLE players ADD COLUMN hookah_tobacco_amount INTEGER DEFAULT 0',
            'has_burner': 'ALTER TABLE players ADD COLUMN has_burner INTEGER DEFAULT 0',
            'disposable_vape_type': 'ALTER TABLE players ADD COLUMN disposable_vape_type TEXT DEFAULT NULL',
            'disposable_vape_puffs': 'ALTER TABLE players ADD COLUMN disposable_vape_puffs INTEGER DEFAULT 0',
            'chapman_cigarettes': 'ALTER TABLE players ADD COLUMN chapman_cigarettes INTEGER DEFAULT 0',
            'on_probation': 'ALTER TABLE players ADD COLUMN on_probation INTEGER DEFAULT 0',
            'probation_until': 'ALTER TABLE players ADD COLUMN probation_until TEXT',
            'has_tea_leaf': 'ALTER TABLE players ADD COLUMN has_tea_leaf INTEGER DEFAULT 0',
            'unconscious_until': 'ALTER TABLE players ADD COLUMN unconscious_until TEXT'
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
                  'on_probation', 'probation_until', 'created_at', 'has_tea_leaf', 'unconscious_until']
        
        player_dict = {}
        for i, column in enumerate(columns):
            if i < len(player):
                player_dict[column] = player[i]
            else:
                player_dict[column] = None
        
        # Установка значений по умолчанию
        player_dict.setdefault('health', 100)
        player_dict.setdefault('happiness', 100)
        player_dict.setdefault('food', 100)
        player_dict.setdefault('age', 16)
        player_dict.setdefault('education_level', 0)
        player_dict.setdefault('job_level', 0)
        player_dict.setdefault('cigarettes', 0)
        player_dict.setdefault('vape_juice', 0)
        player_dict.setdefault('snus_packs', 0)
        player_dict.setdefault('snus_strength', 0)
        player_dict.setdefault('girlfriend_happiness', 0)
        player_dict.setdefault('iqos_sticks', 0)
        player_dict.setdefault('iqos_battery', 0)
        player_dict.setdefault('vape_battery', 0)
        player_dict.setdefault('has_hookah', 0)
        player_dict.setdefault('hookah_coals', 0)
        player_dict.setdefault('hookah_tobacco_amount', 0)
        player_dict.setdefault('has_burner', 0)
        player_dict.setdefault('disposable_vape_puffs', 0)
        player_dict.setdefault('chapman_cigarettes', 0)
        player_dict.setdefault('on_probation', 0)
        player_dict.setdefault('has_tea_leaf', 0)
        player_dict.setdefault('unconscious_until', None)
        
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

def reset_player(user_id, username):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    try:
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
                vape_battery = 0,
                has_hookah = 0,
                hookah_coals = 0,
                hookah_tobacco = NULL,
                hookah_tobacco_amount = 0,
                has_burner = 0,
                disposable_vape_type = NULL,
                disposable_vape_puffs = 0,
                chapman_cigarettes = 0,
                on_probation = 0,
                probation_until = NULL,
                has_tea_leaf = 0,
                unconscious_until = NULL
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при сбросе игрока: {e}")
    finally:
        conn.close()

async def check_unconscious(user_id):
    """Проверяет, находится ли игрок в бессознательном состоянии"""
    player = get_player(user_id)
    if player['unconscious_until']:
        unconscious_until = datetime.fromisoformat(player['unconscious_until'])
        if datetime.now() < unconscious_until:
            time_left = unconscious_until - datetime.now()
            seconds_left = int(time_left.total_seconds())
            return True, seconds_left
        else:
            update_player(user_id, unconscious_until=None)
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
        ["🏠 Статус", "💼 Работа"],
        ["🛒 Магазин", "🔫 Криминал"],
        ["🏫 Школа", "🚬 Курить/Вейпить/Снюс"],
        ["🏡 Квартира", "💕 Девушка"],
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
            iqos_info += f"\n📦 Стики: {player['iqos_sticks']} шт."
    
    disposable_info = ""
    if player['disposable_vape_type']:
        disposable_info = f"\n🚬 Одноразка: {player['disposable_vape_type']} ({player['disposable_vape_puffs']} тяг)"
    
    chapman_info = ""
    if player['chapman_cigarettes'] > 0:
        chapman_info = f"\n🍒 Чапман: {player['chapman_cigarettes']} шт."
    
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
        snus_info = f"\n📦 Снюс: {player['snus_packs']} пачек ({player['snus_strength']} мг)"
    
    girlfriend_info = ""
    if player['has_girlfriend']:
        girlfriend_info = f"\n💕 Девушка: счастье {player['girlfriend_happiness']}/100"
    
    tech_info = ""
    if player['has_laptop']:
        tech_info += "\n💻 Ноутбук: ✅ Есть"
    if player['has_vpn']:
        tech_info += "\n🛡️ VPN: ✅ Есть"
    
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
{chapman_info}
{vape_info}
{disposable_info}
{iqos_info}
{hookah_info}
{snus_info}
{tea_info}
{girlfriend_info}
{probation_info}
{unconscious_info}

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
        8: "Работник ПВЗ (3250 руб.)"
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
    
    # НЕТ КД НА РАБОТУ - можно работать без ограничений
    earnings = [0, 50, 100, 200, 800, 500, 1000, 600, 3250][player['job_level']]
    new_money = player['money'] + earnings
    
    update_player(
        user_id, 
        money=new_money, 
        last_work_time=datetime.now().isoformat(),
        happiness=max(0, player['happiness'] - 5)
    )
    
    job_names = {
        7: "🕵️‍♂️ Провели аферу",
        8: "📦 Поработали в ПВЗ",
    }
    
    job_name = job_names.get(player['job_level'], "💼 Поработали")
    
    await update.message.reply_text(f"{job_name} и заработали {earnings} руб.! 💰 Теперь у вас: {new_money} руб.\n\n😔 Счастье немного уменьшилось...")

# ... (остальные функции остаются такими же, как в предыдущем коде, но с добавлением проверки бессознательного состояния)

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
    stick_type = "обычные"
    unconscious_time = 0
    
    # Определяем тип стиков по названию
    if "малина лед" in str(player.get('stick_flavor', '')).lower():
        stick_type = "малина лёд 🧊"
        unconscious_time = 2  # 2 секунды бессознательного состояния
    
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
    
    battery_warning = "🪫 Айкос почти разряжен! Зарядите устройство." if new_battery <= 20 else ""
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно лечитесь!" if new_health <= 20 else ""
    
    message = f"🔥 Вы покурили Айкос ({stick_type})...\n\n❤️ Здоровье: -10 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness})\n📦 Стиков осталось: {new_sticks} шт.\n🔋 Батарея Айкос: {new_battery}%"
    
    # Если это крепкие стики, добавляем эффект бессознательного состояния
    if unconscious_time > 0:
        unconscious_until = datetime.now() + timedelta(seconds=unconscious_time)
        update_player(user_id, unconscious_until=unconscious_until.isoformat())
        message += f"\n\n💫 ОЙ! Слишком крепко! Вы потеряли сознание на {unconscious_time} секунды!"
    
    message += f"\n\n{battery_warning}\n{health_warning}\n⚠️ Курение в реальной жизни вредит здоровью!"
    
    await update.message.reply_text(message)

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
    
    # Проверяем тип жидкости
    juice_type = "обычная"
    unconscious_time = 0
    
    # Определяем тип жидкости по названию
    if "морозная вишня 120мг" in str(player['juice_flavor']).lower():
        juice_type = "Морозная Вишня 120мг ❄️"
        unconscious_time = 3  # 3 секунды бессознательного состояния
    
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
    
    message = f"💨 Вы покурили вейп ({player['vape_type']})...\n\n❤️ Здоровье: -8 (теперь {new_health})\n😊 Счастье: +25 (теперь {new_happiness})\n💧 Жидкости осталось: {new_juice}мл\n🔋 Батарея вейпа: {new_battery}%\n🎯 Вкус: {player['juice_flavor']}"
    
    # Если это крепкая жидкость, добавляем эффект бессознательного состояния
    if unconscious_time > 0:
        unconscious_until = datetime.now() + timedelta(seconds=unconscious_time)
        update_player(user_id, unconscious_until=unconscious_until.isoformat())
        message += f"\n\n💫 ОЙ! Слишком крепко! Вы потеряли сознание на {unconscious_time} секунды!"
    
    message += f"\n\n{battery_warning}\n{health_warning}\n⚠️ Вейпинг в реальной жизни тоже вреден для здоровья!"
    
    await update.message.reply_text(message)

# МАГАЗИН С ПЕРЕРАСПРЕДЕЛЕННЫМИ КАТЕГОРИЯМИ
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
        [InlineKeyboardButton("💨 Вейпы и устройства", callback_data="vapes_shop")],
        [InlineKeyboardButton("💧 Жидкости для вейпов", callback_data="vape_juices_shop")],
        [InlineKeyboardButton("🚬 Одноразки", callback_data="disposables_shop")],
        [InlineKeyboardButton("🔥 Айкос и системы", callback_data="iqos_shop")],
        [InlineKeyboardButton("💨 Кальяны и табак", callback_data="hookah_shop")],
        [InlineKeyboardButton("📦 Снюс и жевательный табак", callback_data="snus_shop")],
        [InlineKeyboardButton("🍃 Чай в бумаге", callback_data="tea_shop")],
        [InlineKeyboardButton("⚡ Зарядка устройств", callback_data="charge_shop")],
        [InlineKeyboardButton("💼 Работа и технологии", callback_data="work_tech_shop")],
        [InlineKeyboardButton("🏡 Недвижимость", callback_data="real_estate_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🛒 МАГАЗИН - Выберите категорию:", reply_markup=reply_markup)

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
    
    await query.edit_message_text("🍖 ЕДА И ЗДОРОВЬЕ:\n\n🍖 Еда - 50 руб. (+30 к еде)\n❤️ Лечение - 100 руб. (+30 к здоровью)\n😊 Развлечения - 80 руб. (+20 к счастью)", reply_markup=reply_markup)

async def cigarettes_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🚬 Сигареты (30 руб.)", callback_data="buy_cigarettes")],
        [InlineKeyboardButton("🍒 Чапман с вишней (200 руб.)", callback_data="buy_chapman")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🚬 СИГАРЕТЫ:\n\n🚬 Сигареты - 30 руб. (20 шт)\n🍒 Чапман с вишней - 200 руб. (10 шт)", reply_markup=reply_markup)

async def vapes_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💨 Начинающий вейп (1000 руб.)", callback_data="buy_vape_beginner")],
        [InlineKeyboardButton("💨 Профессиональный вейп (2000 руб.)", callback_data="buy_vape_pro")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💨 ВЕЙПЫ И УСТРОЙСТВА:\n\n💨 Начинающий вейп - 1000 руб.\n💨 Профессиональный вейп - 2000 руб.", reply_markup=reply_markup)

async def vape_juices_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🍉 Арбуз и мята (200 руб.)", callback_data="buy_juice_watermelon")],
        [InlineKeyboardButton("🌿 Лесные ягоды и мята (220 руб.)", callback_data="buy_juice_berries")],
        [InlineKeyboardButton("🍌 Анархия: Банан-Малина 70мг (300 руб.)", callback_data="buy_juice_anarchy")],
        [InlineKeyboardButton("🍌 Монашка: Банан и лед 50мг (280 руб.)", callback_data="buy_juice_monk")],
        [InlineKeyboardButton("🍒 Морозная Вишня 120мг (500 руб.)", callback_data="buy_juice_frost_cherry")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💧 ЖИДКОСТИ ДЛЯ ВЕЙПОВ:\n\n🍉 Арбуз и мята - 200 руб. (30мл)\n🌿 Лесные ягоды и мята - 220 руб. (30мл)\n🍌 Анархия: Банан-Малина 70мг - 300 руб. (30мл)\n🍌 Монашка: Банан и лед 50мг - 280 руб. (30мл)\n🍒 Морозная Вишня 120мг - 500 руб. (30мл) 💀 ОЧЕНЬ КРЕПКАЯ!", reply_markup=reply_markup)

async def disposables_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🚬 Эльфбар клубника (300 руб.)", callback_data="buy_elfbar")],
        [InlineKeyboardButton("🍇 Одноразка виноград (800 руб.)", callback_data="buy_grape_disposable")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🚬 ОДНОРАЗКИ:\n\n🚬 Эльфбар клубника - 300 руб. (600 тяг)\n🍇 Одноразка виноград - 800 руб. (1000 тяг)", reply_markup=reply_markup)

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
    
    await query.edit_message_text("🔥 АЙКОС И СИСТЕМЫ:\n\n🔥 Айкос устройство - 1500 руб.\n📦 Обычные стики - 100 руб. (10 шт)\n🧊 Стики Малина Лёд - 300 руб. (10 шт) 💀 ОЧЕНЬ КРЕПКИЕ!", reply_markup=reply_markup)

async def hookah_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💨 Кальян (2000 руб.)", callback_data="buy_hookah")],
        [InlineKeyboardButton("🔥 Угли (100 руб.)", callback_data="buy_coals")],
        [InlineKeyboardButton("🔥 Горелка (300 руб.)", callback_data="buy_burner")],
        [InlineKeyboardButton("🌿 Табак малина (400 руб.)", callback_data="buy_raspberry_tobacco")],
        [InlineKeyboardButton("🥤 Табак кола (350 руб.)", callback_data="buy_cola_tobacco")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("💨 КАЛЬЯНЫ И ТАБАК:\n\n💨 Кальян - 2000 руб.\n🔥 Угли - 100 руб. (5 шт)\n🔥 Горелка - 300 руб.\n🌿 Табак малина - 400 руб. (50г) КРЕПОСТЬ 9/10\n🥤 Табак кола - 350 руб. (50г) КРЕПОСТЬ 4/10", reply_markup=reply_markup)

async def snus_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📦 Снюс 500 мг (150 руб.)", callback_data="buy_snus")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("📦 СНЮС И ЖЕВАТЕЛЬНЫЙ ТАБАК:\n\n📦 Снюс 500 мг - 150 руб. (1 пачка) 💀 ОЧЕНЬ КРЕПКИЙ!", reply_markup=reply_markup)

async def tea_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🍃 Бумага с чаем (20 руб.)", callback_data="buy_tea_leaf")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🍃 ЧАЙ В БУМАГЕ:\n\n🍃 Бумага с чаем - 20 руб. (для тех кому нет 18 лет)", reply_markup=reply_markup)

async def charge_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("⚡ Зарядка вейпа (100 руб.)", callback_data="charge_vape")],
        [InlineKeyboardButton("⚡ Зарядка айкос (80 руб.)", callback_data="charge_iqos")],
        [InlineKeyboardButton("⚡ Зарядка всего (150 руб.)", callback_data="charge_all")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("⚡ ЗАРЯДКА УСТРОЙСТВ:\n\n⚡ Зарядка вейпа - 100 руб.\n⚡ Зарядка айкос - 80 руб.\n⚡ Зарядка всего - 150 руб.", reply_markup=reply_markup)

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
    
    await query.edit_message_text("💼 РАБОТА И ТЕХНОЛОГИИ:\n\n💼 Устроиться на работу - 200 руб.\n💻 Ноутбук - 5000 руб.\n🛡️ VPN - 200 руб.", reply_markup=reply_markup)

async def real_estate_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏡 Купить квартиру (50000 руб.)", callback_data="buy_apartment_shop")],
        [InlineKeyboardButton("⬅️ Назад в магазин", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("🏡 НЕДВИЖИМОСТЬ:\n\n🏡 Квартира - 50000 руб.", reply_markup=reply_markup)

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
    
    # Обработка категорий магазина
    if query.data == "food_health_shop":
        await food_health_shop(update, context)
        return
    elif query.data == "cigarettes_shop":
        await cigarettes_shop(update, context)
        return
    elif query.data == "vapes_shop":
        await vapes_shop(update, context)
        return
    elif query.data == "vape_juices_shop":
        await vape_juices_shop(update, context)
        return
    elif query.data == "disposables_shop":
        await disposables_shop(update, context)
        return
    elif query.data == "iqos_shop":
        await iqos_shop(update, context)
        return
    elif query.data == "hookah_shop":
        await hookah_shop(update, context)
        return
    elif query.data == "snus_shop":
        await snus_shop(update, context)
        return
    elif query.data == "tea_shop":
        await tea_shop(update, context)
        return
    elif query.data == "charge_shop":
        await charge_shop(update, context)
        return
    elif query.data == "work_tech_shop":
        await work_tech_shop(update, context)
        return
    elif query.data == "real_estate_shop":
        await real_estate_shop(update, context)
        return
    elif query.data == "back_to_shop":
        await shop(update, context)
        return
    
    # Обработка покупок товаров
    item_data = {
        "buy_food": {"price": 50, "type": "food"},
        "buy_cigarettes": {"price": 30, "type": "cigarettes"},
        "buy_chapman": {"price": 200, "type": "chapman"},
        "buy_health": {"price": 100, "type": "health"},
        "buy_happiness": {"price": 80, "type": "happiness"},
        "buy_job": {"price": 200, "type": "job"},
        "buy_laptop": {"price": 5000, "type": "laptop"},
        "buy_vpn": {"price": 200, "type": "vpn"},
        "buy_snus": {"price": 150, "type": "snus"},
        "buy_tea_leaf": {"price": 20, "type": "tea_leaf"},
        "buy_vape_beginner": {"price": 1000, "type": "vape_device", "device": "Начинающий вейп"},
        "buy_vape_pro": {"price": 2000, "type": "vape_device", "device": "Профессиональный вейп"},
        "buy_elfbar": {"price": 300, "type": "elfbar"},
        "buy_grape_disposable": {"price": 800, "type": "grape_disposable"},
        "buy_hookah": {"price": 2000, "type": "hookah"},
        "buy_coals": {"price": 100, "type": "coals"},
        "buy_burner": {"price": 300, "type": "burner"},
        "buy_raspberry_tobacco": {"price": 400, "type": "raspberry_tobacco"},
        "buy_cola_tobacco": {"price": 350, "type": "cola_tobacco"},
        "buy_iqos_device": {"price": 1500, "type": "iqos_device"},
        "buy_iqos_sticks": {"price": 100, "type": "iqos_sticks"},
        "buy_iqos_raspberry_ice": {"price": 300, "type": "iqos_raspberry_ice"},
        "buy_juice_watermelon": {"price": 200, "type": "vape_juice", "flavor": "Арбуз и мята"},
        "buy_juice_berries": {"price": 220, "type": "vape_juice", "flavor": "Лесные ягоды и мята"},
        "buy_juice_anarchy": {"price": 300, "type": "vape_juice", "flavor": "Анархия: Банан-Малина 70мг"},
        "buy_juice_monk": {"price": 280, "type": "vape_juice", "flavor": "Монашка: Банан и лед 50мг"},
        "buy_juice_frost_cherry": {"price": 500, "type": "vape_juice", "flavor": "Морозная Вишня 120мг"},
        "charge_vape": {"price": 100, "type": "charge_vape"},
        "charge_iqos": {"price": 80, "type": "charge_iqos"},
        "charge_all": {"price": 150, "type": "charge_all"},
        "buy_apartment_shop": {"price": 50000, "type": "apartment"}
    }
    
    if query.data not in item_data:
        await query.edit_message_text("Неизвестный товар!")
        return
    
    item_info = item_data[query.data]
    price = item_info["price"]
    item_type = item_info["type"]
    
    if player['money'] < price:
        await query.edit_message_text(f"❌ Недостаточно денег! Нужно {price} руб., у вас {player['money']} руб.")
        return
    
    new_money = player['money'] - price
    message = f"✅ Покупка успешна!\n💰 Потрачено: {price} руб.\n💵 Осталось: {new_money} руб.\n\n"
    
    # Обработка разных типов товаров
    if item_type == "food":
        update_player(user_id, money=new_money, food=min(100, player['food'] + 30))
        message += "🍖 +30 к еде"
    elif item_type == "cigarettes":
        update_player(user_id, money=new_money, cigarettes=player['cigarettes'] + 20)
        message += "🚬 +20 сигарет"
    elif item_type == "chapman":
        update_player(user_id, money=new_money, chapman_cigarettes=player['chapman_cigarettes'] + 10)
        message += "🍒 +10 Чапман с вишней"
    elif item_type == "health":
        update_player(user_id, money=new_money, health=min(100, player['health'] + 30))
        message += "❤️ +30 к здоровью"
    elif item_type == "happiness":
        update_player(user_id, money=new_money, happiness=min(100, player['happiness'] + 20))
        message += "😊 +20 к счастью"
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
        message += "💻 Ноутбук приобретен! Теперь можно заниматься мошенничеством."
    elif item_type == "vpn":
        update_player(user_id, money=new_money, has_vpn=1)
        message += "🛡️ VPN активирован! Теперь мошенничество безопаснее."
    elif item_type == "snus":
        update_player(user_id, money=new_money, snus_packs=player['snus_packs'] + 1, snus_strength=50)
        message += "📦 +1 пачка снюса 50 мг (ОЧЕНЬ КРЕПКИЙ!)"
    elif item_type == "tea_leaf":
        update_player(user_id, money=new_money, has_tea_leaf=1)
        message += "🍃 Бумага с чаем приобретена! Для тех кому нет 18 лет."
    elif item_type == "vape_device":
        device_name = item_info["device"]
        update_player(user_id, money=new_money, vape_type=device_name, vape_battery=100)
        message += f"💨 {device_name} приобретен! Батарея: 100%"
    elif item_type == "elfbar":
        update_player(user_id, money=new_money, disposable_vape_type="Эльфбар клубника", disposable_vape_puffs=600)
        message += "🚬 Эльфбар клубника (600 тяг)"
    elif item_type == "grape_disposable":
        update_player(user_id, money=new_money, disposable_vape_type="Одноразка виноград", disposable_vape_puffs=1000)
        message += "🍇 Одноразка виноград (1000 тяг)"
    elif item_type == "hookah":
        update_player(user_id, money=new_money, has_hookah=1)
        message += "💨 Кальян приобретен!"
    elif item_type == "coals":
        update_player(user_id, money=new_money, hookah_coals=player['hookah_coals'] + 5)
        message += "🔥 +5 углей для кальяна"
    elif item_type == "burner":
        update_player(user_id, money=new_money, has_burner=1)
        message += "🔥 Горелка приобретена!"
    elif item_type == "raspberry_tobacco":
        update_player(user_id, money=new_money, hookah_tobacco="Малина", hookah_tobacco_amount=player['hookah_tobacco_amount'] + 50)
        message += "🌿 Табак малина 50г (крепкость 9/10)"
    elif item_type == "cola_tobacco":
        update_player(user_id, money=new_money, hookah_tobacco="Кола", hookah_tobacco_amount=player['hookah_tobacco_amount'] + 50)
        message += "🥤 Табак кола 50г (крепкость 4/10)"
    elif item_type == "iqos_device":
        update_player(user_id, money=new_money, has_iqos=1, iqos_battery=100)
        message += "🔥 Айкос устройство приобретено! Батарея: 100%"
    elif item_type == "iqos_sticks":
        update_player(user_id, money=new_money, iqos_sticks=player['iqos_sticks'] + 10)
        message += "📦 +10 обычных стиков для Айкос"
    elif item_type == "iqos_raspberry_ice":
        update_player(user_id, money=new_money, iqos_sticks=player['iqos_sticks'] + 10)
        # Сохраняем информацию о типе стиков
        update_player(user_id, stick_flavor="Малина Лёд 🧊")
        message += "🧊 +10 стиков Малина Лёд для Айкос (ОЧЕНЬ КРЕПКИЕ!)"
    elif item_type == "vape_juice":
        flavor = item_info["flavor"]
        update_player(user_id, money=new_money, vape_juice=player['vape_juice'] + 30, juice_flavor=flavor)
        message += f"💧 +30мл жидкости: {flavor}"
    elif item_type == "charge_vape":
        if player['vape_type'] and player['vape_battery'] < 100:
            update_player(user_id, money=new_money, vape_battery=100)
            message += "⚡ Вейп заряжен до 100%"
        else:
            message = "❌ Нет вейпа для зарядки или он уже заряжен!"
            new_money = player['money']
    elif item_type == "charge_iqos":
        if player['has_iqos'] and player['iqos_battery'] < 100:
            update_player(user_id, money=new_money, iqos_battery=100)
            message += "⚡ Айкос заряжен до 100%"
        else:
            message = "❌ Нет айкос для зарядки или он уже заряжен!"
            new_money = player['money']
    elif item_type == "charge_all":
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
            new_money = player['money']
    elif item_type == "apartment":
        if not player['has_apartment']:
            update_player(user_id, money=new_money, has_apartment=1)
            message += "🏡 Квартира приобретена! Теперь у вас есть свой дом."
        else:
            message = "❌ У вас уже есть квартира!"
            new_money = player['money']
    
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
    elif text == "🏡 Квартира":
        await apartment_menu(update, context)
    elif text == "🚬 Курить/Вейпить/Снюс":
        await smoke_vape_menu(update, context)
    elif text == "🚬 Выкурить сигарету":
        await smoke_cigarette(update, context)
    elif text == "🍒 Выкурить Чапман":
        await smoke_chapman(update, context)
    elif text == "💨 Покурить вейп":
        await vape(update, context)
    elif text == "🚬 Покурить одноразку":
        await use_disposable_vape(update, context)
    elif text == "🔥 Покурить айкос":
        await use_iqos(update, context)
    elif text == "📦 Закинуть снюс":
        await use_snus(update, context)
    elif text == "💨 Покурить кальян":
        await use_hookah(update, context)
    elif text == "🍃 Покурить бумагу с чаем":
        await use_tea_leaf(update, context)
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
