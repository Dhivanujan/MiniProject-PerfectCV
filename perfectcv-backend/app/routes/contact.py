from flask import Blueprint, request, jsonify, current_app
import re
from app.utils.email_utils import send_contact_email

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact', methods=['POST'])
def contact():
    """Accepts JSON payload with `name`, `email`, `message` and forwards it to support.

    - Validates required fields.
    - Sends email using configured Flask-Mail instance.
    - Attempts to store the message in MongoDB if available (non-fatal).
    """
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    if not name or not email or not message:
        return jsonify({'status': 'error', 'message': 'Missing name, email or message.'}), 400

    # Simple email format check
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'status': 'error', 'message': 'Invalid email address.'}), 400

    saved = False
    # 1. Attempt to save to MongoDB first (so we don't lose the message if email fails)
    try:
        if hasattr(current_app, 'mongo') and getattr(current_app, 'mongo') is not None:
            try:
                current_app.mongo.db.contacts.insert_one({'name': name, 'email': email, 'message': message})
                saved = True
            except Exception as e:
                current_app.logger.warning('Could not save contact message to DB: %s', e)
    except Exception:
        current_app.logger.debug('Mongo not available to save contact message.')

    # 2. Send contact email
    sent = send_contact_email(name, email, message)
    
    if not sent and not saved:
        # Both failed
        return jsonify({'status': 'error', 'message': 'Failed to send message. Please try again later.'}), 503
    
    if not sent and saved:
        # Email failed but saved to DB. We can consider this a partial success.
        # We'll tell the user it was sent (or received) so they don't retry endlessly.
        current_app.logger.warning(f"Contact message from {email} saved to DB but email sending failed.")
        return jsonify({'status': 'ok', 'saved': True, 'email_sent': False, 'message': 'Message received.'}), 200

    return jsonify({'status': 'ok', 'saved': saved, 'email_sent': True}), 200
