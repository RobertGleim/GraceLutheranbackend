from app import create_app
from app.models import db
from flask_cors import CORS
from flasgger import Swagger

app = create_app('ProductionConfig')
CORS(app)
Swagger(app)  # Add this line to enable Swagger UI

with app.app_context():
    # db.drop_all() for tersting purposes
    db.create_all()


# commented out for testing purposes