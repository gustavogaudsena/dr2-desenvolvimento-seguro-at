from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2, OAuth2PasswordBearer
from models.users import Role

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/signin",
    scheme_name="UserBearer",
)
client_oauth2_scheme = OAuth2(
    flows={
        "clientCredentials": {
            "tokenUrl": "/oauth/token",
            "scopes": {
                "horarios:read": "Consultar horários disponíveis",
            },
        },
    },
    scheme_name="ClientBearer",
)


async def authenticate(
    request: Request,
    _: str = Depends(oauth2_scheme),
) -> dict:
    user = getattr(request.state, "token_data", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user["actor"] != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User token required",
        )
    return user


async def authenticate_client(
    request: Request,
    _: str = Security(client_oauth2_scheme),
) -> dict:
    client = getattr(request.state, "token_data", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if client["actor"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client token required",
        )
    return client


async def require_horarios_read(
    client: dict = Security(
        authenticate_client,
        scopes=["horarios:read"],
    ),
) -> dict:
    if "horarios:read" not in client["scope"].split():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scope horarios:read required",
        )
    return client


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
