import os
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    parent_env = os.path.join(BASE_DIR, '..', '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/perfectcv')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')
    # Frontend base URL used to construct password reset links sent to users.
    # Set this to your frontend origin in production, e.g. https://app.example.com
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173')