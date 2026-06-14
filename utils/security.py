from datetime import datetime, timedelta
import jwt
import bcrypt
from backend.config import settings

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    # Bcrypt maximum input length is 72 bytes. Truncate to avoid crashing.
    truncated = password[:72].encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        truncated = plain_password[:72].encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(truncated, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
