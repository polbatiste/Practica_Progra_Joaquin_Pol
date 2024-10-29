from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from clientes.models.models import Dueno
from clientes.schemas.schemas import DuenoCreate
from database import get_db

router = APIRouter()

@router.post("/duenos/")
def crear_dueno(dueno: DuenoCreate, db: Session = Depends(get_db)):
    db_dueno = Dueno(**dueno.dict())
    db.add(db_dueno)
    try:
        db.commit()
        db.refresh(db_dueno)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al registrar el dueño: {e}")
    return db_dueno