from sqlmodel import Session

from models.users import Role, User

DEFAULT_USERS = [
    {
        "email": "medico@clinica.com",
        "name": "Dr. João Souza",
        "password": "$2b$12$qLf7xLrlpsJF0lprip/wH.ucWswC8PU8cRPgQXVZLtEtRyur1Wo8S",
        "role": Role.PROFISSIONAL_SAUDE,
    },
    {
        "email": "recepcao@clinica.com",
        "name": "Recepção",
        "password": "$2b$12$BkXXCR1fImf.2z9vmXQxBOsis/2v.6MTyF0A9ArhUJ/HVp6p7B8u.",
        "role": Role.RECEPCIONISTA,
    },
    {
        "email": "admin@clinica.com",
        "name": "Administrador",
        "password": "$2b$12$1DZRxH3ZoAKAdb26xXVq1u0xQRql3sXBPO7QgSt3oDka4hv02fsXu",
        "role": Role.ADMINISTRADOR,
        "mfa_enabled": True,
    },
]


def seed_users(session: Session) -> None:
    for user_data in DEFAULT_USERS:
        if session.get(User, user_data["email"]) is None:
            session.add(User(**user_data))
    session.commit()
