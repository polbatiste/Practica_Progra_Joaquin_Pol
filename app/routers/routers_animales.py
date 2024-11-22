# app/routers/routers_animales.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.data.models import Animal as AnimalModel
from database.engine import get_db
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Animal(BaseModel):
    id: Optional[int] = None
    name: str
    species: str
    breed: str
    age: int
    owner_id: int

    class Config:
        orm_mode = True

@router.post("/animals", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(animal: Animal, db: Session = Depends(get_db)):
    # Comprobar duplicados
    existing_animal = db.query(AnimalModel).filter(
        AnimalModel.name == animal.name,
        AnimalModel.owner_id == animal.owner_id
    ).first()
    
    if existing_animal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El animal ya existe para este propietario"
        )
    
    db_animal = AnimalModel(**animal.dict(exclude={'id'}))
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal

@router.get("/animals", response_model=List[Animal])
def get_animals(db: Session = Depends(get_db)):
    return db.query(AnimalModel).all()

@router.get("/animals/count")
def get_animal_count(db: Session = Depends(get_db)):
    return {"total_animals": db.query(AnimalModel).count()}

@router.get("/animals/{animal_id}", response_model=Animal)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    db_animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return db_animal

@router.delete("/animals/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    db_animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    
    db.delete(db_animal)
    db.commit()
    return {"message": "Animal eliminado exitosamente"}