import os
import secrets

from auth.authenticate import require_admin
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.database import get_session
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.users import Role, TokenResponse, User, UserCreate
from sqlmodel import Session

user_router = APIRouter(
    tags=["User"],
)

hash_password = HashPassword()
MFA_CODE = os.getenv("ADMIN_MFA_CODE")


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_user_up(
    user: UserCreate,
    _: dict = Depends(require_admin),
    session: Session = Depends(get_session),
) -> dict:
    if session.get(User, user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com o e-mail informado."
        )

    new_user = User(
        email=user.email,
        name=user.name,
        password=hash_password.create_hash(user.password),
        role=Role.PROFISSIONAL_SAUDE,
    )
    session.add(new_user)
    session.commit()
    return {
        "message": "Usuário criado com sucesso"
    }


@user_router.post("/signin", response_model=TokenResponse)
async def sign_user_in(
    user: OAuth2PasswordRequestForm = Depends(),
    mfa_code: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> dict:
    user_exist = session.get(User, user.username)

    if not user_exist or not hash_password.verify_hash(user.password, user_exist.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    mfa_verified = False
    if user_exist.mfa_enabled:
        if MFA_CODE is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MFA não configurado no servidor.",
            )
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
