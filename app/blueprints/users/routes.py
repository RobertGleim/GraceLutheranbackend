from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required
from .schemas import user_schema, users_schema, login_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import users_bp









@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data=login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user = db.session.query(User).where(User.email == data["email"]).first()
    if user and check_password_hash(user.password, data["password"]):
        token = encode_token(user.id, user.role)
        return jsonify({"message": "Login successful", "token": token, "user": user_schema.dump(user)}), 200
    
    return jsonify({"message": "Invalid email or password."}), 401  

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

@users_bp.route('', methods=['GET'])
@token_required
def get_users():
    
    users = db.session.query(User).all()
    return users_schema.jsonify(users), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):

    user = db.session.get(User, user_id)
    if user:
        return user_schema.jsonify(user), 200
    return jsonify({"message": "User not found."}), 404

@users_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user_by_id(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    data['password'] = generate_password_hash(data['password'])
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify({"message": "User updated successfully.", "user": user_schema.dump(user)}), 200
