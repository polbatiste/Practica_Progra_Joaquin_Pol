# routers_citas.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.data.models import Appointment as AppointmentModel
from database.engine import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

router = APIRouter()

class Appointment(BaseModel):
    id: Optional[int] = None
    date: date
    time: time
    treatment: str
    reason: str
    consultation: str
    owner_id: int
    animal_id: int

    class Config:
        orm_mode = True

@router.post("/appointments", response_model=Appointment, status_code=201)
def create_appointment(appointment: Appointment, db: Session = Depends(get_db)):
    # Verificar conflictos de fecha, hora y consulta
    existing_appointment = db.query(AppointmentModel).filter(
        AppointmentModel.date == appointment.date,
        AppointmentModel.time == appointment.time,
        AppointmentModel.consultation == appointment.consultation
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
        )
    
    db_appointment = AppointmentModel(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/appointments", response_model=List[Appointment])
def get_appointments(db: Session = Depends(get_db)):
    return db.query(AppointmentModel).all()

@router.put("/appointments/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: int, appointment_update: Appointment, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Verificar conflictos al actualizar
    conflict = db.query(AppointmentModel).filter(
        AppointmentModel.date == appointment_update.date,
        AppointmentModel.time == appointment_update.time,
        AppointmentModel.consultation == appointment_update.consultation,
        AppointmentModel.id != appointment_id
    ).first()
    
    if conflict:
        raise HTTPException(
            status_code=400,
            detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
        )
    
    for key, value in appointment_update.dict(exclude={'id'}).items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    db.delete(db_appointment)
    db.commit()
    return {"message": "Cita eliminada exitosamente"}