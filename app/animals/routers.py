# app/animals/routers.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Modelo de datos para el registro de un animal
class Animal(BaseModel):
    name: str
    species: str
    breed: str
    age: int
    owner_id: int  # Este campo puede ser el ID del dueño registrado

# Base de datos simulada en memoria para almacenar animales (para desarrollo inicial)
animals_db = []

@router.post("/animals", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(animal: Animal):
    """
    Endpoint para registrar un nuevo animal.
    Recibe los datos del animal en el cuerpo de la solicitud y lo guarda en la base de datos simulada.
    """
    # Agregar el animal a la base de datos simulada
    animals_db.append(animal.dict())
    return animal

@router.get("/animals", response_model=List[Animal])
def get_animals():
    """
    Endpoint para obtener la lista de todos los animales registrados.
    Devuelve una lista de objetos Animal.
    """
    return animals_db