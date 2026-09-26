from fastapi import FastAPI
from routes.consultas import consultas_router
import uvicorn

app = FastAPI()

app.include_router(consultas_router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
