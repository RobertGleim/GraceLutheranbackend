from flask import request, jsonify
from app.models import PastorMessage, db
from app.utils.auth import token_required, admin_required
from . import pastor_messages_bp

@pastor_messages_bp.route('/active', methods=['GET'])
def get_active_message():
    """Get the currently active pastor message."""
    active_message = db.session.query(PastorMessage).filter_by(is_active=True).first()
    
    if not active_message:
        return jsonify({"message": "No active pastor message found."}), 404
    
    return jsonify({
        "id": active_message.id,
        "title": active_message.title,
        "content": active_message.content,
        "author": active_message.author,
        "created_at": active_message.created_at.isoformat() if active_message.created_at else None,
        "updated_at": active_message.updated_at.isoformat() if active_message.updated_at else None
    }), 200

@pastor_messages_bp.route('', methods=['GET'])
@token_required
def get_all_messages():
    """Get all pastor messages (admin only)."""
    messages = db.session.query(PastorMessage).order_by(PastorMessage.created_at.desc()).all()
    
    return jsonify([{
        "id": msg.id,
        "title": msg.title,
        "content": msg.content,
        "author": msg.author,
        "is_active": msg.is_active,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "updated_at": msg.updated_at.isoformat() if msg.updated_at else None
    } for msg in messages]), 200

@pastor_messages_bp.route('', methods=['POST'])
@admin_required
def create_message():
    """Create a new pastor message (admin only)."""
    data = request.get_json(silent=True) or {}
    
    if not data.get('title') or not data.get('content'):
        return jsonify({"message": "Title and content are required."}), 400
    
    # If setting as active, deactivate other messages
    if data.get('is_active'):
        db.session.query(PastorMessage).update({PastorMessage.is_active: False})
    
    new_message = PastorMessage(
        title=data['title'],
        content=data['content'],
        author=data.get('author', 'Pastor'),
        is_active=data.get('is_active', False)
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "message": "Pastor message created successfully.",
        "id": new_message.id
    }), 201

@pastor_messages_bp.route('/<int:message_id>', methods=['PUT'])
@admin_required
def update_message(message_id):
    """Update a pastor message (admin only)."""
    message = db.session.get(PastorMessage, message_id)
    if not message:
        return jsonify({"message": "Message not found."}), 404
    
    data = request.get_json(silent=True) or {}
    
    # If setting as active, deactivate other messages
    if data.get('is_active') and not message.is_active:
        db.session.query(PastorMessage).update({PastorMessage.is_active: False})
    
    if 'title' in data:
        message.title = data['title']
    if 'content' in data:
        message.content = data['content']
    if 'author' in data:
        message.author = data['author']
    if 'is_active' in data:
        message.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({"message": "Pastor message updated successfully."}), 200

@pastor_messages_bp.route('/<int:message_id>', methods=['DELETE'])
@admin_required
def delete_message(message_id):
    """Delete a pastor message (admin only)."""
    message = db.session.get(PastorMessage, message_id)
    if not message:
        return jsonify({"message": "Message not found."}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({"message": "Pastor message deleted successfully."}), 200

@pastor_messages_bp.route('/<int:message_id>/activate', methods=['PATCH', 'POST'])
@admin_required
def activate_message(message_id):
    """Activate a specific pastor message and deactivate all others (admin only)."""
    message = db.session.get(PastorMessage, message_id)
    if not message:
        return jsonify({"message": "Message not found."}), 404
    
    # Deactivate all other messages
    db.session.query(PastorMessage).update({PastorMessage.is_active: False})
    
    # Activate the specified message
    message.is_active = True
    db.session.commit()
    
    return jsonify({
        "message": "Pastor message activated successfully.",
        "id": message.id
    }), 200