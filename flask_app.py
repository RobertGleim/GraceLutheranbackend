from app import create_app
from app.models import db
from flask_cors import CORS
import os

app = create_app(os.getenv('FLASK_CONFIG', 'DevelopmentConfig'))

# Allow local development and production Vercel frontend
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # Alternate localhost
    "https://grace-lutheran.vercel.app",  # Production Vercel URL
    os.getenv("FRONTEND_URL", "")  # From Render environment variable
]

CORS(app, 
     supports_credentials=True, 
     origins=[origin for origin in allowed_origins if origin],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Ensure OPTIONS is included
     expose_headers=["Content-Type", "Authorization"])

with app.app_context():
    # db.drop_all()  # Uncomment to recreate database
    db.create_all()

if __name__ == '__main__':
    app.run()