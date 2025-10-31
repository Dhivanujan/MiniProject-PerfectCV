from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.utils.email_utils import send_reset_email
from itsdangerous import URLSafeTimedSerializer
from flask import url_for, redirect, request

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
        # Return a minimal user representation to the frontend
        user_public = {
            'id': str(user.get('_id')),
            'email': user.get('email'),
            'full_name': user.get('full_name'),
            'username': user.get('username')
        }
        return jsonify({'success': True, 'message': 'Logged in successfully', 'user': user_public})
    
    return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400

    try:
        # Check existing user
        if current_app.mongo.db.users.find_one({'email': email}):
            return jsonify({'success': False, 'error': 'Email already registered'}), 400

        hashed_password = generate_password_hash(password)

        # Store any other provided fields (optional)
        user_doc = {
            'email': email,
            'password': hashed_password,
        }
        # Add optional fields if present
        for key in ('full_name', 'username', 'phone'):
            if data.get(key):
                user_doc[key] = data.get(key)

        inserted = current_app.mongo.db.users.insert_one(user_doc)
        return jsonify({'success': True, 'message': 'Registered successfully', 'user_id': str(inserted.inserted_id)})
    except Exception as e:
        current_app.logger.exception('Error during user registration')
        return jsonify({'success': False, 'error': 'Server error during registration', 'details': str(e)}), 500

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    user = current_app.mongo.db.users.find_one({'email': email})
    if not user:
        return jsonify({'success': False, 'error': 'Email not found'}), 404
    
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(email, salt='password-reset-salt')
    # Construct link to frontend reset page (frontend will POST the new password to backend)
    frontend_base = current_app.config.get('FRONTEND_URL', request.host_url.rstrip('/'))
    reset_url = f"{frontend_base.rstrip('/')}/reset-password/{token}"
    
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


@auth.route('/reset-password/<token>', methods=['GET'])
def reset_password_redirect(token):
    """Redirect GET requests to the frontend reset page so clicking links from email works.

    The frontend will render the form and POST the new password to the backend endpoint.
    """
    frontend_base = current_app.config.get('FRONTEND_URL') or request.host_url.rstrip('/')
    redirect_url = f"{frontend_base.rstrip('/')}/reset-password/{token}"
    return redirect(redirect_url, code=302)

@auth.route('/logout')
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})