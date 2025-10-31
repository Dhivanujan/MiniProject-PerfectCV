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

    # Send contact email
    sent = send_contact_email(name, email, message)
    if not sent:
        return jsonify({'status': 'error', 'message': 'Failed to send message. Try again later.'}), 503

    saved = False
    # Optionally save to MongoDB if available
    try:
        if hasattr(current_app, 'mongo') and getattr(current_app, 'mongo') is not None:
            try:
                current_app.mongo.db.contacts.insert_one({'name': name, 'email': email, 'message': message})
                saved = True
            except Exception as e:
                current_app.logger.warning('Could not save contact message to DB: %s', e)
    except Exception:
        # Defensive: don't let storage issues affect response
        current_app.logger.debug('Mongo not available to save contact message.')

    return jsonify({'status': 'ok', 'saved': saved}), 200
