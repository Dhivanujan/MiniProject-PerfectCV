from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.utils.email_utils import send_reset_email
from itsdangerous import URLSafeTimedSerializer

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = current_app.mongo.db.users.find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        user_obj = User(user)
        login_user(user_obj)
        return jsonify({'success': True, 'message': 'Logged in successfully'})
    
    return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if current_app.mongo.db.users.find_one({'email': email}):
        return jsonify({'success': False, 'error': 'Email already registered'}), 400
    
    hashed_password = generate_password_hash(password)
    user_id = current_app.mongo.db.users.insert_one({
        'email': email,
        'password': hashed_password
    }).inserted_id
    
    return jsonify({'success': True, 'message': 'Registered successfully'})

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    user = current_app.mongo.db.users.find_one({'email': email})
    if not user:
        return jsonify({'success': False, 'error': 'Email not found'}), 404
    
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(email, salt='password-reset-salt')
    reset_url = f"{request.host_url}reset-password/{token}"
    
    if send_reset_email(email, reset_url):
        return jsonify({'success': True, 'message': 'Password reset email sent'})
    return jsonify({'success': False, 'error': 'Error sending email'}), 500

@auth.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
        
        data = request.get_json()
        new_password = data.get('password')
        
        current_app.mongo.db.users.update_one(
            {'email': email},
            {'$set': {'password': generate_password_hash(new_password)}}
        )
        
        return jsonify({'success': True, 'message': 'Password reset successfully'})
    except:
        return jsonify({'success': False, 'error': 'Invalid or expired token'}), 400

@auth.route('/logout')
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})