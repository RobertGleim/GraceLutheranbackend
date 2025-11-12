from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required, admin_required
from .schemas import user_schema, users_schema, login_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import users_bp



@users_bp.route('/login', methods=['POST'])
def login():
    # ensure JSON payload
    if not request.is_json:
        return jsonify({"message": "Expected JSON payload (Content-Type: application/json)."}), 400

    raw_json = request.get_json(silent=True) or {}
    # log keys only (avoid logging password value)
    print(f"Login payload keys: {list(raw_json.keys())}")

    try:
        data = login_schema.load(raw_json)
    except ValidationError as e:
        print(f"Validation error: {e.messages}")  # Debug log
        return jsonify({"message": "Invalid request format", "errors": e.messages}), 400

    # require password
    if not data.get('password'):
        return jsonify({"message": "Password is required."}), 400

    # prefer email if provided, otherwise fall back to username
    user = None
    if data.get('email'):
        email_lower = data['email'].lower().strip()
        print(f"Login attempt using email: '{email_lower}'")  # Debug log
        user = db.session.query(User).filter(db.func.lower(User.email) == email_lower).first()
    elif data.get('username'):
        username = data['username'].strip()
        print(f"Login attempt using username: '{username}'")  # Debug log
        user = db.session.query(User).filter(User.username == username).first()
    else:
        return jsonify({"message": "Either 'email' or 'username' is required."}), 400

    if not user:
        print("User lookup failed")  # Debug log
        return jsonify({"message": "Invalid email or password."}), 401

    password_match = check_password_hash(user.password, data.get("password", ""))
    print(f"Password match result: {password_match}")  # Debug log

    if password_match:
        token = encode_token(user.id, user.role)
        return jsonify({"message": "Login successful", "token": token, "user": user_schema.dump(user)}), 200

    print("Password check failed")  # Debug log
    return jsonify({"message": "Invalid email or password."}), 401  


@users_bp.route('', methods=['POST'])
def create_user():
    # Get raw JSON and normalize email before validation
    raw_data = request.get_json(silent=True) or {}
    
    # Normalize email in the raw data before schema validation
    if "email" in raw_data and raw_data["email"]:
        raw_data["email"] = raw_data["email"].lower().strip()
    
    try:
        new_user = user_schema.load(raw_data)
    except ValidationError as e:
        return jsonify({"message": "Invalid request format", "errors": e.messages}), 400 
    
    # Hash the password
    new_user.password = generate_password_hash(raw_data["password"])
    
    # Check for existing email (email is already normalized)
    existing_user = db.session.query(User).filter(db.func.lower(User.email) == new_user.email).first()
    if existing_user: 
        return jsonify({"message": "User with this email already exists."}), 400

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
    """
    Accept only PUT for full/partial updates.
    Blank or omitted password will not overwrite existing password.
    Email cannot be changed (case-insensitive check).
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    # get raw JSON and remove empty password values so validation won't enforce it
    raw = request.get_json(silent=True) or {}
    if 'password' in raw:
        pw = raw.get('password')
        if pw is None or (isinstance(pw, str) and pw.strip() == ""):
            raw.pop('password', None)

    # validate remaining fields (partial allowed)
    data = user_schema.load(raw, partial=True)

    # hash password only if provided and not empty
    if 'password' in data and data['password']:
        data['password'] = generate_password_hash(data['password'])
    else:
        data.pop('password', None)

    # prevent email changes
    if 'email' in data and data['email']:
        new_email = data['email'].lower().strip()
        current_email = (user.email or "").lower().strip()
        if new_email != current_email:
            return jsonify({"message": "Email cannot be changed."}), 400
        data.pop('email', None)

    # apply updates
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

@users_bp.route('/<int:user_id>/role', methods=['PATCH'])
@admin_required
def update_user_role(user_id):
    """
    Update user role and return new token if it's the current user.
    Admin only endpoint.
    """
    data = request.get_json(silent=True) or {}
    new_role = data.get('role')
    
    # Validate role value
    if new_role not in ['user', 'admin']:
        return jsonify({"error": "Invalid role. Must be 'user' or 'admin'."}), 400
    
    # Get user
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    # Update the role
    user.role = new_role
    db.session.commit()
    
    # If updating current user's role, return new token with updated claims
    new_token = None
    if request.user_id == user_id:
        new_token = encode_token(user.id, user.role)
    
    return jsonify({
        "message": "Role updated successfully.",
        "user": user_schema.dump(user),
        "token": new_token  # Only present if updating own role
    }), 200
