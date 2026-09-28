import os
import secrets

from auth.authenticate import require_admin
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.users import Role, TokenResponse, User, UserCreate

user_router = APIRouter(
    tags=["User"],
)

hash_password = HashPassword()
MFA_CODE = os.getenv("ADMIN_MFA_CODE", "123456")

users = {
    "medico@clinica.com": User(
        email="medico@clinica.com",
        name="Dr. João Souza",
        password="$2b$12$qLf7xLrlpsJF0lprip/wH.ucWswC8PU8cRPgQXVZLtEtRyur1Wo8S",
        role=Role.PROFISSIONAL_SAUDE,
    ),
    "recepcao@clinica.com": User(
        email="recepcao@clinica.com",
        name="Recepção",
        password="$2b$12$BkXXCR1fImf.2z9vmXQxBOsis/2v.6MTyF0A9ArhUJ/HVp6p7B8u.",
        role=Role.RECEPCIONISTA,
    ),
    "admin@clinica.com": User(
        email="admin@clinica.com",
        name="Administrador",
        password="$2b$12$1DZRxH3ZoAKAdb26xXVq1u0xQRql3sXBPO7QgSt3oDka4hv02fsXu",
        role=Role.ADMINISTRADOR,
        mfa_enabled=True,
    ),
}


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_user_up(
    user: UserCreate,
    _: dict = Depends(require_admin),
) -> dict:
    if user.email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com o e-mail informado."
        )

    users[user.email] = User(
        email=user.email,
        name=user.name,
        password=hash_password.create_hash(user.password),
        role=Role.PROFISSIONAL_SAUDE,
    )
    return {
        "message": "Usuário criado com sucesso"
    }


@user_router.post("/signin", response_model=TokenResponse)
async def sign_user_in(
    user: OAuth2PasswordRequestForm = Depends(),
    mfa_code: str | None = Form(default=None),
) -> dict:
    user_exist = users.get(user.username)

    if not user_exist or not hash_password.verify_hash(user.password, user_exist.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    mfa_verified = False
    if user_exist.mfa_enabled:
        mfa_verified = (
            mfa_code is not None
            and secrets.compare_digest(mfa_code, MFA_CODE)
        )
        if not mfa_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código MFA inválido.",
            )

    return {
        "access_token": create_access_token(user_exist, mfa_verified),
        "token_type": "bearer"
    }


@user_router.get("/admin")
async def admin_route(_: dict = Depends(require_admin)) -> dict:
    return {"message": "Admin access granted"}
