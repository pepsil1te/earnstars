from flask import jsonify, request, render_template
from backend import app, db
from backend.models import User, Transaction, Gift, PremiumSubscription
from backend.utils import generate_token, verify_token, generate_referral_code
from datetime import datetime, timedelta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()
    
    user = User.query.filter_by(telegram_id=data['telegram_id']).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400
    
    user = User(
        telegram_id=data['telegram_id'],
        username=data.get('username'),
        referral_code=generate_referral_code(data['telegram_id'])
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': user.id
    }), 201

@app.route('/api/stars/purchase', methods=['POST'])
def purchase_stars():
    data = request.get_json()
    user = User.query.filter_by(telegram_id=data['user_id']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    transaction = Transaction(
        user_id=user.id,
        amount=data['amount'],
        type='purchase'
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Purchase initiated',
        'transaction_id': transaction.id
    }), 201

@app.route('/api/gifts/send', methods=['POST'])
def send_gift():
    data = request.get_json()
    sender = User.query.filter_by(telegram_id=data['sender_id']).first()
    recipient = User.query.filter_by(telegram_id=data['recipient_id']).first()
    
    if not sender or not recipient:
        return jsonify({'message': 'User not found'}), 404
    
    if sender.balance < data['stars_amount']:
        return jsonify({'message': 'Insufficient balance'}), 400
    
    gift = Gift(
        sender_id=sender.id,
        recipient_id=recipient.id,
        stars_amount=data['stars_amount'],
        gift_type=data['gift_type'],
        message=data.get('message')
    )
    
    sender.balance -= data['stars_amount']
    recipient.balance += data['stars_amount']
    
    db.session.add(gift)
    db.session.commit()
    
    return jsonify({
        'message': 'Gift sent successfully',
        'gift_id': gift.id
    }), 201

@app.route('/api/premium/subscribe', methods=['POST'])
def subscribe_premium():
    data = request.get_json()
    user = User.query.filter_by(telegram_id=data['user_id']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    subscription = PremiumSubscription(
        user_id=user.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    user.is_premium = True
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({
        'message': 'Premium subscription activated',
        'subscription_id': subscription.id
    }), 201
