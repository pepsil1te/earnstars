import jwt
from datetime import datetime, timedelta
from backend import app
import hashlib

def generate_token(user_id: int) -> str:
    """Генерирует JWT токен для пользователя"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token: str) -> dict:
    """Проверяет JWT токен и возвращает payload"""
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def generate_referral_code(user_id: int) -> str:
    """Генерирует реферальный код для пользователя"""
    base = f"{user_id}:{datetime.utcnow().timestamp()}"
    return hashlib.md5(base.encode()).hexdigest()[:8]

def calculate_referral_reward(amount: float) -> float:
    """Рассчитывает награду за реферала"""
    return amount * 0.1  # 10% от суммы
