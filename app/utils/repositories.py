from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from database.data.models import Animal as AnimalModel

class IRepository(ABC):
    """Interfaz base para los repositorios."""
    @abstractmethod
    def add(self, db: Session, data: dict):
        pass

class AnimalRepository(IRepository):
    """Repositorio para animales estándar."""
    def add(self, db: Session, data: dict):
        db_animal = AnimalModel(**data)
        db.add(db_animal)
        db.commit()
        db.refresh(db_animal)
        return db_animal

class ExoticAnimalRepository(AnimalRepository):
    """Repositorio especializado para animales exóticos."""
    def add(self, db: Session, data: dict):
        if data.get("species") == "Exotic":
            data["status"] = "Requires special care"
        return super().add(db, data)
