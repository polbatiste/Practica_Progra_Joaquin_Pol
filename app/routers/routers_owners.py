# app/routers/routers_owners.py

from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from database.data.models import Owner as OwnerModel
from database.engine import get_db
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter()

class Owner(BaseModel):
    id: Optional[int] = None  # Añade =None
    nombre: str
    dni: str
    direccion: str
    telefono: str
    correo_electronico: EmailStr

    class Config:
        from_attributes = True  # Actualiza esto también

@router.post("/owners", response_model=Owner, status_code=status.HTTP_201_CREATED)
def create_owner(owner: Owner, db: Session = Depends(get_db)):
    db_owner = db.query(OwnerModel).filter(OwnerModel.dni == owner.dni).first()
    if db_owner:
        raise HTTPException(status_code=400, detail="DNI ya registrado")
    db_owner = OwnerModel(**owner.dict())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner

@router.get("/owners", response_model=List[Owner])
def get_owners(db: Session = Depends(get_db)):
    return db.query(OwnerModel).all()

@router.get("/owners/{dni}", response_model=Owner)
def get_owner(dni: str, db: Session = Depends(get_db)):
    owner = db.query(OwnerModel).filter(OwnerModel.dni == dni).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return owner

@router.put("/owners/{dni}", response_model=Owner)
def update_owner(dni: str, owner_update: Owner, db: Session = Depends(get_db)):
    db_owner = db.query(OwnerModel).filter(OwnerModel.dni == dni).first()
    if not db_owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    
    for key, value in owner_update.dict().items():
        setattr(db_owner, key, value)
    
    db.commit()
    db.refresh(db_owner)
    return db_owner

@router.delete("/owners/{dni}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(dni: str, db: Session = Depends(get_db)):
    db_owner = db.query(OwnerModel).filter(OwnerModel.dni == dni).first()
    if not db_owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    
    db.delete(db_owner)
    db.commit()
    return {"message": "Dueño eliminado exitosamente"}

@router.get("/owners/search", response_model=List[Owner])
def search_owners(
    db: Session = Depends(get_db),
    nombre: Optional[str] = Query(None),
    dni: Optional[str] = Query(None),
    direccion: Optional[str] = Query(None),
    telefono: Optional[str] = Query(None),
    correo_electronico: Optional[str] = Query(None)
):
    query = db.query(OwnerModel)
    
    if nombre:
        query = query.filter(OwnerModel.nombre == nombre)
    if dni:
        query = query.filter(OwnerModel.dni == dni)
    if direccion:
        query = query.filter(OwnerModel.direccion == direccion)
    if telefono:
        query = query.filter(OwnerModel.telefono == telefono)
    if correo_electronico:
        query = query.filter(OwnerModel.correo_electronico == correo_electronico)
    
    results = query.all()
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron dueños con los criterios de búsqueda")
    return results