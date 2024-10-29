from fastapi import FastAPI
from clientes.endpoints.endpoints import router as clientes_router

app = FastAPI()

app.include_router(clientes_router, prefix="/api")