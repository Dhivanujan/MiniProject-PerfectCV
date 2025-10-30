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