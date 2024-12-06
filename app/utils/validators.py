from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.data.models import Owner, Animal as AnimalModel

class AnimalValidator:
    @staticmethod
    def validate_owner_exists(db: Session, owner_id: int):
        """Verifica si el dueño existe en la base de datos."""
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="El dueño no existe")

    @staticmethod
    def validate_unique_animal(db: Session, name: str, owner_id: int):
        """Verifica si un animal con el mismo nombre y dueño ya existe."""
        existing_animal = db.query(AnimalModel).filter(
            AnimalModel.name == name,
            AnimalModel.owner_id == owner_id
        ).first()
        if existing_animal:
            raise HTTPException(status_code=400, detail="El animal ya existe")
