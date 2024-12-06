from abc import ABC, abstractmethod
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.data.models import Owner, Animal as AnimalModel

class IValidator(ABC):
    """Interfaz base para los validadores."""
    @abstractmethod
    def validate(self, db: Session, data: dict):
        pass

class AnimalValidator(IValidator):
    """Validador para animales estándar."""
    @staticmethod
    def validate_owner_exists(db: Session, owner_id: int):
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="El dueño no existe")

    @staticmethod
    def validate_unique_animal(db: Session, name: str, owner_id: int):
        existing_animal = db.query(AnimalModel).filter(
            AnimalModel.name == name,
            AnimalModel.owner_id == owner_id
        ).first()
        if existing_animal:
            raise HTTPException(status_code=400, detail="El animal ya existe")

    def validate(self, db: Session, data: dict):
        self.validate_owner_exists(db, data["owner_id"])
        self.validate_unique_animal(db, data["name"], data["owner_id"])

class SpecialAnimalValidator(AnimalValidator):
    """Extensión para validaciones especiales."""
    @staticmethod
    def validate_exotic_species(data: dict):
        if data.get("species") == "Exotic" and not data.get("permits"):
            raise HTTPException(
                status_code=400, detail="Exotic animals require permits"
            )

    def validate(self, db: Session, data: dict):
        super().validate(db, data)
        self.validate_exotic_species(data)
