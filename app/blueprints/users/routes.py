from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required
from .schemas import user_schema, users_schema, login_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import users_bp
from sqlalchemy.exc import IntegrityError  # new import



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
    # use filter(...) which is more idiomatic and reliable across backends
    user = db.session.query(User).filter(db.func.lower(User.email) == email_lower).first()
    
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
    user = db.session.query(User).filter(db.func.lower(User.email) == data["email"]).first()
    if user: 
        return jsonify({"message": "User with this email already exists."}), 400

    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()

    # generate token so frontend can immediately use it
    token = encode_token(new_user.id, new_user.role)
    
    return jsonify({
        "message": "User created successfully.",
        "user": user_schema.dump(new_user),
        "token": token
    }), 201

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
        # allow partial updates so fields like password can be omitted on update
        data = user_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Only hash & set password if provided; otherwise keep existing password
    if 'password' in data and data['password']:
        data['password'] = generate_password_hash(data['password'])
    else:
        data.pop('password', None)

    # Prevent changing email — allow same value (case-insensitive) but do not accept a different email.
    if 'email' in data and data['email']:
        new_email = data['email'].lower().strip()
        current_email = (user.email or "").lower().strip()
        if new_email != current_email:
            return jsonify({"message": "Email cannot be changed."}), 400
        # same email provided, remove to avoid setting it again
        data.pop('email', None)

    for key, value in data.items():
        setattr(user, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Failed to update user: database constraint error."}), 400

    return jsonify({"message": "User updated successfully.", "user": user_schema.dump(user)}), 200

@users_bp.route('', methods=['PUT'])
@token_required
def update_user():
    """
    Update a user by id supplied in the request JSON.
    Body example: { "id": 1, "email": "new@example.com", "password": "newpass" }
    Allows partial updates; password is optional and only re-hashed if provided.
    """
    payload = request.json or {}
    user_id = payload.get('id')
    if user_id is None:
        return jsonify({"message": "User id is required in request body."}), 400
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid user id."}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    try:
        data = user_schema.load(payload, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Only hash & set password if provided; otherwise keep existing password
    if 'password' in data and data['password']:
        data['password'] = generate_password_hash(data['password'])
    else:
        data.pop('password', None)

    # Prevent changing email — allow same value (case-insensitive) but do not accept a different email.
    if 'email' in data and data['email']:
        new_email = data['email'].lower().strip()
        current_email = (user.email or "").lower().strip()
        if new_email != current_email:
            return jsonify({"message": "Email cannot be changed."}), 400
        data.pop('email', None)

    for key, value in data.items():
        setattr(user, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Failed to update user: database constraint error."}), 400

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
