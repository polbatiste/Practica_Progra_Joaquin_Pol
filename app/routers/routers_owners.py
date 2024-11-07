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

# Endpoint para crear un nuevo dueño
@router.post("/owners", response_model=Owner, status_code=status.HTTP_201_CREATED)
def create_owner(owner: Owner):
    # Verificar si ya existe un dueño con el mismo DNI para evitar duplicados
    if any(existing_owner['dni'] == owner.dni for existing_owner in owners_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El dueño ya existe con el DNI proporcionado"
        )
    # Agregar el nuevo dueño a la base de datos
    owners_db.append(owner.dict())
    return owner

# Endpoint para obtener todos los dueños
@router.get("/owners", response_model=List[Owner])
def get_owners():
    return owners_db

# Endpoint para obtener un dueño por DNI
@router.get("/owners/{dni}", response_model=Owner)
def get_owner(dni: str):
    owner = next((owner for owner in owners_db if owner['dni'] == dni), None)
    if not owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return owner

# Endpoint para actualizar un dueño por DNI
@router.put("/owners/{dni}", response_model=Owner)
def update_owner(dni: str, owner_update: Owner):
    index = next((index for index, owner in enumerate(owners_db) if owner['dni'] == dni), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    owners_db[index] = owner_update.dict()
    return owner_update

# Endpoint para eliminar un dueño por DNI
@router.delete("/owners/{dni}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(dni: str):
    index = next((index for index, owner in enumerate(owners_db) if owner['dni'] == dni), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    owners_db.pop(index)
    return {"message": "Dueño eliminado exitosamente"}
