import pandas as pd
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as PydanticBaseModel
from routers.routers_owners import router as owners_router
from routers.routers_citas import router as appointments_router
from routers.routers_animales import router as animals_router
from routers.routers_tratamientos import router as tratamientos_router
from routers.routers_productos import router as productos_router

# Modelo base para configuraciones de Pydantic
class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True

# Modelo para un contrato
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
    adjudicatario: str
    fecha_formalizacion: str
    I_G: str

# Modelo para una lista de contratos
class ListadoContratos(BaseModel):
    contratos: List[Contrato]

# Instancia principal de la aplicación FastAPI
app = FastAPI(
    title="Gestión de Clínica Veterinaria",
    description="API para la gestión de datos de la clínica veterinaria y otras funcionalidades.",
    version="0.2.0"
)

# Incluir routers para las funcionalidades de la clínica
app.include_router(owners_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")
app.include_router(animals_router, prefix="/api/v1")
app.include_router(tratamientos_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")

# Endpoint para recuperar datos de contratos
@app.get("/retrieve_data/")
def retrieve_data():
    try:
        contratos_df = pd.read_csv('./contratos_inscritos_simplificado_2023.csv', sep=';').fillna(0)
        contratos_dict = contratos_df.to_dict(orient='records')
        return ListadoContratos(contratos=contratos_dict)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo de contratos no encontrado")

# Modelo de datos para envío de formularios
class FormData(PydanticBaseModel):
    date: str
    description: str
    option: str
    amount: float

# Endpoint para recibir y procesar un formulario
@app.post("/envio/")
async def submit_form(data: FormData):
    return {"message": "Formulario recibido", "data": data}

# Mensaje de bienvenida
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la clínica veterinaria"}