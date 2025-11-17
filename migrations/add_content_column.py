"""
Migration script to add content column to pastor_messages table
Run this with: python migrations/add_content_column.py
"""
from app import create_app, db
from sqlalchemy import text

def upgrade():
    """Add content column to pastor_messages table"""
    app = create_app()
    with app.app_context():
        try:
            # Add the content column
            db.session.execute(text(
                'ALTER TABLE pastor_messages ADD COLUMN content TEXT'
            ))
            db.session.commit()
            print("✓ Successfully added 'content' column to pastor_messages table")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding column: {e}")

if __name__ == '__main__':
    upgrade()
