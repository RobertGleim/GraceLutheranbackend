from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required, admin_required
from .schemas import pastor_message_schema, pastor_messages_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import pastor_messages_bp
from app.models import PastorMessage


@pastor_messages_bp.route('', methods=['POST'])
@admin_required
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

@pastor_messages_bp.route('/<int:message_id>', methods=['PUT'])
@admin_required
def update_message(message_id):
    """Update a pastor message (admin only)"""
    message = db.session.get(PastorMessage, message_id)
    
    if not message:
        return jsonify({"message": "Pastor message not found."}), 404
    
    try:
        data = request.json
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    if data.get('is_active', False):
        db.session.query(PastorMessage).filter(PastorMessage.id != message_id).update({'is_active': False})
    
   
    if 'title' in data:
        message.title = data['title']
    if 'message' in data:
        message.message = data['message']
    if 'is_active' in data:
        message.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        "message": "Pastor message updated successfully.",
        "data": pastor_message_schema.dump(message)
    }), 200




@pastor_messages_bp.route('', methods=['GET'])
def get_all_messages():
    """Get all pastor messages"""
    messages = db.session.query(PastorMessage).all()
    return pastor_messages_schema.jsonify(messages), 200

@pastor_messages_bp.route('/active', methods=['GET'])
def get_active_message():
    """Get the currently active pastor message"""
    message = db.session.query(PastorMessage).filter_by(is_active=True).first()
    
    if message:
        return pastor_message_schema.jsonify(message), 200
    
    return jsonify({"message": "No active pastor message found."}), 404

@pastor_messages_bp.route('/<int:message_id>', methods=['DELETE'])
@admin_required
def delete_message(message_id):
    """Delete a pastor message (admin only)"""
    message = db.session.get(PastorMessage, message_id)
    
    if not message:
        return jsonify({"message": "Pastor message not found."}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({"message": "Pastor message deleted successfully."}), 200

@pastor_messages_bp.route('/<int:message_id>/activate', methods=['PATCH'])
@admin_required
def activate_message(message_id):
    """Set a specific message as the active one"""
    message = db.session.get(PastorMessage, message_id)
    
    if not message:
        return jsonify({"message": "Pastor message not found."}), 404
    
    # Deactivate all messages
    db.session.query(PastorMessage).update({'is_active': False})
    
    # Activate this message
    message.is_active = True
    db.session.commit()
    
    return jsonify({
        "message": "Pastor message activated successfully.",
        "data": pastor_message_schema.dump(message)
    }), 200