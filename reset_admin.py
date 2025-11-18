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
        # Use environment variables or defaults
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@email.com')
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        new_password = os.getenv('ADMIN_PASSWORD', 'admin123!')
        
        # Find admin user by email (case-insensitive)
        admin = db.session.query(User).filter(db.func.lower(User.email) == admin_email.lower()).first()
        
        if admin:
            # Update password
            admin.password = generate_password_hash(new_password)
            admin.username = admin_username  # Update username too
            admin.role = 'admin'  # Ensure role is admin
            db.session.commit()
            print("=" * 50)
            print("✓ Admin password has been reset!")
            print("=" * 50)
            print(f"Email:    {admin.email}")
            print(f"Username: {admin.username}")
            print(f"Password: {new_password}")
            print(f"Role:     {admin.role}")
            print("=" * 50)
        else:
            print("=" * 50)
            print("✗ Admin user not found!")
            print("Creating new admin user...")
            print("=" * 50)
            
            admin = User(
                username=admin_username,
                email=admin_email,
                password=generate_password_hash(new_password),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            
            print("=" * 50)
            print("✓ New admin user created!")
            print("=" * 50)
            print(f"Email:    {admin_email}")
            print(f"Username: {admin_username}")
            print(f"Password: {new_password}")
            print(f"Role:     admin")
            print("=" * 50)
            

if __name__ == "__main__":
    reset_admin()
