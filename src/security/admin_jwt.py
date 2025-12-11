import jwt
from datetime import datetime, timedelta, UTC
from src.config import settings


def create_jwt(username: str):
    payload = {
        "sub": username,
        "exp": datetime.now(UTC) + timedelta(hours=8)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
