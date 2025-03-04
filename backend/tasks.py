from backend import celery, mongo, redis_client
from backend.models import Transaction, Gift, User
from datetime import datetime
import logging
from pythonjsonlogger import jsonlogger

# Настройка логирования
logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@celery.task(bind=True, max_retries=3)
def process_payment(self, transaction_id):
    try:
        # Получаем транзакцию из базы
        transaction = mongo.db.transactions.find_one({'_id': transaction_id})
        if not transaction:
            raise Exception(f"Transaction {transaction_id} not found")

        logger.info('Processing payment', extra={
            'transaction_id': transaction_id,
            'amount': transaction['amount'],
            'user_id': transaction['user_id']
        })

        # TODO: Интеграция с платежным шлюзом
        # payment_result = payment_gateway.process_payment(transaction)

        # Обновляем баланс пользователя
        mongo.db.users.update_one(
            {'telegram_id': transaction['user_id']},
            {'$inc': {'balance': transaction['amount']}}
        )

        # Обновляем статус транзакции
        mongo.db.transactions.update_one(
            {'_id': transaction_id},
            {'$set': {
                'status': 'completed',
                'completed_at': datetime.utcnow()
            }}
        )

        logger.info('Payment processed successfully', extra={
            'transaction_id': transaction_id,
            'status': 'completed'
        })

    except Exception as e:
        logger.error('Payment processing failed', extra={
            'transaction_id': transaction_id,
            'error': str(e)
        })
        
        mongo.db.transactions.update_one(
            {'_id': transaction_id},
            {'$set': {
                'status': 'failed',
                'error': str(e)
            }}
        )
        
        raise self.retry(exc=e)

@celery.task(bind=True, max_retries=3)
def send_gift(self, gift_id):
    try:
        # Получаем подарок из базы
        gift = mongo.db.gifts.find_one({'_id': gift_id})
        if not gift:
            raise Exception(f"Gift {gift_id} not found")

        logger.info('Processing gift', extra={
            'gift_id': gift_id,
            'sender_id': gift['sender_id'],
            'recipient_id': gift['recipient_id']
        })

        # Проверяем баланс отправителя
        sender = mongo.db.users.find_one({'telegram_id': gift['sender_id']})
        if sender['balance'] < gift['stars_amount']:
            raise Exception("Insufficient balance")

        # Обновляем балансы отправителя и получателя
        mongo.db.users.update_one(
            {'telegram_id': gift['sender_id']},
            {'$inc': {'balance': -gift['stars_amount']}}
        )
        
        mongo.db.users.update_one(
            {'telegram_id': gift['recipient_id']},
            {'$inc': {'balance': gift['stars_amount']}}
        )

        # Обновляем статус подарка
        mongo.db.gifts.update_one(
            {'_id': gift_id},
            {'$set': {
                'status': 'delivered',
                'delivered_at': datetime.utcnow()
            }}
        )

        logger.info('Gift sent successfully', extra={
            'gift_id': gift_id,
            'status': 'delivered'
        })

    except Exception as e:
        logger.error('Gift sending failed', extra={
            'gift_id': gift_id,
            'error': str(e)
        })
        
        mongo.db.gifts.update_one(
            {'_id': gift_id},
            {'$set': {
                'status': 'failed',
                'error': str(e)
            }}
        )
        
        raise self.retry(exc=e)

@celery.task
def cleanup_expired_sessions():
    """Периодическая задача для очистки устаревших сессий"""
    try:
        current_time = datetime.utcnow()
        redis_client.delete(
            *[key for key in redis_client.scan_iter("session:*")]
        )
        logger.info('Cleaned up expired sessions')
    except Exception as e:
        logger.error('Session cleanup failed', extra={'error': str(e)})
