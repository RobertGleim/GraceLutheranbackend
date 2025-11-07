from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app('DevelopmentConfig')

with app.app_context():
    # Check if admin exists
    admin = db.session.query(User).filter_by(email='admin@gracelutheran.com').first()
    
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@gracelutheran.com',
            password=generate_password_hash('ChangeThisPassword123!'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created successfully!")
        print("Email: admin@gracelutheran.com")
        print("Password: ChangeThisPassword123!")
    else:
        print("⚠️ Admin user already exists")
