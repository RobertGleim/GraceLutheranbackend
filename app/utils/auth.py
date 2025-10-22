from jose import jwt
import jose
from datetime import datetime, timedelta, timezone
from app.models import User


SECRET_KEY = "super secret key"

def encode_token (user_id, role):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
        "role": role
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
