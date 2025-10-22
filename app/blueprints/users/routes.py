
from flask import request, jsonify
from app.models import User, db
from .schemas import user_schema, users_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import users_bp


@users_bp.route('', methods=['POST'])
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 
    
    data["password"] = generate_password_hash(data["password"])
    
    user = db.session.query(User).where(User.email == data["email"]).first()
    
    if user: 
        return jsonify({"message": "User with this email already exists."}), 400

    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully.", 
                    "user": user_schema.dump(new_user)}), 201