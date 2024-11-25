# app/routers/routers_tratamientos.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient

# Conexión con MongoDB
MONGO_URI = "mongodb://root:example@mongodb:27017/?authSource=admin"
client = MongoClient(MONGO_URI)
db = client.clinica_veterinaria
coleccion_tratamientos = db.tratamientos

router = APIRouter()

# Modelo de datos para representar un Tratamiento
class Tratamiento(BaseModel):
    tipo: str             # Tipo de tratamiento (ej., Cirugía, Revisión)
    nombre: str           # Nombre del tratamiento
    descripcion: Optional[str] = None  # Descripción del tratamiento
    precio: float         # Precio del tratamiento

# Función para poblar la colección con tratamientos iniciales, solo si está vacía
def poblar_tratamientos_iniciales():
    tratamientos_iniciales = [
        # Tratamientos básicos
        {"tipo": "Tratamientos básicos", "nombre": "Análisis de sangre", "descripcion": "Análisis de sangre completo", "precio": 50.0},
        {"tipo": "Tratamientos básicos", "nombre": "Análisis hormonales", "descripcion": "Detección de niveles hormonales", "precio": 70.0},
        {"tipo": "Tratamientos básicos", "nombre": "Vacunación", "descripcion": "Vacunas generales", "precio": 30.0},
        {"tipo": "Tratamientos básicos", "nombre": "Desparasitación", "descripcion": "Eliminación de parásitos internos y externos", "precio": 25.0},
        
        # Revisión general
        {"tipo": "Revisión general", "nombre": "Revisión general", "descripcion": "Revisión completa del animal", "precio": 60.0},

        # Revisión específica
        {"tipo": "Revisión específica", "nombre": "Revisión cardiológica", "descripcion": "Examen especializado del corazón", "precio": 120.0},
        {"tipo": "Revisión específica", "nombre": "Revisión cutánea", "descripcion": "Evaluación de la piel y pelaje", "precio": 80.0},
        {"tipo": "Revisión específica", "nombre": "Revisión broncológica", "descripcion": "Revisión de vías respiratorias", "precio": 90.0},

        # Ecografías
        {"tipo": "Ecografías", "nombre": "Ecografía abdominal", "descripcion": "Ecografía de la cavidad abdominal", "precio": 150.0},
        {"tipo": "Ecografías", "nombre": "Ecografía cardíaca", "descripcion": "Ecografía para evaluar el corazón", "precio": 180.0},

        # Tratamientos dentales
        {"tipo": "Tratamientos dentales", "nombre": "Limpieza bucal", "descripcion": "Limpieza profunda de dientes", "precio": 100.0},
        {"tipo": "Tratamientos dentales", "nombre": "Extracción de piezas dentales", "descripcion": "Extracción quirúrgica de dientes dañados", "precio": 200.0},

        # Cirugías
        {"tipo": "Cirugía", "nombre": "Castración", "descripcion": "Castración quirúrgica", "precio": 150.0},
        {"tipo": "Cirugía", "nombre": "Cirugía abdominal", "descripcion": "Procedimientos quirúrgicos abdominales", "precio": 300.0},
        {"tipo": "Cirugía", "nombre": "Cirugía cardíaca", "descripcion": "Cirugía en el corazón", "precio": 500.0},
        {"tipo": "Cirugía", "nombre": "Cirugía articular y ósea", "descripcion": "Reparación de articulaciones y huesos", "precio": 400.0},
        {"tipo": "Cirugía", "nombre": "Cirugía de hernias", "descripcion": "Reparación de hernias", "precio": 250.0}
    ]
    if coleccion_tratamientos.count_documents({}) == 0:
        coleccion_tratamientos.insert_many(tratamientos_iniciales)

# Llamada para poblar tratamientos iniciales si la colección está vacía
poblar_tratamientos_iniciales()

# Crear un nuevo tratamiento
@router.post("/tratamientos", response_model=Tratamiento)
def crear_tratamiento(tratamiento: Tratamiento):
    if coleccion_tratamientos.find_one({"nombre": tratamiento.nombre}):
        raise HTTPException(status_code=400, detail="El tratamiento ya existe")
    coleccion_tratamientos.insert_one(tratamiento.dict())
    return tratamiento

# Listar todos los tratamientos
@router.get("/tratamientos", response_model=List[Tratamiento])
def listar_tratamientos():
    return list(coleccion_tratamientos.find({}, {"_id": 0}))

# Actualizar un tratamiento existente por nombre
@router.put("/tratamientos/{nombre}", response_model=Tratamiento)
def actualizar_tratamiento(nombre: str, tratamiento: Tratamiento):
    resultado = coleccion_tratamientos.update_one({"nombre": nombre}, {"$set": tratamiento.dict()})
    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado o sin cambios")
    return tratamiento

# Eliminar un tratamiento por nombre
@router.delete("/tratamientos/{nombre}")
def eliminar_tratamiento(nombre: str):
    resultado = coleccion_tratamientos.delete_one({"nombre": nombre})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
    return {"mensaje": "Tratamiento eliminado exitosamente"}