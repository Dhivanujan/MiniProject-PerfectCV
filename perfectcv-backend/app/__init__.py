from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from config.config import Config
from app.models.user import User
from app.routes.auth import auth
from app.routes.chatbot import chatbot

mongo = PyMongo()
login_manager = LoginManager()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': user_id})
    return User(user_data) if user_data else None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    mongo.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(chatbot, url_prefix='/api')
    
    return app