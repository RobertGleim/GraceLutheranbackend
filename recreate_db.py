"""
Script to recreate all database tables
WARNING: This will delete all existing data!
Run with: python recreate_db.py
"""
from app import create_app, db

def recreate_database():
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("✓ Database recreated successfully!")

if __name__ == '__main__':
    recreate_database()
