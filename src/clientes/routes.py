from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import Dueno, Base
from ..database import get_db  # Asumiendo que tienes un archivo database.py para conectar a la base de datos

router = APIRouter()

@router.post("/duenos/", response_model=Dueno)
def crear_dueno(nombre: str, dni: str, direccion: str, telefono: str, correo_electronico: str, db: Session = Depends(get_db)):
    nuevo_dueno = Dueno(
        nombre=nombre,
        dni=dni,
        direccion=direccion,
        telefono=telefono,
        correo_electronico=correo_electronico
    )
    db.add(nuevo_dueno)
    try:
        db.commit()
        db.refresh(nuevo_dueno)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear el dueño")
    return nuevo_dueno