from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.utils.email_utils import send_reset_email, send_reset_code_email
from itsdangerous import URLSafeTimedSerializer
from flask import url_for, redirect, request
from datetime import datetime, timedelta
import random
from bson import ObjectId

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
    # Generate 6-digit code and store an entry in password_resets collection
    code = f"{random.randint(0, 999999):06d}"
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=15)

    reset_doc = {
        'email': email,
        'code': code,
        'created_at': now,
        'expires_at': expires_at,
        'attempts': 0,
        'used': False,
        'verified': False
    }
    try:
        inserted = current_app.mongo.db.password_resets.insert_one(reset_doc)
        sent = send_reset_code_email(email, code)
        
        if not sent:
            # If email fails, check if we are in debug mode to help developer
            if current_app.config.get('DEBUG') or current_app.config.get('ENV') == 'development':
                current_app.logger.info(f"DEBUG MODE: Password reset code for {email} is {code}")
                # We still return error to frontend, but developer can see code in terminal
                # Alternatively, we could return it in response for dev convenience:
                # return jsonify({'success': True, 'message': 'Reset code sent (DEBUG: check console)', 'debug_code': code}), 200
            
            # cleanup the reset doc on failure to send (unless we want to allow manual code entry from logs)
            # For now, let's keep it strict: if email fails, process fails.
            current_app.mongo.db.password_resets.delete_one({'_id': inserted.inserted_id})
            return jsonify({'success': False, 'error': 'Failed to send reset email. Please check system configuration.'}), 500

        return jsonify({'success': True, 'message': 'Reset code sent to email'}), 200
    except Exception:
        current_app.logger.exception('Error creating password reset code')
        return jsonify({'success': False, 'error': 'Server error creating reset code'}), 500

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


@auth.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """Verify the 6-digit code sent to user's email. Returns a short-lived reset token on success."""
    data = request.get_json() or {}
    email = data.get('email')
    code = (data.get('code') or '').strip()

    if not email or not code:
        return jsonify({'success': False, 'error': 'Email and code are required'}), 400

    try:
        # Find most recent unused reset doc
        reset_doc = current_app.mongo.db.password_resets.find_one(
            {'email': email, 'used': False}, sort=[('created_at', -1)])
        if not reset_doc:
            return jsonify({'success': False, 'error': 'No reset request found'}), 404

        now = datetime.utcnow()
        # check expiry
        if reset_doc.get('expires_at') and now > reset_doc['expires_at']:
            return jsonify({'success': False, 'error': 'Reset code has expired'}), 400

        # Check attempt limits
        attempts = reset_doc.get('attempts', 0)
        if attempts >= 5:
            # mark as used to block further attempts
            current_app.mongo.db.password_resets.update_one({'_id': reset_doc['_id']}, {'$set': {'used': True}})
            return jsonify({'success': False, 'error': 'Too many invalid attempts'}), 403

        if code != reset_doc.get('code'):
            current_app.mongo.db.password_resets.update_one({'_id': reset_doc['_id']}, {'$inc': {'attempts': 1}})
            return jsonify({'success': False, 'error': 'Invalid code'}), 400

        # Mark verified and produce a signed reset token referencing this reset doc id
        current_app.mongo.db.password_resets.update_one(
            {'_id': reset_doc['_id']},
            {'$set': {'verified': True, 'verified_at': now}}
        )

        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        reset_token = s.dumps(str(reset_doc['_id']), salt='password-reset-salt')
        # Build a frontend reset link if frontend URL is configured (helps reliable navigation)
        frontend_base = current_app.config.get('FRONTEND_URL') or request.host_url.rstrip('/')
        reset_link = f"{frontend_base.rstrip('/')}/reset-password/{reset_token}"
        current_app.logger.info(f"Generated reset token for {email}")
        return jsonify({'success': True, 'reset_token': reset_token, 'reset_link': reset_link}), 200

    except Exception:
        current_app.logger.exception('Error verifying reset code')
        return jsonify({'success': False, 'error': 'Server error during verification'}), 500


@auth.route('/reset-password', methods=['POST'])
def reset_password_with_token():
    """Reset password using reset_token returned from verify endpoint."""
    data = request.get_json() or {}
    reset_token = data.get('reset_token')
    new_password = data.get('password')

    if not reset_token or not new_password:
        return jsonify({'success': False, 'error': 'Token and new password are required'}), 400

    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        reset_doc_id = s.loads(reset_token, salt='password-reset-salt', max_age=900)  # 15 minutes
        # find reset doc
        try:
            rid = ObjectId(reset_doc_id)
        except Exception:
            # maybe already a string id
            rid = ObjectId(reset_doc_id)

        reset_doc = current_app.mongo.db.password_resets.find_one({'_id': rid})
        if not reset_doc:
            return jsonify({'success': False, 'error': 'Invalid reset token'}), 400

        if reset_doc.get('used'):
            return jsonify({'success': False, 'error': 'Reset token already used'}), 400

        if not reset_doc.get('verified'):
            return jsonify({'success': False, 'error': 'Reset token not verified'}), 400

        now = datetime.utcnow()
        if reset_doc.get('expires_at') and now > reset_doc['expires_at']:
            return jsonify({'success': False, 'error': 'Reset code expired'}), 400

        # update user's password
        current_app.mongo.db.users.update_one(
            {'email': reset_doc['email']},
            {'$set': {'password': generate_password_hash(new_password)}}
        )

        # mark reset doc used and set used_at
        current_app.mongo.db.password_resets.update_one({'_id': rid}, {'$set': {'used': True, 'used_at': now}})

        return jsonify({'success': True, 'message': 'Password reset successfully'})
    except Exception:
        current_app.logger.exception('Error resetting password with token')
        return jsonify({'success': False, 'error': 'Server error during password reset'}), 500

@auth.route('/logout')
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})