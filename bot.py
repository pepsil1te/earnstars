import os
import json
import base64
import requests
from dotenv import load_dotenv
import telebot
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Добавьте этот токен в .env файл
GITHUB_REPO = "pepsil1te/earnstars"
GITHUB_BRANCH = "main"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
CORS(app, resources={
    r"/prices": {
        "origins": ["https://pepsil1te.github.io", "http://127.0.0.1:5000", "http://localhost:5000"],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Путь к директории с файлами
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PRICES_FILE = os.path.join(CURRENT_DIR, 'config', 'prices.json')

def load_prices():
    with open(PRICES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_github_file(prices):
    """Обновляет файл prices.json в GitHub репозитории"""
    if not GITHUB_TOKEN:
        return False, "GitHub токен не настроен"

    try:
        # Путь к файлу в репозитории
        file_path = "config/prices.json"
        
        # API endpoint для GitHub
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
        
        # Заголовки для авторизации
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Получаем текущий файл, чтобы узнать его SHA
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return False, f"Ошибка получения файла: {response.status_code}"
        
        current_file = response.json()
        
        # Кодируем новое содержимое в base64
        content = json.dumps(prices, ensure_ascii=False, indent=4)
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        # Данные для обновления
        data = {
            "message": "Обновление цен через бота",
            "content": content_base64,
            "sha": current_file["sha"],
            "branch": GITHUB_BRANCH
        }
        
        # Отправляем обновление
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return True, "Цены успешно обновлены в GitHub"
        else:
            return False, f"Ошибка обновления файла: {response.status_code}"
            
    except Exception as e:
        return False, f"Ошибка при обновлении GitHub: {str(e)}"

def save_prices(prices):
    """Сохраняет цены локально и в GitHub"""
    # Сохраняем локально
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices, f, ensure_ascii=False, indent=4)
    
    # Обновляем в GitHub
    success, message = update_github_file(prices)
    return success, message

def get_usd_rate():
    """Получает актуальный курс USD/RUB"""
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        if response.ok:
            data = response.json()
            return data['Valute']['USD']['Value']
    except:
        # Если не удалось получить курс, используем фиксированный
        return 92.5

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

@app.route('/prices', methods=['GET'])
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

@bot.message_handler(func=lambda message: message.text == "💫 Цены на звезды")
def edit_star_prices(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    prices = load_prices()
    packages = prices['stars']['packages']
    
    response = "Текущие цены на звезды:\n\n"
    for pkg in packages:
        response += f"{pkg['stars']} звезд = {pkg['price']}₽ (~{pkg['usd']}$)\n"
    
    response += "\nДля изменения цены отправьте сообщение в формате:\n"
    response += "звезды <номер_пакета> <цена>\n"
    response += "Например: звезды 2 60"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('звезды '))
def update_star_price(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        # Разбираем команду
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Неверный формат команды\n\nИспользуйте формат:\nзвезды <номер_пакета> <цена>\nНапример: звезды 2 60")
            return
            
        try:
            package_num = int(parts[1])
            price = int(parts[2])
        except ValueError:
            bot.reply_to(message, "❌ Номер пакета и цена должны быть числами")
            return
            
        # Загружаем текущие цены
        prices = load_prices()
        packages = prices['stars']['packages']
        
        # Проверяем существование пакета
        if package_num < 1 or package_num > len(packages):
            bot.reply_to(message, f"❌ Ошибка: пакет с номером {package_num} не существует.\nДоступны пакеты с 1 по {len(packages)}")
            return
            
        # Получаем актуальный курс и считаем цену в USD
        usd_rate = get_usd_rate()
        usd = round(price / usd_rate, 2)
        
        # Обновляем выбранный пакет
        package = packages[package_num - 1]
        old_price = package['price']
        old_usd = package['usd']
        package['price'] = price
        package['usd'] = usd
        
        # Сохраняем изменения
        success, github_message = save_prices(prices)
        
        if success:
            response = f"✅ Цена обновлена для пакета #{package_num} ({package['stars']} звезд):\n"
            response += f"Старая цена: {old_price}₽ (~{old_usd}$)\n"
            response += f"Новая цена: {price}₽ (~{usd}$)\n"
            response += f"Текущий курс: {usd_rate}₽ за $1\n\n"
            response += github_message
        else:
            response = f"❌ Ошибка при сохранении:\n{github_message}"
        
        bot.reply_to(message, response)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "🎁 Цены на подарки")
def edit_gift_prices(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    prices = load_prices()
    gifts = prices['gifts']
    
    response = "Текущие цены на подарки:\n\n"
    for i, (gift_id, gift) in enumerate(gifts.items(), 1):
        response += f"{i}. {gift['name']} = {gift['price']}₽\n"
    
    response += "\nДля изменения цены отправьте сообщение в формате:\n"
    response += "подарок <номер> <цена>\n"
    response += "Например: подарок 1 200"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('подарок '))
def update_gift_price(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        # Разбираем команду
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Неверный формат команды\n\nИспользуйте формат:\nподарок <номер> <цена>\nНапример: подарок 1 200")
            return
            
        gift_num = int(parts[1])
        new_price = int(parts[2])
        
        # Загружаем текущие цены
        prices = load_prices()
        gifts = list(prices['gifts'].items())
        
        if gift_num < 1 or gift_num > len(gifts):
            bot.reply_to(message, f"❌ Номер подарка должен быть от 1 до {len(gifts)}")
            return
        
        # Получаем id и данные подарка
        gift_id, gift_data = gifts[gift_num - 1]
        old_price = gift_data['price']
        
        # Обновляем цену
        prices['gifts'][gift_id]['price'] = new_price
        
        # Сохраняем изменения
        success, github_message = save_prices(prices)
        
        if success:
            response = f"✅ Цена подарка '{gift_data['name']}' изменена:\n"
            response += f"Старая цена: {old_price}₽\n"
            response += f"Новая цена: {new_price}₽\n\n"
            response += github_message
        else:
            response = f"❌ Ошибка при сохранении:\n{github_message}"
        
        bot.reply_to(message, response)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "👑 Цены на Premium")
def edit_premium_prices(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    prices = load_prices()
    packages = prices['premium']['packages']
    
    response = "Текущие пакеты Premium:\n\n"
    for i, pkg in enumerate(packages, 1):
        response += f"{i}. {pkg['name']} = {pkg['price']}₽\n"
    
    response += "\nДля изменения цены отправьте сообщение в формате:\n"
    response += "премиум <номер> <цена>\n"
    response += "Например: премиум 1 500"
    
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text.startswith('премиум '))
def update_premium_price(message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        # Разбираем команду
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Неверный формат команды\n\nИспользуйте формат:\nпремиум <номер> <цена>\nНапример: премиум 1 500")
            return
            
        pkg_num = int(parts[1])
        new_price = int(parts[2])
        
        # Загружаем текущие цены
        prices = load_prices()
        packages = prices['premium']['packages']
        
        if pkg_num < 1 or pkg_num > len(packages):
            bot.reply_to(message, f"❌ Номер пакета должен быть от 1 до {len(packages)}")
            return
        
        # Получаем данные пакета
        package = packages[pkg_num - 1]
        old_price = package['price']
        
        # Обновляем цену
        package['price'] = new_price
        
        # Сохраняем изменения
        success, github_message = save_prices(prices)
        
        if success:
            response = f"✅ Цена пакета '{package['name']}' изменена:\n"
            response += f"Старая цена: {old_price}₽\n"
            response += f"Новая цена: {new_price}₽\n\n"
            response += github_message
        else:
            response = f"❌ Ошибка при сохранении:\n{github_message}"
        
        bot.reply_to(message, response)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(func=lambda message: message.text == '🔙 Назад' and message.from_user.id == ADMIN_ID)
def back_to_start(message):
    start(message)

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Запускаем Flask сервер в отдельном потоке
    from threading import Thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True  # Поток завершится вместе с основной программой
    flask_thread.start()
    
    # Запускаем бота
    print("Бот запущен! Веб-сервер доступен по адресу http://localhost:5000")
    bot.polling()
