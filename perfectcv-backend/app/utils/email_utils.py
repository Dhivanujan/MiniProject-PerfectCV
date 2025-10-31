from flask_mail import Message
from flask import current_app

def send_reset_email(user_email, reset_url):
    msg = Message('Password Reset Request',
                  sender='noreply@perfectcv.com',
                  recipients=[user_email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    try:
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False


def send_contact_email(name, sender_email, message_body):
    """Send a contact message to the configured support address.

    Returns True on success, False on failure.
    """
    # Destination: prefer configured MAIL_USERNAME or fallback to support@perfectcv.com
    recipient = current_app.config.get('MAIL_USERNAME') or 'support@perfectcv.com'
    subject = f"New contact message from {name}"
    body = f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_body}\n"
    msg = Message(subject, sender=recipient, recipients=[recipient])
    msg.body = body
    try:
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending contact email: {str(e)}")
        return False