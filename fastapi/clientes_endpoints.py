from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from clientes.models import Dueno
from pydantic import BaseModel
from database import get_db  # Asegúrate de tener esta función para obtener la sesión de base de datos

router = APIRouter()

class DuenoCreate(BaseModel):
    nombre: str
    dni: str
    direccion: str
    telefono: str
    correo: str

@router.post("/duenos/")
def crear_dueno(dueno: DuenoCreate, db: Session = Depends(get_db)):
    db_dueno = Dueno(**dueno.dict())
    db.add(db_dueno)
    try:
        db.commit()
        db.refresh(db_dueno)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el dueño")
    return db_dueno