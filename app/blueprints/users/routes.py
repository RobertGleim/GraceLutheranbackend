from flask import request, jsonify
from app.models import User, db
from app.utils.auth import encode_token, token_required, admin_required
from .schemas import user_schema, users_schema, login_schema
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import users_bp
import os


# Add diagnostic endpoint to check if admin exists
@users_bp.route('/check-admin', methods=['GET'])
def check_admin():
    """Diagnostic endpoint to verify admin user exists."""
    admin = db.session.query(User).filter(db.func.lower(User.email) == 'admin@email.com').first()
    if admin:
        return jsonify({
            "exists": True,
            "email": admin.email,
            "username": admin.username,
            "role": admin.role,
            "has_password": bool(admin.password)
        }), 200
    else:
        all_users = db.session.query(User).all()
        return jsonify({
            "exists": False,
            "total_users": len(all_users),
            "users": [{"email": u.email, "username": u.username} for u in all_users]
        }), 200


@users_bp.route('/login', methods=['POST'])
def login():
    
    if not request.is_json:
        print("[LOGIN ERROR] Request is not JSON")
        return jsonify({"message": "Expected JSON payload (Content-Type: application/json)."}), 400

    raw_json = request.get_json(silent=True) or {}
    
    print(f"[LOGIN] Full payload received: {raw_json}")
    print(f"[LOGIN] Content-Type header: {request.headers.get('Content-Type')}")
    print(f"[LOGIN] Request data type: {type(raw_json)}")

    try:
        data = login_schema.load(raw_json)
        print(f"[LOGIN] Schema validation passed. Loaded data: {data}")
    except ValidationError as e:
        print(f"[LOGIN ERROR] Validation failed: {e.messages}") 
        return jsonify({"message": "Invalid request format", "errors": e.messages}), 400

    # Validate that password exists
    password = data.get('password', '').strip()
    if not password:
        print("[LOGIN ERROR] Password missing from request")
        return jsonify({"message": "Password is required."}), 400

    # Validate that at least email or username is provided
    if not data.get('email') and not data.get('username'):
        print("[LOGIN ERROR] Neither email nor username provided")
        return jsonify({"message": "Either 'email' or 'username' is required."}), 400

    # Lookup user by email or username
    user = None
    if data.get('email'):
        email_lower = data['email'].lower().strip()
        print(f"[LOGIN] Attempting login with email: '{email_lower}'")
        user = db.session.query(User).filter(db.func.lower(User.email) == email_lower).first()
        if user:
            print(f"[LOGIN] User found: id={user.id}, email={user.email}, username={user.username}, role={user.role}")
            print(f"[LOGIN] User has password hash: {bool(user.password)}")
            print(f"[LOGIN] Password hash starts with: {user.password[:20] if user.password else 'NONE'}")
        else:
            print(f"[LOGIN ERROR] No user found with email: '{email_lower}'")
            # Debug: show all users in database
            all_users = db.session.query(User).all()
            print(f"[LOGIN DEBUG] Total users in database: {len(all_users)}")
            for u in all_users:
                print(f"[LOGIN DEBUG] User: {u.email}, {u.username}")
    elif data.get('username'):
        username = data['username'].strip()
        print(f"[LOGIN] Attempting login with username: '{username}'")
        user = db.session.query(User).filter(User.username == username).first()
        if user:
            print(f"[LOGIN] User found: id={user.id}, email={user.email}, username={user.username}")
        else:
            print(f"[LOGIN ERROR] No user found with username: '{username}'")

    if not user:
        print("[LOGIN ERROR] Authentication failed - user not found")
        return jsonify({"message": "Invalid credentials."}), 401

    # Verify password
    print(f"[LOGIN] Attempting password verification for user: {user.email}")
    print(f"[LOGIN] Password length from request: {len(password)}")
    password_match = check_password_hash(user.password, password)
    print(f"[LOGIN] Password verification result: {password_match}")

    if not password_match:
        print("[LOGIN ERROR] Authentication failed - incorrect password")
        # Debug: try with raw password (REMOVE THIS AFTER TESTING)
        print(f"[LOGIN DEBUG] Raw password from request: '{password}'")
        return jsonify({"message": "Invalid credentials."}), 401

    # Success - generate token
    print(f"[LOGIN SUCCESS] User {user.email} authenticated successfully")
    token = encode_token(user.id, user.role)
    return jsonify({
        "message": "Login successful", 
        "token": token, 
        "user": user_schema.dump(user)
    }), 200

@users_bp.route('', methods=['POST'])
def create_user():
    
    raw_data = request.get_json(silent=True) or {}
    
    
    if "email" in raw_data and raw_data["email"]:
        raw_data["email"] = raw_data["email"].lower().strip()
    
    try:
        new_user = user_schema.load(raw_data)
    except ValidationError as e:
        return jsonify({"message": "Invalid request format", "errors": e.messages}), 400 
    
   
    new_user.password = generate_password_hash(raw_data["password"])
    
    
    existing_user = db.session.query(User).filter(db.func.lower(User.email) == new_user.email).first()
    if existing_user: 
        return jsonify({"message": "User with this email already exists."}), 400

    db.session.add(new_user)
    db.session.commit()

    
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

    
    raw = request.get_json(silent=True) or {}
    if 'password' in raw:
        pw = raw.get('password')
        if pw is None or (isinstance(pw, str) and pw.strip() == ""):
            raw.pop('password', None)

    
    data = user_schema.load(raw, partial=True)

    
    if 'password' in data and data['password']:
        data['password'] = generate_password_hash(data['password'])
    else:
        data.pop('password', None)

    
    if 'email' in data and data['email']:
        new_email = data['email'].lower().strip()
        current_email = (user.email or "").lower().strip()
        if new_email != current_email:
            return jsonify({"message": "Email cannot be changed."}), 400
        data.pop('email', None)

    
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
    
    
    if new_role not in ['user', 'admin']:
        return jsonify({"error": "Invalid role. Must be 'user' or 'admin'."}), 400
    
    
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    
    user.role = new_role
    db.session.commit()
    
    
    new_token = None
    if request.user_id == user_id:
        new_token = encode_token(user.id, user.role)
    
    return jsonify({
        "message": "Role updated successfully.",
        "user": user_schema.dump(user),
        "token": new_token  
    }), 200

# TEMPORARY: Remove this endpoint after fixing the password issue
@users_bp.route('/reset-admin-password', methods=['POST'])
def reset_admin_password():
    """Temporary endpoint to reset admin password. REMOVE AFTER USE!"""
    data = request.get_json(silent=True) or {}
    secret = data.get('secret')
    
    # Simple protection - set this as environment variable on Render
    if secret != os.getenv('ADMIN_RESET_SECRET', 'change-me-in-production'):
        return jsonify({"message": "Unauthorized"}), 401
    
    admin = db.session.query(User).filter(db.func.lower(User.email) == 'admin@email.com').first()
    if not admin:
        return jsonify({"message": "Admin not found"}), 404
    
    new_password = data.get('new_password', 'admin123!')
    admin.password = generate_password_hash(new_password)
    db.session.commit()
    
    print(f"[ADMIN RESET] Password reset for {admin.email}")
    print(f"[ADMIN RESET] New hash: {admin.password[:30]}")
    
    return jsonify({
        "message": "Admin password reset successfully",
        "email": admin.email,
        "new_password_hint": f"{new_password[:2]}...{new_password[-2:]}"
    }), 200
