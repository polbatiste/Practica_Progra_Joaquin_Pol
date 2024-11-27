# app/routers/routers_citas.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.data.models import Appointment as AppointmentModel, Invoice as InvoiceModel, Owner as OwnerModel
from database.engine import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

router = APIRouter()

# Modelo Pydantic para citas
class Appointment(BaseModel):
    id: Optional[int] = None
    date: date
    time: time
    treatment: str
    reason: str
    consultation: str
    owner_id: int
    animal_id: int
    completed: Optional[bool] = False  # Campo opcional para indicar si está completada

    class Config:
        orm_mode = True

# Modelo Pydantic para completar una cita
class CompleteAppointment(BaseModel):
    treatments: List[str]  # Lista de tratamientos realizados
    payment_method: str  # Forma de pago: transferencia, efectivo, tarjeta

# Crear una cita
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

# Obtener todas las citas
@router.get("/appointments", response_model=List[Appointment])
def get_appointments(db: Session = Depends(get_db)):
    return db.query(AppointmentModel).all()

# Actualizar una cita
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

# Eliminar una cita
@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    db.delete(db_appointment)
    db.commit()
    return {"message": "Cita eliminada exitosamente"}

# Completar una cita y generar factura
@router.put("/appointments/{appointment_id}/complete", status_code=201)
def complete_appointment(appointment_id: int, completion_data: CompleteAppointment, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    # Validar si la cita ya está completada
    if db_appointment.completed:
        raise HTTPException(status_code=400, detail="La cita ya fue completada.")

    # Actualizar la cita como completada
    db_appointment.completed = True
    db.commit()
    
    # Crear la factura asociada
    owner = db.query(OwnerModel).filter(OwnerModel.id == db_appointment.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Propietario no encontrado.")

    treatments_done = ", ".join(completion_data.treatments)
    total_price = len(completion_data.treatments) * 50.0  # Ejemplo: cada tratamiento cuesta 50 unidades

    invoice = InvoiceModel(
        appointment_id=appointment_id,
        owner_id=db_appointment.owner_id,
        treatments=treatments_done,
        total_price=total_price,
        payment_method=completion_data.payment_method,
        paid=False  # Por defecto, las facturas no están pagadas
    )

    db.add(invoice)
    db.commit()
    return {"message": "Cita completada y factura generada exitosamente."}