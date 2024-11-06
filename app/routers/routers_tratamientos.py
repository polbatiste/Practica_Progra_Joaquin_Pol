from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient

# Conexión con MongoDB
client = MongoClient("mongodb://mongodb:27017")
db = client.clinica_veterinaria
coleccion_tratamientos = db.tratamientos

router = APIRouter()

# Modelo de tratamiento
class Tratamiento(BaseModel):
    tipo: str
    nombre: str
    descripcion: Optional[str] = None
    precio: float

# Función para poblar la colección con tratamientos iniciales
def poblar_tratamientos_iniciales():
    tratamientos_iniciales = [
        {"tipo": "Tratamientos básicos", "nombre": "Análisis de sangre", "descripcion": "Análisis de sangre completo", "precio": 50.0},
        {"tipo": "Tratamientos básicos", "nombre": "Análisis hormonales", "descripcion": "Pruebas hormonales", "precio": 70.0},
        {"tipo": "Tratamientos básicos", "nombre": "Vacunación", "descripcion": "Vacunas generales", "precio": 30.0},
        {"tipo": "Tratamientos básicos", "nombre": "Desparasitación", "descripcion": "Tratamiento contra parásitos", "precio": 25.0},
        {"tipo": "Revisión general", "nombre": "Revisión general", "descripcion": "Revisión completa del animal", "precio": 60.0},
        {"tipo": "Revisión específica", "nombre": "Cardiología", "descripcion": "Revisión cardiológica", "precio": 80.0},
        {"tipo": "Revisión específica", "nombre": "Cutánea", "descripcion": "Revisión de la piel", "precio": 45.0},
        {"tipo": "Revisión específica", "nombre": "Broncológica", "descripcion": "Revisión del sistema respiratorio", "precio": 75.0},
        {"tipo": "Ecografías", "nombre": "Ecografía", "descripcion": "Ecografía general", "precio": 90.0},
        {"tipo": "Limpieza dental", "nombre": "Limpieza bucal", "descripcion": "Limpieza y revisión dental", "precio": 55.0},
        {"tipo": "Extracción dental", "nombre": "Extracción de piezas dentales", "descripcion": "Extracción de piezas dentales dañadas", "precio": 100.0},
        {"tipo": "Cirugía", "nombre": "Castración", "descripcion": "Castración quirúrgica", "precio": 150.0},
        {"tipo": "Cirugía", "nombre": "Cirugía abdominal", "descripcion": "Intervención abdominal", "precio": 300.0},
        {"tipo": "Cirugía", "nombre": "Cirugía cardíaca", "descripcion": "Cirugía en el corazón", "precio": 500.0},
        {"tipo": "Cirugía", "nombre": "Cirugía articular y ósea", "descripcion": "Cirugía de articulaciones y huesos", "precio": 400.0},
        {"tipo": "Cirugía", "nombre": "Cirugía de hernias", "descripcion": "Corrección de hernias", "precio": 350.0},
    ]

    # Solo poblar si la colección está vacía
    if coleccion_tratamientos.count_documents({}) == 0:
        coleccion_tratamientos.insert_many(tratamientos_iniciales)

# Llamar a la función de población inicial
poblar_tratamientos_iniciales()

@router.post("/tratamientos", response_model=Tratamiento)
def crear_tratamiento(tratamiento: Tratamiento):
    if coleccion_tratamientos.find_one({"nombre": tratamiento.nombre}):
        raise HTTPException(status_code=400, detail="El tratamiento ya existe")
    coleccion_tratamientos.insert_one(tratamiento.dict())
    return tratamiento

@router.get("/tratamientos", response_model=List[Tratamiento])
def listar_tratamientos():
    tratamientos = list(coleccion_tratamientos.find({}, {"_id": 0}))
    return tratamientos

@router.put("/tratamientos/{nombre}", response_model=Tratamiento)
def actualizar_tratamiento(nombre: str, tratamiento: Tratamiento):
    resultado = coleccion_tratamientos.update_one({"nombre": nombre}, {"$set": tratamiento.dict()})
    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado o sin cambios")
    return tratamiento

@router.delete("/tratamientos/{nombre}")
def eliminar_tratamiento(nombre: str):
    resultado = coleccion_tratamientos.delete_one({"nombre": nombre})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
    return {"mensaje": "Tratamiento eliminado exitosamente"}