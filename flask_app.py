from app import create_app
from app.models import db
from flask_cors import CORS

app = create_app('DevelopmentConfig')
CORS(app)

with app.app_context():
    # db.drop_all() for tersting purposes
    db.create_all()

import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)