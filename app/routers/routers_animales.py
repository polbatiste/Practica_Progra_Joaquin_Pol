from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
import random

router = APIRouter()

# Modelo de datos para representar un Animal
class Animal(BaseModel):
    id: str = None  # El ID se generará automáticamente
    name: str       # Nombre del animal
    species: str    # Especie del animal (e.g., perro, gato)
    breed: str      # Raza del animal
    age: int        # Edad del animal
    owner_id: int   # ID del propietario del animal

# Base de datos simulada en memoria para almacenar animales
animals_db = []

# Función para generar un ID único de animal
def generate_animal_id():
    return str(random.randint(1000, 9999))

# Endpoint para crear un nuevo animal
@router.post("/animals", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(animal: Animal):
    # Comprobación de duplicados: mismo nombre y propietario
    if any(existing["name"] == animal.name and existing["owner_id"] == animal.owner_id for existing in animals_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El animal ya existe para este propietario"
        )
    
    # Generación de un ID único que no esté en la base de datos
    animal.id = generate_animal_id()
    while any(existing["id"] == animal.id for existing in animals_db):
        animal.id = generate_animal_id()
    
    animals_db.append(animal.dict())  # Guarda el animal en la base de datos en memoria
    return animal

# Endpoint para obtener todos los animales en la base de datos
@router.get("/animals", response_model=List[Animal])
def get_animals():
    return animals_db

# Endpoint para obtener el número total de animales
@router.get("/animals/count")
def get_animal_count():
    return {"total_animals": len(animals_db)}