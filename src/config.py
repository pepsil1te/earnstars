import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
PRICES_FILE = os.path.join(CONFIG_DIR, 'prices.json')

# Exchange rate (USD to RUB)
USD_RATE = 92.5  # Актуальный курс доллара
