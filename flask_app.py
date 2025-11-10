from app import create_app
from app.models import db
from flask_cors import CORS
from flask import jsonify  # added
from flask import request  # added
import os
import re
from urllib.parse import urlparse  # added

app = create_app(os.getenv('FLASK_CONFIG', 'DevelopmentConfig'))

# Allow local development and production Vercel frontend
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # Alternate localhost
    "https://grace-lutheran.vercel.app",  # Production Vercel URL
    os.getenv("FRONTEND_URL", "")  # From Render environment variable
]

# compiled regex to accept any localhost or 127.0.0.1 with any port (http or https)
localhost_regex = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")

# Build origins list: include the localhost regex first so any localhost:PORT is accepted,
# plus any explicitly configured origins.
origins_list = [localhost_regex] + [origin for origin in allowed_origins if origin]

CORS(app, 
     supports_credentials=True, 
     resources={r"/*": {"origins": origins_list}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Ensure OPTIONS is included
     expose_headers=["Content-Type", "Authorization"])

# Build a set of frontend hostnames parsed from allowed_origins to compare against incoming Host/Origin.
_frontend_hosts = set()
for o in allowed_origins:
    if not o:
        continue
    try:
        p = urlparse(o)
        if p.hostname:
            _frontend_hosts.add(p.hostname)
    except Exception:
        pass
# also include known frontend hostnames explicitly
_frontend_hosts.update({"grace-lutheran.vercel.app", "www.grace-lutheran.vercel.app"})

# Minimal logging and quick check to surface misconfigured frontend API host
@app.before_request
def _log_and_check_request():
    host = request.host
    origin = request.headers.get("Origin", "")
    print(f"[incoming] host={host} origin={origin} method={request.method} path={request.path}")

    # If a user-related POST/PUT is received and the Host or Origin matches known frontend hosts,
    # return a clear JSON error so developers see the misconfiguration quickly.
    if request.path.startswith("/users") and request.method in ("POST", "PUT"):
        try:
            origin_host = urlparse(origin).hostname or ""
        except Exception:
            origin_host = ""
        req_host = (host.split(":")[0] if host else "")
        if req_host in _frontend_hosts or origin_host in _frontend_hosts:
            return jsonify({
                "error": "incorrect_api_host",
                "message": "This request appears to have reached a frontend host. Verify your frontend's API base URL — it should point to your backend (e.g. https://gracelutheranbacke.onrender.com) not https://grace-lutheran.vercel.app."
            }), 400

# Add a small health endpoint to verify the backend URL quickly
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# Improve 405 responses so clients see a JSON message (helps during debugging)
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": "method_not_allowed",
        "message": "The requested URL exists but does not allow that HTTP method. Verify the frontend is using the correct API base URL and HTTP verb."
    }), 405

with app.app_context():
    # db.drop_all()  # Uncomment to recreate database
    db.create_all()

if __name__ == '__main__':
    app.run()