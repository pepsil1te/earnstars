import os
import json
from dotenv import load_dotenv
import telebot
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import threading
import base64
import requests
import time

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/prices": {
        "origins": "*",  # Разрешаем запросы с любого домена
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

# Путь к файлу с ценами
PRICES_FILE = os.path.join(os.path.dirname(__file__), 'config', 'prices.json')

# Путь к файлу конфигурации
SERVER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'server_config.json')

def load_prices():
    """Загружает цены из JSON файла"""
    with open(PRICES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_prices(prices):
    """Сохраняет цены в JSON файл"""
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)

def load_server_config():
    try:
        with open(SERVER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации сервера: {e}")
        return {
            "development": {"server_url": "http://localhost:5000"},
            "production": {"server_url": "http://localhost:5000"}
        }

def save_server_config(config):
    try:
        with open(SERVER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации сервера: {e}")
        return False

@app.route('/prices', methods=['GET'])
def get_prices():
    """Возвращает все цены"""
    try:
        prices = load_prices()
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_package_price(stars, new_price, new_usd):
    """Обновляет цену пакета звезд"""
    try:
        prices = load_prices()
        for package in prices['stars']['packages']:
            if package['stars'] == stars:
                package['price'] = new_price
                package['usd'] = new_usd
                save_prices(prices)
                return True
        return False
    except Exception as e:
        print(f"Ошибка при обновлении цены пакета: {e}")
        return False

def update_gift_price(gift_id, new_price):
    """Обновляет цену подарка"""
    try:
        prices = load_prices()
        for gift_type, gift in prices['gifts'].items():
            if str(gift['id']) == str(gift_id):
                gift['price'] = float(new_price)
                save_prices(prices)
                return True
        return False
    except Exception as e:
        raise Exception(f"Ошибка при обновлении цены подарка: {str(e)}")

def update_premium_price(package_index, new_price):
    """Обновляет цену премиум пакета"""
    try:
        prices = load_prices()
        if 0 <= package_index < len(prices['premium']['packages']):
            prices['premium']['packages'][package_index]['price'] = float(new_price)
            save_prices(prices)
            return True
        return False
    except Exception as e:
        raise Exception(f"Ошибка при обновлении цены премиум пакета: {str(e)}")

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Отправляет приветственное сообщение и кнопку для открытия приложения"""
    markup = telebot.types.InlineKeyboardMarkup()
    webapp_btn = telebot.types.InlineKeyboardButton(
        text="Открыть",
        web_app=telebot.types.WebAppInfo(url="https://pepsil1te.github.io/earnstars/")
    )
    markup.add(webapp_btn)
    
    welcome_text = """👋 Привет! Я бот для покупки и заработка Telegram Stars.

🌟 С моей помощью вы можете:
• Покупать звезды для себя или друзей
• Дарить подарки
• Покупать Telegram Premium
• Зарабатывать на рефералах

Нажмите кнопку "Открыть" чтобы начать!"""
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "❌ У вас нет доступа к админ-панели")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("💫 Цены на звезды", callback_data="menu_stars"),
        telebot.types.InlineKeyboardButton("🎁 Цены на подарки", callback_data="menu_gifts"),
        telebot.types.InlineKeyboardButton("👑 Цены на Premium", callback_data="menu_premium")
    )
    
    bot.send_message(message.chat.id, "Выберите раздел для редактирования цен:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_menu_selection(call):
    if call.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.answer_callback_query(call.id, "У вас нет доступа к этой функции")
        return
    
    menu_type = call.data.split('_')[1]
    
    if menu_type == 'stars':
        show_stars_menu(call.message)
    elif menu_type == 'gifts':
        show_gifts_menu(call.message)
    elif menu_type == 'premium':
        show_premium_menu(call.message)
    
    bot.answer_callback_query(call.id)

def show_stars_menu(message):
    prices = load_prices()
    packages = prices['stars']['packages']
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for pkg in packages:
        button_text = f"{pkg['stars']} звезд - {pkg['price']}₽"
        callback_data = f"edit_stars_{pkg['stars']}"
        markup.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    # Добавляем кнопку возврата
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin"))
    
    bot.edit_message_text(
        "Выберите пакет звезд для изменения цены:",
        message.chat.id,
        message.message_id,
        reply_markup=markup
    )

def show_gifts_menu(message):
    try:
        prices = load_prices()
        gifts = prices['gifts']
        
        # Создаем клавиатуру с подарками
        keyboard = telebot.types.InlineKeyboardMarkup()
        for gift_type, gift in gifts.items():
            button_text = f"{gift['name']} - {gift['price']} ₽"
            callback_data = f"edit_gift_{gift['id']}"
            keyboard.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
        
        # Добавляем кнопку "Назад"
        keyboard.add(telebot.types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin"))
        
        # Отправляем новое сообщение вместо редактирования
        bot.send_message(
            chat_id=message.chat.id,
            text="Выберите подарок для редактирования цены:",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

def show_premium_menu(message):
    try:
        prices = load_prices()
        premium_packages = prices['premium']['packages']
        
        # Создаем клавиатуру с пакетами премиум
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i, pkg in enumerate(premium_packages):
            duration = pkg['duration']
            price = pkg['price']
            button_text = f"🌟 {duration} дней - {price} ₽"
            callback_data = f"edit_premium_{i}"  # Используем индекс вместо id
            keyboard.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
        
        # Добавляем кнопку "Назад"
        keyboard.add(telebot.types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin"))
        
        # Отправляем новое сообщение вместо редактирования
        bot.send_message(
            chat_id=message.chat.id,
            text="Выберите премиум пакет для редактирования цены:",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
def back_to_admin_menu(call):
    if call.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.answer_callback_query(call.id, "У вас нет доступа к этой функции")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("💫 Цены на звезды", callback_data="menu_stars"),
        telebot.types.InlineKeyboardButton("🎁 Цены на подарки", callback_data="menu_gifts"),
        telebot.types.InlineKeyboardButton("👑 Цены на Premium", callback_data="menu_premium")
    )
    
    bot.edit_message_text(
        "Выберите раздел для редактирования цен:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('edit_stars_', 'edit_gift_', 'edit_premium_')))
def handle_edit_selection(call):
    if call.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.answer_callback_query(call.id, "У вас нет доступа к этой функции")
        return
    
    try:
        action, item_type, item_id = call.data.split('_')
        prices = load_prices()
        
        if item_type == 'stars':
            stars = int(item_id)
            package = next((pkg for pkg in prices['stars']['packages'] if pkg['stars'] == stars), None)
            if package:
                msg = f"Текущая цена пакета {stars} звезд: {package['price']}₽ (${package['usd']})\n\n"
                msg += "Отправьте новую цену в рублях."
                bot.send_message(call.message.chat.id, msg)
                bot.register_next_step_handler(call.message, process_new_price, stars=stars)
        
        elif item_type == 'gift':
            gift_id = int(item_id)
            gift = next((data for _, data in prices['gifts'].items() if data['id'] == gift_id), None)
            if gift:
                msg = f"Текущая цена подарка '{gift['name']}': {gift['price']}₽\n\n"
                msg += "Отправьте новую цену в рублях."
                bot.send_message(call.message.chat.id, msg)
                bot.register_next_step_handler(call.message, process_new_gift_price, gift_id=gift_id)
        
        elif item_type == 'premium':
            package_index = int(item_id)
            package = prices['premium']['packages'][package_index]
            duration = package['duration']
            msg = f"Текущая цена пакета '{package['name']}': {package['price']}₽\n\n"
            msg += "Отправьте новую цену в рублях."
            bot.send_message(call.message.chat.id, msg)
            bot.register_next_step_handler(call.message, process_new_premium_price, package_index=package_index)
        
        bot.answer_callback_query(call.id)
    
    except Exception as e:
        bot.answer_callback_query(call.id, f"Произошла ошибка: {str(e)}")

def process_new_price(message, stars):
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        new_price = float(message.text)
        if new_price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        
        # Получаем курс USD
        usd_rate = get_usd_rate()
        new_usd = round(new_price / usd_rate, 2)
        
        # Обновляем цену
        if update_package_price(stars, new_price, new_usd):
            response = f"✅ Цена пакета {stars} звезд обновлена:\n"
            response += f"Новая цена: {new_price}₽ (${new_usd})"
        else:
            response = "❌ Пакет не найден"
        
        bot.reply_to(message, response)
    
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите корректную цену (число больше нуля)")
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

def process_new_gift_price(message, gift_id):
    """Обрабатывает новую цену подарка"""
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        new_price = float(message.text)
        if new_price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        
        # Обновляем цену подарка
        if update_gift_price(gift_id, new_price):
            prices = load_prices()
            gift_name = None
            for gift in prices['gifts'].values():
                if str(gift['id']) == str(gift_id):
                    gift_name = gift['name']
                    break
            
            response = f"✅ Цена подарка '{gift_name}' обновлена:\n"
            response += f"Новая цена: {new_price}₽"
        else:
            response = "❌ Подарок не найден"
        
        bot.reply_to(message, response)
        # Показываем обновленное меню подарков
        show_gifts_menu(message)
        
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите корректное число")
        show_gifts_menu(message)
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

def process_new_premium_price(message, package_index):
    """Обрабатывает новую цену премиум пакета"""
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        new_price = float(message.text)
        if new_price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        
        # Обновляем цену премиум пакета
        if update_premium_price(package_index, new_price):
            prices = load_prices()
            package = prices['premium']['packages'][package_index]
            response = f"✅ Цена премиум пакета на {package['duration']} дней обновлена:\n"
            response += f"Новая цена: {new_price}₽"
        else:
            response = "❌ Пакет не найден"
        
        bot.reply_to(message, response)
        # Показываем обновленное меню премиум пакетов
        show_premium_menu(message)
        
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите корректное число")
        show_premium_menu(message)
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

def get_usd_rate():
    """Получает актуальный курс USD/RUB с ЦБ РФ"""
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        if response.ok:
            data = response.json()
            return data['Valute']['USD']['Value']
    except:
        return 90.0  # Фиксированный курс если API недоступен

@bot.message_handler(commands=['seturl'])
def set_server_url(message):
    if str(message.from_user.id) != os.getenv('ADMIN_ID'):
        bot.reply_to(message, "У вас нет прав для выполнения этой команды")
        return

    try:
        # Получаем URL из сообщения
        url = message.text.split(maxsplit=1)[1].strip()
        
        # Проверяем формат URL
        if not url.startswith(('http://', 'https://')):
            bot.reply_to(message, "URL должен начинаться с http:// или https://")
            return
            
        # Загружаем текущую конфигурацию
        config = load_server_config()
        
        # Обновляем URL в конфигурации
        config['production']['server_url'] = url
        
        # Сохраняем конфигурацию
        if save_server_config(config):
            bot.reply_to(message, f"URL сервера успешно обновлен на: {url}")
        else:
            bot.reply_to(message, "Ошибка при сохранении конфигурации")
            
    except IndexError:
        bot.reply_to(message, "Использование: /seturl <url>\nПример: /seturl http://192.168.0.102:5000")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

if __name__ == '__main__':
    # Запускаем Flask сервер в отдельном потоке на всех интерфейсах
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка в работе бота: {e}")
            time.sleep(5)
