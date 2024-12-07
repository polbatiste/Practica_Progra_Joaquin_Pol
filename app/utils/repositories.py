from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from database.data.models import Animal as AnimalModel

# Interfaces específicas para operaciones de repositorios
class IAddRepository(ABC):
    @abstractmethod
    def add(self, db: Session, data: dict):
        pass

class IRepository(IAddRepository):
    """Interfaz combinada para repositorios."""
    pass

# Implementaciones específicas
class AnimalRepository(IRepository):
    def add(self, db: Session, data: dict):
        db_animal = AnimalModel(**data)
        db.add(db_animal)
        db.commit()
        db.refresh(db_animal)
        return db_animal

class ExoticAnimalRepository(AnimalRepository):
    def add(self, db: Session, data: dict):
        if data.get("species") == "Exotic":
            data["status"] = "Requires special care"
        return super().add(db, data)
