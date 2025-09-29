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
            created_at TEXT
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
            'vape_battery': 'ALTER TABLE players ADD COLUMN vape_battery INTEGER DEFAULT 0'
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
                  'last_fraud_time', 'has_iqos', 'iqos_sticks', 'iqos_battery', 'vape_battery', 'created_at']
        
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
                vape_battery = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при сбросе игрока: {e}")
    finally:
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
        8: "Работник ПВЗ (3250 руб.)"
    }
    return jobs.get(level, "Неизвестно")

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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

async def crime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Украсть кошелек", "🏪 Ограбить магазин"],
        ["🏠 Ограбить квартиру", "🚗 Угнать машину"],
        ["🕵️‍♂️ Мошенничество", "⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("🔫 КРИМИНАЛ:\n\n💰 Украсть кошелек - мало риска, мало денег\n🏪 Ограбить магазин - средний риск, средние деньги\n🏠 Ограбить квартиру - высокий риск, много денег\n🚗 Угнать машину - очень высокий риск, очень много денег\n🕵️‍♂️ Мошенничество - интернет-аферы (нужен ноутбук)\n\n⚠️ Внимание: Криминал опасен! Можете попасть в тюрьму (сброс прогресса)!", reply_markup=reply_markup)

async def commit_crime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
    elif crime_type == "🏪 Ограбить магазин":
        money_min, money_max = 200, 500
        arrest_chance = 0.4
        crime_name = "ограбление магазина" 
        escape_chance = 0.5
    elif crime_type == "🏠 Ограбить квартиру":
        money_min, money_max = 500, 1000
        arrest_chance = 0.6
        crime_name = "ограбление квартиры"
        escape_chance = 0.3
    elif crime_type == "🚗 Угнать машину":
        money_min, money_max = 1000, 2000
        arrest_chance = 0.8
        crime_name = "угон машины"
        escape_chance = 0.2
    elif crime_type == "🕵️‍♂️ Мошенничество":
        if not player['has_laptop']:
            await update.message.reply_text("❌ Для мошенничества нужен ноутбук! Купите в магазине.")
            return
        
        money_min, money_max = 600, 1200
        arrest_chance = 0.3 if player['has_vpn'] else 0.6
        crime_name = "мошенничество"
        escape_chance = 0.8 if player['has_vpn'] else 0.4
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
        
        crime_emoji = "💻" if crime_type == "🕵️‍♂️ Мошенничество" else "💰"
        
        vpn_message = "🛡️ VPN помог остаться анонимным!" if crime_type == "🕵️‍♂️ Мошенничество" and player['has_vpn'] else "🏃‍♂️ Быстро скрывайтесь с места преступления!"
        
        await update.message.reply_text(f"✅ Преступление удалось!\n\n{crime_emoji} Вы получили: {stolen_money} руб.\n💰 Теперь у вас: {new_money} руб.\n😊 Счастье: +10\n\n{vpn_message}")
    else:
        if random.random() < escape_chance:
            escape_text = "скрыть следы" if crime_type == "🕵️‍♂️ Мошенничество" else "убежать"
            vpn_text = "использовали VPN для анонимности" if crime_type == "🕵️‍♂️ Мошенничество" and player['has_vpn'] else "скрылись в темных переулках"
            
            await update.message.reply_text(f"🏃‍♂️ ВАС ПОЧТИ ПОЙМАЛИ!\n\nПолиция заметила вас при попытке {crime_name}, но вам удалось {escape_text}!\n\n💨 Вы {vpn_text}...\n😰 Счастье: -15")
            
            update_player(user_id, happiness=max(0, player['happiness'] - 15))
        else:
            await update.message.reply_text(f"🚨🚨🚨 ВАС ПОЙМАЛИ! 🚨🚨🚨\n\nПолиция поймала вас при попытке {crime_name}!\nВас посадили в тюрьму...\n\n💀 Все достижения сброшены!")
            reset_player(user_id, player['username'])

async def school_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📚 Учиться", "🚬 Сходить в туалет покурить"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("🏫 ШКОЛА:\n\n📚 Учиться - повысить уровень образования\n🚬 Сходить в туалет покурить - рискованно, но можно покурить\n\n⚠️ Внимание: курение в школе может привести к проблемам!", reply_markup=reply_markup)

async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
    
    await update.message.reply_text(f"🎓 Поздравляем! Вы получили: {education_names[new_education_level]}\n\nТеперь вы можете устроиться на работу уровня {new_education_level}!\n\n😔 Счастье немного уменьшилось от учебы...")

async def school_smoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    teacher_catch_chance = 0.4
    
    if random.random() < teacher_catch_chance:
        await update.message.reply_text("🚨🚨🚨 ВАС ПОЙМАЛИ! 🚨🚨🚨\n\nУчитель застал вас курящим в школьном туалете!\nРодители вызваны в школу...\nВас отчислили! Игра начинается заново.\n\n💀 Все достижения сброшены!")
        reset_player(user_id, player['username'])
    else:
        keyboard = [
            ["🚬 Выкурить сигарету", "💨 Покурить вейп"],
            ["🔥 Покурить айкос", "📦 Закинуть снюс"],
            ["⬅️ Выйти из туалета"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update_player(user_id, last_smoke_time=datetime.now().isoformat())
        
        await update.message.reply_text("🚬 Вы успешно пробрались в школьный туалет...\n\n💨 Пахнет дымом и вейпом...\n👀 Осторожно! Учитель может зайти в любой момент!\n\nВыберите что хотите сделать:", reply_markup=reply_markup)

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
    
    await update.message.reply_text("🚬 Выберите что хотите использовать:\n\n🚬 Сигарета - больше вреда, но дешевле\n💨 Вейп - меньше вреда, но нужен вейп и жидкость\n🔥 Айкос - система нагревания табака, меньше вреда чем сигареты\n📦 Снюс - очень крепкий, большой вред здоровью\n\n⚠️ Помните: в реальной жизни и то и другое вредно для здоровья!", reply_markup=reply_markup)

async def smoke_cigarette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
    
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно лечитесь!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"🚬 Вы выкурили сигарету...\n\n❤️ Здоровье: -15 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness})\n📦 Сигарет осталось: {new_cigarettes}\n\n{health_warning}\n⚠️ Курение в реальной жизни вызывает рак и другие заболевания!")

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
    
    await update.message.reply_text(f"💨 Вы покурили вейп ({player['vape_type']})...\n\n❤️ Здоровье: -8 (теперь {new_health})\n😊 Счастье: +25 (теперь {new_happiness})\n💧 Жидкости осталось: {new_juice}мл\n🔋 Батарея вейпа: {new_battery}%\n🎯 Вкус: {player['juice_flavor']}\n\n{battery_warning}\n{health_warning}\n⚠️ Вейпинг в реальной жизни тоже вреден для здоровья!")

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
    
    await update.message.reply_text(f"🔥 Вы покурили Айкос (мятные стики)...\n\n❤️ Здоровье: -10 (теперь {new_health})\n😊 Счастье: +20 (теперь {new_happiness})\n📦 Стиков осталось: {new_sticks}\n🔋 Батарея Айкос: {new_battery}%\n\n{battery_warning}\n{health_warning}\n⚠️ Курение в реальной жизни вредит здоровью!")

async def use_snus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['snus_packs'] <= 0:
        await update.message.reply_text("❌ У вас нет снюса! Купите в магазине.")
        return
    
    new_snus = player['snus_packs'] - 1
    new_health = max(0, player['health'] - 25)
    new_happiness = min(100, player['happiness'] + 30)
    
    update_player(
        user_id,
        snus_packs=new_snus,
        health=new_health,
        happiness=new_happiness
    )
    
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! СРОЧНО ПРЕКРАТИТЕ И ЛЕЧИТЕСЬ!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"📦 Вы закинули снюс {player['snus_strength']} мг...\n\n❤️ Здоровье: -25 (теперь {new_health})\n😊 Счастье: +30 (теперь {new_happiness})\n📦 Пачек снюса осталось: {new_snus}\n\n{health_warning}\n⚠️ СНЮС ОЧЕНЬ ОПАСЕН! В реальной жизни вызывает рак ротовой полости!")

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
    
    await update.message.reply_text("🛒 МАГАЗИН:\n\n🍖 Еда (50 руб.) - +50 к еде\n🚬 Сигареты (30 руб.) - пачка сигарет (только с 18 лет)\n🔞 Попросить взрослых (100 руб.) - дороже, но без паспорта\n💨 Вейпы и жижи - электронные сигареты и жидкости\n🔥 Айкос и стики - системы нагревания табака\n⚡ Зарядка устройств (120 руб.) - зарядить вейп/айкос\n📦 Снюс 500 мг (150 руб.) - крепкий снюс\n❤️ Лечение (100 руб.) - +30 к здоровью\n😊 Развлечения (80 руб.) - +40 к счастью\n💼 Устроиться на работу (200 руб.) - получить работу\n💻 Ноутбук (5000 руб.) - для удаленной работы и мошенничества\n🛡️ VPN (200 руб.) - анонимность для мошенничества\n\nВыберите что хотите купить:", reply_markup=reply_markup)

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
    
    await query.edit_message_text("💨 МАГАЗИН ВЕЙПОВ И ЖИДКОСТЕЙ:\n\n🔋 Вейп устройства - одноразовые и многоразовые\n💧 Жидкости - разные вкусы\n🔞 Попросить взрослых купить вейп - купить без паспорта\n🔞 Попросить взрослых купить жижу - купить без паспорта\n\n⚠️ Для покупки вейпов нужно быть 18+ или попросить взрослых", reply_markup=reply_markup)

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
    
    await query.edit_message_text("🔥 МАГАЗИН АЙКОС:\n\n🔥 Айкос устройство - 800 руб. (система нагревания табака)\n📦 Мятные стики - 150 руб. (пачка стиков)\n🔞 Попросить взрослых купить айкос - 1000 руб. (без паспорта)\n\n⚠️ Для покупки айкос нужно быть 18+ или попросить взрослых", reply_markup=reply_markup)

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
    
    await query.edit_message_text("🔋 ВЕЙП УСТРОЙСТВА:\n\nPasito 2 - 400 руб. (мощный, многоразовый)\nXros - 350 руб. (компактный)\nBoost 2 - 450 руб. (профессиональный)\nMinican - 300 руб. (одноразовый)\nKnight - 380 руб. (стильный)\n\nВыберите устройство:", reply_markup=reply_markup)

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
    
    await query.edit_message_text("💧 ЖИДКОСТИ ДЛЯ ВЕЙПА:\n\n🍉 Арбуз и мята - 200 руб. (30мл)\n🌿 Лесные ягоды и мята - 220 руб. (30мл)\n🍌 Анархия: Банан-Малина 70мг - 300 руб. (30мл) - ОЧЕНЬ КРЕПКАЯ!\n\nЖидкости добавляют 30мл к вашему вейпу", reply_markup=reply_markup)

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
        if player['job_level'] < 8:
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
    
    await query.edit_message_text(message)

async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await shop(update, context)

async def buy_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_apartment']:
        await update.message.reply_text("🏡 У вас уже есть квартира!")
        return
    
    apartment_price = 50000
    
    if player['money'] < apartment_price:
        await update.message.reply_text(f"❌ Недостаточно денег для покупки квартиры!\n💰 Нужно: {apartment_price} руб.\n💵 У вас: {player['money']} руб.\n\n💼 Продолжайте работать и копите деньги!")
        return
    
    new_money = player['money'] - apartment_price
    update_player(user_id, money=new_money, has_apartment=1, happiness=min(100, player['happiness'] + 50))
    
    await update.message.reply_text(f"🎉 ПОЗДРАВЛЯЕМ! Вы купили квартиру за {apartment_price} руб.!\n\n🏡 Теперь у вас есть собственное жилье!\n😊 Счастье значительно увеличилось!\n💰 Осталось денег: {new_money} руб.\n\n🎯 Основная цель достигнута! Вы победили в игре!\nНо жизнь продолжается... 😊")

async def celebrate_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    new_age = player['age'] + 1
    update_player(user_id, age=new_age, happiness=min(100, player['happiness'] + 10))
    
    message = f"🎂 С Днем Рождения! Вам теперь {new_age} лет!\n😊 +10 к счастью"
    
    if new_age == 18:
        message += "\n\n🎉 Вам 18 лет! Теперь вы можете:\n• Получить паспорт\n• Легально покупать сигареты\n• Легально покупать вейпы\n• Легально покупать айкос\n• Устроиться на работу дальнобойщиком"
    
    await update.message.reply_text(message)

async def get_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_id']:
        await update.message.reply_text("📋 У вас уже есть паспорт!")
        return
    
    if player['age'] < 18:
        await update.message.reply_text(f"❌ Паспорт можно получить только с 18 лет! Вам сейчас {player['age']} лет.")
        return
    
    update_player(user_id, has_id=1)
    await update.message.reply_text("📋 Поздравляем! Вы получили паспорт!\n\nТеперь вы можете:\n• Легально покупать сигареты\n• Легально покупать вейпы\n• Легально покупать айкос\n• Устроиться на взрослую работу\n• Жить полной жизнью!")

async def girlfriend_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
    
    if not player['has_girlfriend']:
        await update.message.reply_text("💕 ДЕВУШКА:\n\nУ вас пока нет девушки. Хотите найти?\n- Девушка увеличивает счастье\n- Нужно ходить на свидания\n- Можно дарить подарки\n\nНажмите '💕 Найти девушку' чтобы попробовать!", reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"💕 ВАША ДЕВУШКА:\n\n😊 Счастье девушки: {player['girlfriend_happiness']}/100\n\n💑 Свидание - повышает счастье девушки\n🎁 Подарок - дорого, но сильно повышает счастье\n💔 Расстаться - если надоело\n\nЧем счастливее девушка, тем больше бонус к вашему счастью!", reply_markup=reply_markup)

async def find_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['has_girlfriend']:
        await update.message.reply_text("💕 У вас уже есть девушка!")
        return
    
    success_chance = 0.3 + (player['happiness'] / 200) + (min(player['money'], 1000) / 2000)
    
    if random.random() < success_chance:
        update_player(
            user_id,
            has_girlfriend=1,
            girlfriend_happiness=50,
            happiness=min(100, player['happiness'] + 20)
        )
        await update.message.reply_text("💕 ПОЗДРАВЛЯЕМ! Вы нашли девушку!\n\n😊 Ваше счастье: +20\n💑 Счастье девушки: 50/100\n\nТеперь вы можете ходить на свидания и дарить подарки!\nЧем счастливее девушка, тем больше бонус к вашему счастью!")
    else:
        await update.message.reply_text("😔 Вам не удалось найти девушку...\n\nПопробуйте еще раз когда будете счастливее и богаче!\nДевушкам нравятся уверенные и успешные парни.")

async def date_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    last_date = datetime.fromisoformat(player['last_date_time']) if player['last_date_time'] else None
    if last_date and (datetime.now() - last_date) < timedelta(minutes=15):
        time_left = timedelta(minutes=15) - (datetime.now() - last_date)
        await update.message.reply_text(f"💑 Девушка устала! Подождите {int(time_left.total_seconds() / 60)} минут до следующего свидания.")
        return
    
    happiness_increase = random.randint(10, 20)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    player_happiness_bonus = happiness_increase // 2
    
    update_player(
        user_id,
        girlfriend_happiness=new_girlfriend_happiness,
        happiness=min(100, player['happiness'] + player_happiness_bonus),
        last_date_time=datetime.now().isoformat()
    )
    
    await update.message.reply_text(f"💑 Вы сходили на свидание!\n\n😊 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness}/100)\n🎉 Ваше счастье: +{player_happiness_bonus}\n\nДевушка очень довольна свиданием!")

async def gift_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    gift_price = 500
    
    if player['money'] < gift_price:
        await update.message.reply_text(f"❌ Недостаточно денег для подарка! Нужно {gift_price} руб.")
        return
    
    happiness_increase = random.randint(25, 40)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    new_money = player['money'] - gift_price
    
    update_player(
        user_id,
        girlfriend_happiness=new_girlfriend_happiness,
        money=new_money,
        happiness=min(100, player['happiness'] + 15)
    )
    
    await update.message.reply_text(f"🎁 Вы подарили девушке дорогой подарок!\n\n😊 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness}/100)\n💵 Потрачено: {gift_price} руб.\n💰 Осталось: {new_money} руб.\n🎉 Ваше счастье: +15\n\nДевушка в восторге от подарка!")

async def break_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    update_player(
        user_id,
        has_girlfriend=0,
        girlfriend_happiness=0,
        happiness=max(0, player['happiness'] - 30)
    )
    
    await update.message.reply_text("💔 Вы расстались с девушкой...\n\n😔 Ваше счастье: -30\n💔 Теперь вы снова одиноки\n\nМожете найти новую девушку когда будете готовы!")

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

def main():
    # Инициализация базы данных
    init_db()
    upgrade_db()
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^vape_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^iqos_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^charge_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^back_to_shop"))
    
    print("Бот запущен...")
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
