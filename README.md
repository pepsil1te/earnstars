# EarnStars - Telegram Mini App

Мини-приложение Telegram для покупки и заработка звезд.

## Функционал

- 🌟 Покупка звезд
- 🎁 Отправка подарков
- 💎 Покупка Telegram Premium
- 👥 Реферальная система
- 📊 История транзакций
- 🌍 Поддержка мультиязычности (RU/EN)

## Технологии

- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- API: Telegram Bot API
- Анимации: Lottie Web

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/pepsil1te/earnstars.git
cd earnstars
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте необходимые переменные окружения:
```
BOT_TOKEN=your_telegram_bot_token
```

4. Запустите сервер:
```bash
python bot.py
```

## Структура проекта

```
earnstars/
├── bot.py           # Backend сервер
├── index.html       # Главная страница
├── app.js          # JavaScript логика
├── styles.css      # Стили
├── gifts/          # JSON и SVG файлы подарков
└── svg/            # SVG иконки
```

## Лицензия

MIT
