from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List

router = APIRouter()

# Modelo de datos para los dueños
class Owner(BaseModel):
    nombre: str
    dni: str
    direccion: str
    telefono: str
    correo_electronico: EmailStr

# Base de datos simulada en memoria
owners_db = []

@router.post("/owners", response_model=Owner, status_code=status.HTTP_201_CREATED)
def create_owner(owner: Owner):
    owners_db.append(owner.dict())
    return owner

@router.get("/owners", response_model=List[Owner])
def get_owners():
    return owners_db

@router.get("/owners/{dni}", response_model=Owner)
def get_owner(dni: str):
    owner = next((owner for owner in owners_db if owner['dni'] == dni), None)
    if not owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return owner

@router.put("/owners/{dni}", response_model=Owner)
def update_owner(dni: str, owner_update: Owner):
    index = next((index for index, owner in enumerate(owners_db) if owner['dni'] == dni), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    owners_db[index] = owner_update.dict()
    return owner_update

@router.delete("/owners/{dni}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(dni: str):
    index = next((index for index, owner in enumerate(owners_db) if owner['dni'] == dni), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    owners_db.pop(index)
    return {"message": "Dueño eliminado exitosamente"}