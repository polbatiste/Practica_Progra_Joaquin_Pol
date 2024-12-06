from sqlalchemy.orm import Session
from database.data.models import Animal as AnimalModel

class AnimalRepository:
    @staticmethod
    def add_animal(db: Session, animal_data: dict):
        """Crea un nuevo registro de animal en la base de datos."""
        db_animal = AnimalModel(**animal_data)
        db.add(db_animal)
        db.commit()
        db.refresh(db_animal)
        return db_animal
