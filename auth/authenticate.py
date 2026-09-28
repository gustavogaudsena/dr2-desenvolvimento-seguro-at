from auth.jwt_handler import verify_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.users import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")


async def authenticate(token: str = Depends(oauth2_scheme)) -> dict:
    return verify_access_token(token)


async def require_professional(user: dict = Depends(authenticate)) -> dict:
    if user["role"] != Role.PROFISSIONAL_SAUDE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Professional access required",
        )
    return user


async def require_admin(user: dict = Depends(authenticate)) -> dict:
    if user["role"] != Role.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    if not user["mfa"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA required",
        )
    return user
