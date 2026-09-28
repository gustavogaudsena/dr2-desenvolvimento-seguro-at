from datetime import date, datetime, time, timedelta
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session, select

from auth.authenticate import authenticate
from database.database import get_session
from models.consultas import Consulta
from models.users import Role

agenda_router = APIRouter()
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(env=Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape(["html", "xml"]),
))


@agenda_router.get("/agenda", response_class=HTMLResponse)
async def get_agenda(
    request: Request,
    data: date | None = None,
    user: dict = Depends(authenticate),
    session: Session = Depends(get_session),
):
    dia = data or date.today()
    inicio = datetime.combine(dia, time.min)
    fim = inicio + timedelta(days=1)
    statement = select(Consulta).where(
        Consulta.data >= inicio,
        Consulta.data < fim,
    )
    if user["role"] == Role.PROFISSIONAL_SAUDE:
        statement = statement.where(Consulta.owner == user["sub"])
    statement = statement.order_by(Consulta.data)
    consultas_do_dia = session.exec(statement).all()

    return templates.TemplateResponse(
        request,
        "agenda.html",
        {
            "dia": dia,
            "consultas": consultas_do_dia,
        },
    )
