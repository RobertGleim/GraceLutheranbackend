from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.users import users_bp
from .blueprints.pastor_messages import pastor_messages_bp
from flask_cors import CORS

def create_app(config_name):
    
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    ma.init_app(app)
    
    # Configure CORS with explicit settings for preflight requests
    CORS(app, 
         resources={r"/*": {
             "origins": ["https://grace-lutheran.vercel.app", "http://localhost:3000", "http://localhost:5173", "https://gracelutheranbacke.onrender.com"],
             "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }})

    # Register blueprints
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(pastor_messages_bp, url_prefix='/pastor-messages')

    return app