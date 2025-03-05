import os
import json
from dotenv import load_dotenv
import telebot
from flask import Flask, request, render_template_string, send_from_directory, jsonify
from flask_cors import CORS
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))  # ID администратора

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
CORS(app)  # Включаем CORS для всех routes

# Путь к директории с файлами
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PRICES_FILE = os.path.join(CURRENT_DIR, 'config', 'prices.json')

def load_prices():
    with open(PRICES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_prices(prices):
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return send_from_directory(CURRENT_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory(CURRENT_DIR, filename)

@app.route('/webapp')
def webapp():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>EarnStars</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--tg-theme-bg-color, #1d2733);
                color: var(--tg-theme-text-color, #ffffff);
                margin: 0;
                padding: 16px;
            }
            .header {
                display: flex;
                align-items: center;
                padding: 10px;
                border-bottom: 1px solid var(--tg-theme-hint-color, #454545);
            }
            .profile {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .profile-pic {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #4CAF50;
            }
            .button {
                display: block;
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                border-radius: 8px;
                border: none;
                background-color: var(--tg-theme-button-color, #3390ec);
                color: var(--tg-theme-button-text-color, #ffffff);
                cursor: pointer;
                text-align: center;
                text-decoration: none;
            }
            .secondary-button {
                background-color: var(--tg-theme-secondary-bg-color, #232e3c);
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="profile">
                <div class="profile-pic"></div>
                <span id="username">@username</span>
            </div>
            <div style="margin-left: auto;">
                <span>RU</span>
            </div>
        </div>

        <a href="#" class="button" onclick="buyStars()">Купить звёзды</a>
        <a href="#" class="button" onclick="sellStars()">Продать звёзды</a>
        <a href="#" class="button secondary-button" onclick="buyGift()">Купить подарок</a>
        <a href="#" class="button secondary-button" onclick="buyPremium()">Купить Telegram Premium</a>
        <a href="#" class="button secondary-button" onclick="showTransactions()">Список транзакций</a>
        <a href="#" class="button secondary-button" onclick="subscribeChannel()">Подписаться на канал</a>
        <a href="#" class="button secondary-button" onclick="contactSupport()">Написать в поддержку</a>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();
            
            // Получаем имя пользователя
            document.getElementById('username').textContent = tg.initDataUnsafe.user?.username || '@user';

            function buyStars() {
                // Здесь будет логика покупки звёзд
                tg.showAlert('Функция покупки звёзд');
            }

            function sellStars() {
                // Здесь будет логика продажи звёзд
                tg.showAlert('Функция продажи звёзд');
            }

            function buyGift() {
                tg.showAlert('Функция покупки подарка');
            }

            function buyPremium() {
                tg.showAlert('Переход к покупке Telegram Premium');
            }

            function showTransactions() {
                tg.showAlert('Показ списка транзакций');
            }

            function subscribeChannel() {
                tg.showAlert('Переход к подписке на канал');
            }

            function contactSupport() {
                tg.showAlert('Переход в поддержку');
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/prices')
def get_prices():
    try:
        with open('config/prices.json', 'r', encoding='utf-8') as f:
            prices = json.load(f)
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="Открыть EarnStars",
        web_app=WebAppInfo(url="https://pepsil1te.github.io/earnstars/")
    ))
    
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в EarnStars! Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=markup
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет доступа к админ-панели")
        return
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton('💫 Цены на звезды'),
        KeyboardButton('🎁 Цены на подарки')
    )
    markup.add(
        KeyboardButton('👑 Цены на Premium'),
        KeyboardButton('🔙 Назад')
    )
    bot.send_message(
        message.chat.id,
        "Выберите раздел для редактирования цен:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '💫 Цены на звезды' and message.from_user.id == ADMIN_ID)
def edit_star_prices(message):
    prices = load_prices()
    text = "Текущие пакеты звезд:\n\n"
    for i, package in enumerate(prices['stars']['packages'], 1):
        text += f"{i}. {package['stars']} звезд - {package['price']}₽ (${package['usd']})\n"
    
    text += "\nДля изменения цены отправьте:\n"
    text += "звезды <номер_пакета> <новая_цена>\n"
    text += "Например: звезды 1 60"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == '🎁 Цены на подарки' and message.from_user.id == ADMIN_ID)
def edit_gift_prices(message):
    prices = load_prices()
    text = "Текущие цены на подарки:\n\n"
    for i, (gift_id, gift) in enumerate(prices['gifts'].items(), 1):
        text += f"{i}. {gift['name']} - {gift['price']}₽\n"
    
    text += "\nДля изменения цены отправьте:\n"
    text += "подарок <номер> <новая_цена>\n"
    text += "Например: подарок 1 120"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == '👑 Цены на Premium' and message.from_user.id == ADMIN_ID)
def edit_premium_prices(message):
    prices = load_prices()
    text = "Текущие пакеты Premium:\n\n"
    for i, package in enumerate(prices['premium']['packages'], 1):
        text += f"{i}. {package['name']} - {package['price']}₽\n"
    
    text += "\nДля изменения цены отправьте:\n"
    text += "премиум <номер_пакета> <новая_цена>\n"
    text += "Например: премиум 1 600"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text.startswith(('звезды ', 'подарок ', 'премиум ')) and message.from_user.id == ADMIN_ID)
def update_prices(message):
    try:
        prices = load_prices()
        parts = message.text.split()
        
        if parts[0] == 'звезды' and len(parts) == 3:
            idx = int(parts[1]) - 1
            new_price = int(parts[2])
            if 0 <= idx < len(prices['stars']['packages']):
                old_price = prices['stars']['packages'][idx]['price']
                prices['stars']['packages'][idx]['price'] = new_price
                prices['stars']['packages'][idx]['usd'] = round(new_price / 92.5, 2)  # Актуальный курс
                save_prices(prices)
                bot.reply_to(message, f"✅ Цена пакета {prices['stars']['packages'][idx]['stars']} звезд изменена с {old_price}₽ на {new_price}₽ (${prices['stars']['packages'][idx]['usd']})")
            else:
                bot.reply_to(message, "❌ Неверный номер пакета")
        
        elif parts[0] == 'подарок' and len(parts) == 3:
            idx = int(parts[1]) - 1
            new_price = int(parts[2])
            gifts = list(prices['gifts'].items())
            if 0 <= idx < len(gifts):
                gift_id, gift = gifts[idx]
                old_price = gift['price']
                gift['price'] = new_price
                prices['gifts'][gift_id] = gift
                save_prices(prices)
                bot.reply_to(message, f"✅ Цена подарка {gift['name']} изменена с {old_price}₽ на {new_price}₽")
            else:
                bot.reply_to(message, "❌ Неверный номер подарка")
    
    except (ValueError, IndexError):
        bot.reply_to(message, "❌ Неверный формат команды")

@bot.message_handler(func=lambda message: message.text == '🔙 Назад' and message.from_user.id == ADMIN_ID)
def back_to_start(message):
    start(message)

if __name__ == '__main__':
    import threading
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    # Запускаем бота
    print("Бот EarnStars запущен!")
    bot.polling(none_stop=True)
