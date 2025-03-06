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

# Настройка SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель для хранения цен
class StarPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    usd = db.Column(db.Float, nullable=False)

class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class PremiumPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Создаем таблицы
with app.app_context():
    db.create_all()
    # Добавляем начальные данные, если база пустая
    if not StarPackage.query.first():
        initial_packages = [
            {'stars': 50, 'price': 50, 'usd': 0.56},
            {'stars': 75, 'price': 75, 'usd': 0.83},
            {'stars': 100, 'price': 100, 'usd': 1.11},
            {'stars': 150, 'price': 150, 'usd': 1.67},
            {'stars': 200, 'price': 200, 'usd': 2.22},
            {'stars': 300, 'price': 300, 'usd': 3.33},
            {'stars': 400, 'price': 400, 'usd': 4.44},
            {'stars': 500, 'price': 500, 'usd': 5.56}
        ]
        for pkg in initial_packages:
            db.session.add(StarPackage(**pkg))
        
        initial_gifts = [
            {'name': 'Подарок 1', 'price': 100},
            {'name': 'Подарок 2', 'price': 200},
            {'name': 'Подарок 3', 'price': 300},
        ]
        for gift in initial_gifts:
            db.session.add(Gift(**gift))
        
        initial_premium_packages = [
            {'name': 'Премиум 1', 'price': 500},
            {'name': 'Премиум 2', 'price': 1000},
            {'name': 'Премиум 3', 'price': 1500},
        ]
        for pkg in initial_premium_packages:
            db.session.add(PremiumPackage(**pkg))
        
        db.session.commit()

@app.route('/prices', methods=['GET'])
def get_prices():
    try:
        packages = StarPackage.query.all()
        gifts = Gift.query.all()
        premium_packages = PremiumPackage.query.all()
        prices_data = {
            'stars': {
                'packages': [
                    {'stars': pkg.stars, 'price': pkg.price, 'usd': pkg.usd}
                    for pkg in packages
                ]
            },
            'gifts': {
                gift.name: gift.price
                for gift in gifts
            },
            'premium': {
                'packages': [
                    {'name': pkg.name, 'price': pkg.price}
                    for pkg in premium_packages
                ]
            }
        }
        return jsonify(prices_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_package_price(stars, new_price, new_usd):
    with app.app_context():
        package = StarPackage.query.filter_by(stars=stars).first()
        if package:
            package.price = new_price
            package.usd = new_usd
            db.session.commit()
            return True
        return False

def update_gift_price(gift_name, new_price):
    with app.app_context():
        gift = Gift.query.filter_by(name=gift_name).first()
        if gift:
            gift.price = new_price
            db.session.commit()
            return True
        return False

def update_premium_price(package_name, new_price):
    with app.app_context():
        package = PremiumPackage.query.filter_by(name=package_name).first()
        if package:
            package.price = new_price
            db.session.commit()
            return True
        return False

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Добавьте этот токен в .env файл
GITHUB_REPO = "pepsil1te/earnstars"
GITHUB_BRANCH = "main"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    bot.reply_to(message, "Привет! Используйте команду /звезды для управления ценами на звезды.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет доступа к админ-панели")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton('💫 Цены на звезды'),
        telebot.types.KeyboardButton('🎁 Цены на подарки')
    )
    markup.add(
        telebot.types.KeyboardButton('👑 Цены на Premium'),
        telebot.types.KeyboardButton('🔙 Назад')
    )
    bot.send_message(
        message.chat.id,
        "Выберите раздел для редактирования цен:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '💫 Цены на звезды' and message.from_user.id == ADMIN_ID)
def edit_star_prices(message):
    with app.app_context():
        packages = StarPackage.query.all()
        response = "Текущие цены на звезды:\n\n"
        for pkg in packages:
            response += f"{pkg.stars} звезд - {pkg.price} руб. (${pkg.usd})\n"
        
        response += "\nДля изменения цены отправьте сообщение в формате:\n"
        response += "звезды [количество] [новая цена] [цена в USD]\n"
        response += "Например: звезды 50 60 0.67"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text == '🎁 Цены на подарки' and message.from_user.id == ADMIN_ID)
def edit_gift_prices(message):
    with app.app_context():
        gifts = Gift.query.all()
        response = "Текущие цены на подарки:\n\n"
        for gift in gifts:
            response += f"{gift.name} - {gift.price} руб.\n"
        
        response += "\nДля изменения цены отправьте сообщение в формате:\n"
        response += "подарок [название] [новая цена]\n"
        response += "Например: подарок Подарок 1 120"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text == '👑 Цены на Premium' and message.from_user.id == ADMIN_ID)
def edit_premium_prices(message):
    with app.app_context():
        packages = PremiumPackage.query.all()
        response = "Текущие пакеты Premium:\n\n"
        for pkg in packages:
            response += f"{pkg.name} - {pkg.price} руб.\n"
        
        response += "\nДля изменения цены отправьте сообщение в формате:\n"
        response += "премиум [название] [новая цена]\n"
        response += "Например: премиум Премиум 1 600"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text == '🔙 Назад' and message.from_user.id == ADMIN_ID)
def back_to_start(message):
    start(message)

@bot.message_handler(func=lambda message: message.text.lower().startswith('звезды '))
def update_stars_price(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 4:
            raise ValueError("Неверный формат команды")
        
        stars = int(parts[1])
        price = float(parts[2])
        usd = float(parts[3])
        
        if update_package_price(stars, price, usd):
            bot.reply_to(message, f"✅ Цена для пакета {stars} звезд обновлена:\n{price} руб. (${usd})")
        else:
            bot.reply_to(message, f"❌ Пакет {stars} звезд не найден")
    
    except ValueError as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}\nИспользуйте формат: звезды [количество] [новая цена] [цена в USD]")
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(func=lambda message: message.text.lower().startswith('подарок '))
def update_gift_price(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат команды")
        
        gift_name = ' '.join(parts[1:-1])
        new_price = float(parts[-1])
        
        if update_gift_price(gift_name, new_price):
            bot.reply_to(message, f"✅ Цена подарка '{gift_name}' обновлена:\n{new_price} руб.")
        else:
            bot.reply_to(message, f"❌ Подарок '{gift_name}' не найден")
    
    except ValueError as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}\nИспользуйте формат: подарок [название] [новая цена]")
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(func=lambda message: message.text.lower().startswith('премиум '))
def update_premium_price(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат команды")
        
        package_name = ' '.join(parts[1:-1])
        new_price = float(parts[-1])
        
        if update_premium_price(package_name, new_price):
            bot.reply_to(message, f"✅ Цена пакета '{package_name}' обновлена:\n{new_price} руб.")
        else:
            bot.reply_to(message, f"❌ Пакет '{package_name}' не найден")
    
    except ValueError as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}\nИспользуйте формат: премиум [название] [новая цена]")
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

if __name__ == '__main__':
    # Запускаем Flask сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Бот запущен! Веб-сервер доступен по адресу http://localhost:5000")
    bot.polling()
