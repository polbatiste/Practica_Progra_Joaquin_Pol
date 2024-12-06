from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.engine import get_db
from utils.validators import AnimalValidator
from utils.repositories import AnimalRepository
from database.data.models import Animal as AnimalModel

router = APIRouter()

# Esquema para validar y serializar datos de animales
class Animal(BaseModel):
    id: Optional[int] = None
    name: str
    species: str
    breed: str
    age: int
    owner_id: int
    status: Optional[str] = "vivo"  # Estado por defecto

    class Config:
        orm_mode = True

# Crear un nuevo animal
@router.post("/animals", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(animal: Animal, db: Session = Depends(get_db)):
    """Crea un nuevo animal verificando las validaciones necesarias."""
    AnimalValidator.validate_owner_exists(db, animal.owner_id)
    AnimalValidator.validate_unique_animal(db, animal.name, animal.owner_id)
    return AnimalRepository.add_animal(db, animal.dict(exclude={'id'}))

# Obtener todos los animales
@router.get("/animals", response_model=List[Animal])
def get_animals(db: Session = Depends(get_db)):
    """Obtiene todos los animales registrados."""
    return db.query(AnimalModel).all()

# Contar el número total de animales
@router.get("/animals/count")
def get_animal_count(db: Session = Depends(get_db)):
    """Obtiene el número total de animales registrados."""
    count = db.query(AnimalModel).count()
    return {"total_animals": count}

# Obtener un animal específico por ID
@router.get("/animals/{animal_id}", response_model=Animal)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    """Obtiene un animal específico por su ID."""
    animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return animal

# Actualizar datos de un animal existente
@router.put("/animals/{animal_id}", response_model=Animal)
def update_animal(animal_id: int, animal: Animal, db: Session = Depends(get_db)):
    """Actualiza los datos de un animal."""
    db_animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    
    # Actualizar atributos
    for key, value in animal.dict(exclude_unset=True).items():
        setattr(db_animal, key, value)
    
    db.commit()
    db.refresh(db_animal)
    return db_animal

# Marcar un animal como fallecido
@router.patch("/animals/{animal_id}/deceased", response_model=Animal)
def mark_animal_deceased(animal_id: int, db: Session = Depends(get_db)):
    """Marca un animal como fallecido."""
    db_animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    
    db_animal.status = "fallecido"
    db.commit()
    db.refresh(db_animal)
    return db_animal

# Eliminar un animal por ID
@router.delete("/animals/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    """Elimina un animal por su ID."""
    db_animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    
    db.delete(db_animal)
    db.commit()
