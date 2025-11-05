from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required
from .schemas import pastor_message_schema, pastor_messages_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import pastor_messages_bp
from app.models import PastorMessage


@pastor_messages_bp.route('', methods=['POST'])
@token_required
def create_message():
    """Create a new pastor message (admin only)"""
    try:
        data = pastor_message_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    
    if data.get('is_active', True):
        db.session.query(PastorMessage).update({'is_active': False})
    
    new_message = PastorMessage(**data)
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "message": "Pastor message created successfully.",
        "data": pastor_message_schema.dump(new_message)
    }), 201


@pastor_messages_bp.route('/active', methods=['GET'])
def get_active_message():
    """Get the currently active pastor message"""
    message = db.session.query(PastorMessage).filter_by(is_active=True).first()
    
    if message:
        return pastor_message_schema.jsonify(message), 200
    
    return jsonify({"message": "No active pastor message found."}), 404