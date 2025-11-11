from app import create_app
from app.models import db
from flask_cors import CORS
from flask import jsonify  # added
from flask import request  # added
from flask import g  # added
from flask import make_response  # add near other flask imports
import time  # added
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
     allow_headers=["Content-Type", "Authorization", "X-HTTP-Method-Override"],  # allow override header for clients
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Include PATCH for preflight
     expose_headers=["Content-Type", "Authorization"])

# Build a set of frontend hostnames parsed from allowed_origins to compare against incoming Host/Origin.
_frontend_hosts = set()
for o in allowed_origins:
    if not o:
        continue
    try:
        p = urlparse(o)
        # skip local hosts so local backend requests are not flagged
        if p.hostname and p.hostname not in ("localhost", "127.0.0.1"):
            _frontend_hosts.add(p.hostname)
    except Exception:
        pass
# also include known frontend hostnames explicitly (non-local)
_frontend_hosts.update({"grace-lutheran.vercel.app", "www.grace-lutheran.vercel.app"})

# expected backend URL to show in the error message (can be set via env)
_expected_backend = os.getenv("BACKEND_URL", "https://gracelutheranbacke.onrender.com")
_expected_backend_host = urlparse(_expected_backend).hostname or ""

# Minimal logging and quick check to surface misconfigured frontend API host
@app.before_request
def _log_and_check_request():
    # Respect X-HTTP-Method-Override from clients that tunnel methods via POST.
    # Update environ early so request.method reflects the override for routing and checks.
    override = request.headers.get("X-HTTP-Method-Override")
    if override:
        override_up = override.strip().upper()
        # Only allow safe override values
        if override_up in ("PUT", "PATCH", "DELETE"):
            request.environ['REQUEST_METHOD'] = override_up
            # small debug print to show override was applied
            print(f"[method-override] applied override -> {override_up}")
    
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

        # don't flag local hosts or the configured backend host as misconfigured
        if req_host in ("localhost", "127.0.0.1") or req_host == _expected_backend_host:
            return None

        if req_host in _frontend_hosts or origin_host in _frontend_hosts:
            return jsonify({
                "error": "incorrect_api_host",
                "detected_host": req_host or origin_host,
                "expected_backend": _expected_backend,
                "message": "Request reached a frontend host. Update your frontend's API base URL to the backend listed in 'expected_backend'."
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

# Ensure OPTIONS preflight for user endpoints returns required CORS headers.
@app.route('/users', methods=['OPTIONS'])
@app.route('/users/<int:user_id>', methods=['OPTIONS'])
def users_options(user_id=None):
    # Minimal preflight response — after_request will merge headers too, but return explicit values here
    resp = make_response("", 200)
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-HTTP-Method-Override"
    origin = request.headers.get("Origin")
    # Echo origin for credentialed requests, fallback to wildcard if not present
    resp.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp

# Provide a clear, deterministic response when PATCH is requested but not implemented.
@app.route('/users/<int:user_id>', methods=['PATCH'])
def users_patch(user_id):
    return jsonify({
        "error": "not_implemented",
        "message": "PATCH is not implemented on the backend. Use PUT for full updates or implement PATCH on the server."
    }), 501

# Minimal timing/logging: record start time in before_request and log response details in after_request.
@app.before_request
def _start_timer():
    g._start_time = time.time()

@app.after_request
def _log_response(response):
	# Ensure required CORS response headers are present/merged so preflight succeeds
	# required headers and methods we want to guarantee
	_required_headers = ["Content-Type", "Authorization", "X-HTTP-Method-Override"]
	_required_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

	# Merge/ensure Access-Control-Allow-Headers
	existing_headers = response.headers.get("Access-Control-Allow-Headers")
	if existing_headers:
		existing_list = [h.strip() for h in existing_headers.split(",") if h.strip()]
		for h in _required_headers:
			if h not in existing_list:
				existing_list.append(h)
		response.headers["Access-Control-Allow-Headers"] = ", ".join(existing_list)
	else:
		response.headers["Access-Control-Allow-Headers"] = ", ".join(_required_headers)

	# Merge/ensure Access-Control-Allow-Methods
	existing_methods = response.headers.get("Access-Control-Allow-Methods")
	if existing_methods:
		existing_m_list = [m.strip().upper() for m in existing_methods.split(",") if m.strip()]
		for m in _required_methods:
			if m not in existing_m_list:
				existing_m_list.append(m)
		response.headers["Access-Control-Allow-Methods"] = ", ".join(existing_m_list)
	else:
		response.headers["Access-Control-Allow-Methods"] = ", ".join(_required_methods)

	# Ensure Access-Control-Allow-Origin is set for credentialed requests (echo Origin when available)
	if not response.headers.get("Access-Control-Allow-Origin"):
		origin = request.headers.get("Origin")
		if origin:
			response.headers["Access-Control-Allow-Origin"] = origin

	# Compute elapsed time for logging (existing behavior)
	start = getattr(g, "_start_time", None)
	elapsed_ms = None
	if start:
		elapsed_ms = int((time.time() - start) * 1000)

	cors_header = response.headers.get("Access-Control-Allow-Origin", None)
	print(f"[response] method={request.method} path={request.path} status={response.status_code} elapsed_ms={elapsed_ms} cors_allow_origin={cors_header}")

	return response

with app.app_context():
    # db.drop_all()  # Uncomment to recreate database
    db.create_all()

if __name__ == '__main__':
    app.run()