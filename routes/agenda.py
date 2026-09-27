from datetime import date
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.consultas import consultas

agenda_router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@agenda_router.get("/agenda", response_class=HTMLResponse)
async def get_agenda(request: Request, data: date | None = None):
    dia = data or date.today()
    consultas_do_dia = sorted(
        (consulta for consulta in consultas.values() if consulta.data.date() == dia),
        key=lambda consulta: consulta.data,
    )

    return templates.TemplateResponse(request, "agenda.html", {
        "dia": dia,
        "consultas": consultas_do_dia,
    })
