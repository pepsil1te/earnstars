import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
    
    # SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///earnstars.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    
    # Rate Limiting
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 3600))
    
    # Payment Gateway
    PAYMENT_GATEWAY_API_KEY = os.getenv('PAYMENT_GATEWAY_API_KEY')
    PAYMENT_GATEWAY_SECRET = os.getenv('PAYMENT_GATEWAY_SECRET')
