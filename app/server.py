# server.py
import shutil
import io
import pandas as pd
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel as PydanticBaseModel, EmailStr
from routers.routers_owners import router as owners_router  # Importación del router de dueños
from routers.routers_citas import router as appointments_router  # Importación del router de citas
from routers.routers_animales import router as animals_router  # Importación del router de animales
from routers.routers_tratamientos import router as tratamientos_router  # Importación del router de tratamientos

# Clases existentes de ejemplo para la funcionalidad de contratos
class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

class Contrato(BaseModel):
    fecha: str
    centro_seccion: str
    nreg: str
    nexp: str
    objeto: str
    tipo: str
    procedimiento: str
    numlicit: str
    numinvitcurs: str
    proc_adjud: str
    presupuesto_con_iva: str
    valor_estimado: str
    importe_adj_con_iva: str
    adjuducatario: str
    fecha_formalizacion: str
    I_G: str

class ListadoContratos(BaseModel):
    contratos: List[Contrato]

# Instancia principal de la aplicación FastAPI
app = FastAPI(
    title="Gestión de Clínica Veterinaria",
    description="API para la gestión de datos de la clínica veterinaria y otras funcionalidades.",
    version="0.2.0"
)

# Incluir routers de dueños, citas, animales y tratamientos
app.include_router(owners_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")
app.include_router(animals_router, prefix="/api/v1")
app.include_router(tratamientos_router, prefix="/api/v1")  # Nueva línea para incluir el router de tratamientos

# Endpoint para recuperar datos de contratos (funcionalidad existente)
@app.get("/retrieve_data/")
def retrieve_data():
    todosmisdatos = pd.read_csv('./contratos_inscritos_simplificado_2023.csv', sep=';')
    todosmisdatos = todosmisdatos.fillna(0)
    todosmisdatosdict = todosmisdatos.to_dict(orient='records')
    listado = ListadoContratos()
    listado.contratos = todosmisdatosdict
    return listado

# Endpoint para envío de formularios (funcionalidad existente)
class FormData(PydanticBaseModel):
    date: str
    description: str
    option: str
    amount: float

@app.post("/envio/")
async def submit_form(data: FormData):
    return {"message": "Formulario recibido", "data": data}

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la clínica veterinaria"}