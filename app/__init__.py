

from flask import Flask
from .models import db


def create_app(config_name):
    
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)

   

    return app