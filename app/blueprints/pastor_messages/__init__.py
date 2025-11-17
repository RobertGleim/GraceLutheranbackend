from flask import Blueprint

pastor_messages_bp = Blueprint('pastor_messages', __name__, url_prefix='/pastor-messages')

from . import routes
