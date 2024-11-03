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
