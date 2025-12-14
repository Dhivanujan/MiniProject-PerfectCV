from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from config.config import Config
from app.models.user import User
from app.routes.auth import auth
from app.routes.chatbot import chatbot
from app.routes.contact import contact_bp
from bson import ObjectId

mongo = PyMongo()
login_manager = LoginManager()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    try:
        oid = ObjectId(user_id)
    except Exception:
        # If conversion fails, try using raw id (some setups may store string ids)
        oid = user_id
    user_data = mongo.db.users.find_one({'_id': oid})
    return User(user_data) if user_data else None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    # Allow credentials so frontend can send cookies/sessions when needed
    CORS(app, supports_credentials=True)
    
    # Initialize MongoDB with connection timeout handling
    try:
        # Add timeout parameters to MONGO_URI if using Atlas
        mongo_uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/perfectcv')
        if 'mongodb+srv://' in mongo_uri or 'mongodb.net' in mongo_uri:
            # Add timeout parameters for Atlas connections
            separator = '&' if '?' in mongo_uri else '?'
            mongo_uri += f'{separator}connectTimeoutMS=5000&serverSelectionTimeoutMS=5000&socketTimeoutMS=5000'
            app.config['MONGO_URI'] = mongo_uri
            app.logger.info("Using MongoDB Atlas with timeout settings")
        else:
            app.logger.info("Using local MongoDB")
        
        mongo.init_app(app)
        # Test connection
        try:
            mongo.cx.admin.command('ping')
            app.logger.info("✓ MongoDB connection successful")
        except Exception as e:
            app.logger.warning(f"⚠ MongoDB connection failed: {e}")
            app.logger.warning("Application will start but database operations may fail")
    except Exception as e:
        app.logger.error(f"❌ MongoDB initialization error: {e}")
        app.logger.warning("Continuing without MongoDB - some features may not work")
    
    login_manager.init_app(app)
    mail.init_app(app)
    # Attach initialized extensions to the app instance so routes can access them
    app.mongo = mongo
    app.mail = mail
    app.login_manager = login_manager
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    # Register chatbot under /api/chatbot for clearer routing
    app.register_blueprint(chatbot, url_prefix='/api/chatbot')
    # contact form endpoint
    app.register_blueprint(contact_bp, url_prefix='/api')
    # file management routes
    from app.routes.files import files_bp
    app.register_blueprint(files_bp, url_prefix='/api')
    
    # Quick startup DB check (non-fatal) and health endpoint
    # Note: Skipping ping on startup to avoid blocking. Health endpoint will check connection.
    app.config['MONGO_OK'] = True  # Assume OK, let health endpoint verify
    app.logger.info("MongoDB connection will be verified on first request")

    @app.route('/health')
    def health():
        """Simple health endpoint. Returns overall OK and mongo status."""
        mongo_ok = False
        try:
            app.mongo.db.command("ping", maxTimeMS=1000)
            mongo_ok = True
        except Exception:
            pass
        
        ok = True
        status = {'ok': ok, 'mongo': mongo_ok}
        return (jsonify(status), 200) if mongo_ok else (jsonify(status), 503)
    
    return app