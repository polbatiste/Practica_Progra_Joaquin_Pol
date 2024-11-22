# routers_owners.py

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter()

# Modelo de datos para representar a los dueños
class Owner(BaseModel):
    nombre: str              # Nombre del dueño
    dni: str                 # DNI del dueño
    direccion: str           # Dirección
    telefono: str            # Teléfono
    correo_electronico: EmailStr  # Correo electrónico, validado como email

# Base de datos en memoria para almacenar dueños
owners_db = []

# Crear un nuevo dueño
@router.post("/owners", response_model=Owner, status_code=status.HTTP_201_CREATED)
def create_owner(owner: Owner):
    owners_db.append(owner.dict())
    return owner

# Obtener la lista de todos los dueños
@router.get("/owners", response_model=List[Owner])
def get_owners():
    return owners_db

# Obtener un dueño por su DNI
@router.get("/owners/{dni}", response_model=Owner)
def get_owner(dni: str):
    # Buscar el dueño por DNI
    owner = next((owner for owner in owners_db if owner['dni'] == dni), None)
    if not owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return owner

# Actualizar información de un dueño existente por DNI
@router.put("/owners/{dni}", response_model=Owner)
def update_owner(dni: str, owner_update: Owner):
    index = next((i for i, owner in enumerate(owners_db) if owner['dni'] == dni), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    owners_db[index] = owner_update.dict()  # Actualizar el dueño en la posición encontrada
    return owner_update

# Eliminar un dueño por DNI
@router.delete("/owners/{dni}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(dni: str):
    index = next((i for i, owner in enumerate(owners_db) if owner['dni'] == dni), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    owners_db.pop(index)  # Remover el dueño de la base de datos
    return {"message": "Dueño eliminado exitosamente"}

# Buscar dueños por múltiples criterios
@router.get("/owners/search", response_model=List[Owner])
def search_owners(
    nombre: Optional[str] = Query(None),
    dni: Optional[str] = Query(None),
    direccion: Optional[str] = Query(None),
    telefono: Optional[str] = Query(None),
    correo_electronico: Optional[str] = Query(None)
):
    # Filtrar la lista de dueños según los criterios de búsqueda
    results = [
        owner for owner in owners_db
        if (nombre is None or owner['nombre'].lower() == nombre.lower()) and
           (dni is None or owner['dni'] == dni) and
           (direccion is None or owner['direccion'].lower() == direccion.lower()) and
           (telefono is None or owner['telefono'] == telefono) and
           (correo_electronico is None or owner['correo_electronico'].lower() == correo_electronico.lower())
    ]
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron dueños con los criterios de búsqueda")
    return results