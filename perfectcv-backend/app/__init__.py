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
    mongo.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    # Attach initialized extensions to the app instance so routes can access them
    app.mongo = mongo
    app.mail = mail
    app.login_manager = login_manager
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(chatbot, url_prefix='/api')
    # contact form endpoint
    app.register_blueprint(contact_bp, url_prefix='/api')
    # file management routes
    from app.routes.files import files_bp
    app.register_blueprint(files_bp, url_prefix='/api')
    
    # Quick startup DB check (non-fatal) and health endpoint
    try:
        # Attempt a lightweight ping to MongoDB
        app.mongo.db.command("ping")
        app.logger.info("MongoDB connection: OK")
        app.config['MONGO_OK'] = True
    except Exception as e:
        app.logger.warning("MongoDB connection: FAILED (%s)", e)
        app.config['MONGO_OK'] = False

    @app.route('/health')
    def health():
        """Simple health endpoint. Returns overall OK and mongo status."""
        ok = True
        mongo_ok = app.config.get('MONGO_OK', False)
        status = {'ok': ok, 'mongo': mongo_ok}
        return (jsonify(status), 200) if mongo_ok else (jsonify(status), 503)
    
    return app