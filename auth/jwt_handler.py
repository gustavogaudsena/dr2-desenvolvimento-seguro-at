from datetime import datetime, timedelta, timezone
import os
import secrets

from fastapi import HTTPException, status
import jwt

from models.users import Role, User

SECRET_KEY = os.getenv("JWT_SECRET") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user: User, mfa_verified: bool):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.email,
        "actor": "user",
        "role": user.role.value,
        "mfa": mfa_verified,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_client_access_token(client_id: str, scopes: set[str]):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": client_id,
        "client_id": client_id,
        "actor": "client",
        "scope": " ".join(sorted(scopes)),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("actor") == "user":
            data["role"] = Role(data["role"])
        elif data.get("actor") == "client":
            if "client_id" not in data or "scope" not in data:
                raise ValueError
        else:
            raise ValueError
        return data
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
