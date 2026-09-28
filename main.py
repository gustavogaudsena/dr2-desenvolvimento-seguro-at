from fastapi import FastAPI
from routes.consultas import consultas_router
from routes.agenda import agenda_router
from routes.integracao import integracao_router
from routes.users import user_router
import uvicorn

app = FastAPI()

app.include_router(user_router)
app.include_router(consultas_router)
app.include_router(agenda_router)
app.include_router(integracao_router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
