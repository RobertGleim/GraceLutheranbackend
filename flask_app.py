from app import create_app
from app.models import db
from flask_cors import CORS
from flask import jsonify, request, g, make_response
import time
import os

app = create_app(os.getenv('FLASK_CONFIG', 'DevelopmentConfig'))

# Simple list of allowed origins for CORS (keep this easy to understand)
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://grace-lutheran.vercel.app",
    os.getenv("FRONTEND_URL", "")
]
# remove any empty values
allowed_origins = [o for o in allowed_origins if o]

# Enable CORS with credentials using a simple list of origins
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": allowed_origins}},
    allow_headers=["Content-Type", "Authorization", "X-HTTP-Method-Override"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    expose_headers=["Content-Type", "Authorization"]
)

# Simple timing and optional method override
@app.before_request
def before_request():
    g._start_time = time.time()
    # small helper for clients that use X-HTTP-Method-Override
    override = request.headers.get("X-HTTP-Method-Override")
    if override:
        o = override.strip().upper()
        if o in ("PUT", "PATCH", "DELETE"):
            request.environ['REQUEST_METHOD'] = o
            print(f"[method-override] applied -> {o}")
    # small, easy-to-read log for debugging
    print(f"[incoming] method={request.method} path={request.path} origin={request.headers.get('Origin')}")

# Health endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# Better JSON for 405 errors
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": "method_not_allowed",
        "message": "The requested URL does not allow that HTTP method."
    }), 405

# Simple OPTIONS preflight for /users endpoints
@app.route('/users', methods=['OPTIONS'])
@app.route('/users/<int:user_id>', methods=['OPTIONS'])
def users_options(user_id=None):
    resp = make_response("", 200)
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-HTTP-Method-Override"
    origin = request.headers.get("Origin")
    resp.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp

# Clear response when PATCH is not implemented
@app.route('/users/<int:user_id>', methods=['PATCH'])
def users_patch(user_id):
    return jsonify({
        "error": "not_implemented",
        "message": "PATCH is not implemented. Use PUT for full updates."
    }), 501

# Simple after_request to ensure CORS origin is echoed for credentialed requests and timing log
@app.after_request
def after_request(response):
    if not response.headers.get("Access-Control-Allow-Origin"):
        origin = request.headers.get("Origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
    # log elapsed time
    start = getattr(g, "_start_time", None)
    elapsed_ms = int((time.time() - start) * 1000) if start else None
    print(f"[response] method={request.method} path={request.path} status={response.status_code} elapsed_ms={elapsed_ms}")
    return response

with app.app_context():
    # db.drop_all()  # Uncomment to recreate database during development
    db.create_all()

if __name__ == '__main__':
    app.run()