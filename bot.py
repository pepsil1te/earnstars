import os
from dotenv import load_dotenv
import telebot
from flask import Flask, request, render_template_string, send_from_directory
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Путь к директории с файлами
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

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

if __name__ == '__main__':
    import threading
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    # Запускаем бота
    print("Бот EarnStars запущен!")
    bot.polling(none_stop=True)
