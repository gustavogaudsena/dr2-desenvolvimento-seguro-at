from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from auth.middleware_jwt import JWTMiddleware
from auth.rate_limiter import RateLimiterMiddleware
from database.database import create_db_and_tables, engine
from database.seed import seed_users
from routes.consultas import consultas_router
from routes.agenda import agenda_router
from routes.integracao import integracao_router
from routes.users import user_router

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://app.clinica.com",
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_users(session)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(JWTMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

app.include_router(user_router)
app.include_router(consultas_router)
app.include_router(agenda_router)
app.include_router(integracao_router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
