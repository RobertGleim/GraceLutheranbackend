from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.users import users_bp
from .blueprints.pastor_messages import pastor_messages_bp
from flask_cors import CORS

def create_app(config_name='DevelopmentConfig'):
    
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

    with app.app_context():
        db.create_all()
        initialize_default_admin()
    
    return app


def initialize_default_admin():
    """Create default admin user if it doesn't exist"""
    from app.models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(email="admin@email.com").first()
    if not admin:
        default_admin = User(
            username="admin",
            email="admin@email.com",
            password=generate_password_hash("admin123!"),
            role="admin"
        )
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin user created successfully")