from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
import random

router = APIRouter()

# Definición del modelo de datos para Animal
class Animal(BaseModel):
    id: str = None  # ID generado automáticamente
    name: str
    species: str
    breed: str
    age: int
    owner_id: int

# Base de datos simulada en memoria
animals_db = []

# Generador de ID único para los animales
def generate_animal_id():
    return str(random.randint(1000, 9999))

# Endpoint para crear un nuevo animal
@router.post("/animals", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(animal: Animal):
    # Validación para evitar duplicados (según nombre y propietario)
    if any(existing_animal["name"] == animal.name and existing_animal["owner_id"] == animal.owner_id for existing_animal in animals_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El animal ya existe para este propietario"
        )
    
    # Generación de un ID único
    animal.id = generate_animal_id()
    while any(existing_animal["id"] == animal.id for existing_animal in animals_db):
        animal.id = generate_animal_id()
    
    animals_db.append(animal.dict())
    return animal

# Endpoint para obtener todos los animales
@router.get("/animals", response_model=List[Animal])
def get_animals():
    return animals_db

# Endpoint para obtener el total de animales (para el Dashboard)
@router.get("/animals/count")
def get_animal_count():
    return {"total_animals": len(animals_db)}
