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

app = Flask(__name__)
CORS(app)

# Путь к файлу с ценами
PRICES_FILE = os.path.join(os.path.dirname(__file__), 'config', 'prices.json')

def load_prices():
    """Загружает цены из JSON файла"""
    with open(PRICES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_prices(prices):
    """Сохраняет цены в JSON файл"""
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)

@app.route('/prices', methods=['GET'])
def get_prices():
    try:
        return jsonify(load_prices())
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
        for gift_key, gift_data in prices['gifts'].items():
            if gift_data['id'] == gift_id:
                gift_data['price'] = new_price
                save_prices(prices)
                return True
        return False
    except Exception as e:
        print(f"Ошибка при обновлении цены подарка: {e}")
        return False

def update_premium_price(package_id, new_price):
    """Обновляет цену премиум пакета"""
    try:
        prices = load_prices()
        for package in prices['premium']['packages']:
            if package['id'] == package_id:
                package['price'] = new_price
                save_prices(prices)
                return True
        return False
    except Exception as e:
        print(f"Ошибка при обновлении цены премиум пакета: {e}")
        return False

def get_usd_rate():
    """Получает актуальный курс USD/RUB с ЦБ РФ"""
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        if response.ok:
            data = response.json()
            return data['Valute']['USD']['Value']
    except:
        return 90.0  # Фиксированный курс если API недоступен

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    bot.reply_to(message, "Привет! Используйте команду /admin для управления ценами.")

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
    prices = load_prices()
    gifts = prices['gifts']
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for gift_key, gift_data in gifts.items():
        button_text = f"{gift_data['name']} - {gift_data['price']}₽"
        callback_data = f"edit_gift_{gift_data['id']}"
        markup.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    # Добавляем кнопку возврата
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin"))
    
    bot.edit_message_text(
        "Выберите подарок для изменения цены:",
        message.chat.id,
        message.message_id,
        reply_markup=markup
    )

def show_premium_menu(message):
    prices = load_prices()
    packages = prices['premium']['packages']
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for pkg in packages:
        button_text = f"{pkg['name']} - {pkg['price']}₽"
        callback_data = f"edit_premium_{pkg['id']}"
        markup.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    # Добавляем кнопку возврата
    markup.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin"))
    
    bot.edit_message_text(
        "Выберите пакет Premium для изменения цены:",
        message.chat.id,
        message.message_id,
        reply_markup=markup
    )

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
            package_id = int(item_id)
            package = next((pkg for pkg in prices['premium']['packages'] if pkg['id'] == package_id), None)
            if package:
                msg = f"Текущая цена пакета '{package['name']}': {package['price']}₽\n\n"
                msg += "Отправьте новую цену в рублях."
                bot.send_message(call.message.chat.id, msg)
                bot.register_next_step_handler(call.message, process_new_premium_price, package_id=package_id)
        
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
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        new_price = float(message.text)
        if new_price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        
        # Обновляем цену
        if update_gift_price(gift_id, new_price):
            prices = load_prices()
            gift = next((data for _, data in prices['gifts'].items() if data['id'] == gift_id), None)
            response = f"✅ Цена подарка '{gift['name']}' обновлена:\n"
            response += f"Новая цена: {new_price}₽"
        else:
            response = "❌ Подарок не найден"
        
        bot.reply_to(message, response)
    
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите корректную цену (число больше нуля)")
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

def process_new_premium_price(message, package_id):
    if message.from_user.id != int(os.getenv('ADMIN_ID')):
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        new_price = float(message.text)
        if new_price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        
        # Обновляем цену
        if update_premium_price(package_id, new_price):
            prices = load_prices()
            package = next((pkg for pkg in prices['premium']['packages'] if pkg['id'] == package_id), None)
            response = f"✅ Цена пакета '{package['name']}' обновлена:\n"
            response += f"Новая цена: {new_price}₽"
        else:
            response = "❌ Пакет не найден"
        
        bot.reply_to(message, response)
    
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите корректную цену (число больше нуля)")
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

if __name__ == '__main__':
    # Загружаем переменные окружения
    load_dotenv()
    
    # Запускаем Flask сервер в отдельном потоке
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Бот запущен! Веб-сервер доступен по адресу http://localhost:5000")
    bot.polling()
