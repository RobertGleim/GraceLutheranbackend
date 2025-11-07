from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required
from .schemas import user_schema, users_schema, login_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import users_bp









@users_bp.route('/login', methods=['POST'])
def login():
    print(f"Login attempt - Request data: {request.json}")  # Debug log
    
    try:
        data = login_schema.load(request.json)
    except ValidationError as e:
        print(f"Validation error: {e.messages}")  # Debug log
        return jsonify({"message": "Invalid request format", "errors": e.messages}), 400
    
    # Case-insensitive email lookup
    email_lower = data['email'].lower().strip()
    print(f"Looking for user with email: {email_lower}")  # Debug log
    user = db.session.query(User).where(db.func.lower(User.email) == email_lower).first()
    
    if not user:
        print(f"User not found with email: {email_lower}")  # Debug log
        return jsonify({"message": "Invalid email or password."}), 401
    
    print(f"User found: {user.email}, checking password...")  # Debug log
    password_match = check_password_hash(user.password, data["password"])
    print(f"Password match result: {password_match}")  # Debug log
    
    if password_match:
        token = encode_token(user.id, user.role)
        return jsonify({"message": "Login successful", "token": token, "user": user_schema.dump(user)}), 200
    
    print("Password check failed")  # Debug log
    return jsonify({"message": "Invalid email or password."}), 401  

@users_bp.route('', methods=['POST'])
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"message": "Invalid request format", "errors": e.messages}), 400 
    
    # Store email in lowercase for consistency
    data["email"] = data["email"].lower().strip()
    data["password"] = generate_password_hash(data["password"])
    
    # Check for existing email
    user = db.session.query(User).where(db.func.lower(User.email) == data["email"]).first()
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

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."}), 200
