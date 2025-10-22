from app import create_app
from app.models import db

app = create_app('DevelopmentConfig')

with app.app_context():
    # db.drop_all() for tersting purposes
    db.create_all()

app.run()