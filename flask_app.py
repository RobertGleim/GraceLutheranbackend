from app import create_app
from app.models import db
from flask_cors import CORS

app = create_app('ProductionConfig')
CORS(app)

with app.app_context():
    # db.drop_all() for tersting purposes
    db.create_all()

