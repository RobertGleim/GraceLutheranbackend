"""
Script to reset admin password.
Run with: python reset_admin.py
"""
import os
from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

def reset_admin():
    # Determine which config to use
    config_name = os.getenv('FLASK_ENV', 'DevelopmentConfig')
    if config_name == 'production':
        config_name = 'ProductionConfig'
    
    app = create_app(config_name)
    
    with app.app_context():
        # Find admin user by email
        admin = db.session.query(User).filter_by(email="admin@email.com").first()
        
        if admin:
            # Update password
            new_password = "admin123!"
            admin.password = generate_password_hash(new_password)
            db.session.commit()
            print("=" * 50)
            print("✓ Admin password has been reset!")
            print("=" * 50)
            print(f"Email:    {admin.email}")
            print(f"Username: {admin.username}")
            print(f"Password: {new_password}")
            print("=" * 50)
        else:
            print("=" * 50)
            print("✗ Admin user not found!")
            print("Creating new admin user...")
            print("=" * 50)
            
            admin = User(
                username="admin",
                email="admin@email.com",
                password=generate_password_hash("admin123!"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            
            print("=" * 50)
            print("✓ New admin user created!")
            print("=" * 50)
            print(f"Email:    admin@email.com")
            print(f"Username: admin")
            print(f"Password: admin123!")
            print("=" * 50)
            

if __name__ == "__main__":
    reset_admin()
