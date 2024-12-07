from abc import ABC, abstractmethod
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.data.models import Owner, Animal as AnimalModel

# Interfaces específicas para validaciones
class IValidateOwner(ABC):
    @abstractmethod
    def validate_owner_exists(self, db: Session, owner_id: int):
        pass

class IValidateAnimalUniqueness(ABC):
    @abstractmethod
    def validate_unique_animal(self, db: Session, name: str, owner_id: int):
        pass

class IValidator(IValidateOwner, IValidateAnimalUniqueness):
    """Interfaz que combina validaciones generales."""
    pass

# Implementaciones específicas
class AnimalValidator(IValidator):
    def validate_owner_exists(self, db: Session, owner_id: int):
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="El dueño no existe")

    def validate_unique_animal(self, db: Session, name: str, owner_id: int):
        existing_animal = db.query(AnimalModel).filter(
            AnimalModel.name == name,
            AnimalModel.owner_id == owner_id
        ).first()
        if existing_animal:
            raise HTTPException(status_code=400, detail="El animal ya existe")

class SpecialAnimalValidator(AnimalValidator):
    def validate_exotic_species(self, data: dict):
        if data.get("species") == "Exotic" and not data.get("permits"):
            raise HTTPException(
                status_code=400, detail="Exotic animals require permits"
            )
