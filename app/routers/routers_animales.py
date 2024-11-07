from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

# Definición del modelo de datos para Animal
class Animal(BaseModel):
    id: Optional[str] = None  # El ID se generará automáticamente si no se proporciona
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
    
    # Generación de un ID único para el animal
    animal.id = generate_animal_id()
    while any(existing_animal["id"] == animal.id for existing_animal in animals_db):
        animal.id = generate_animal_id()
    
    animals_db.append(animal.dict())
    return animal

# Endpoint para obtener todos los animales
@router.get("/animals", response_model=List[Animal])
def get_animals():
    return animals_db

# Endpoint para obtener un animal por ID
@router.get("/animals/{animal_id}", response_model=Animal)
def get_animal(animal_id: str):
    animal = next((a for a in animals_db if a["id"] == animal_id), None)
    if animal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal no encontrado")
    return animal

# Endpoint para actualizar un animal por ID
@router.put("/animals/{animal_id}", response_model=Animal)
def update_animal(animal_id: str, animal: Animal):
    for idx, existing_animal in enumerate(animals_db):
        if existing_animal["id"] == animal_id:
            updated_animal = animal.dict()
            updated_animal["id"] = animal_id  # Asegurar que el ID no cambie
            animals_db[idx] = updated_animal
            return updated_animal
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal no encontrado")

# Endpoint para eliminar un animal por ID
@router.delete("/animals/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(animal_id: str):
    global animals_db
    animals_db = [animal for animal in animals_db if animal["id"] != animal_id]
    return {"message": "Animal eliminado exitosamente"}
