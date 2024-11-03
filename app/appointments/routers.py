from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import date, time

router = APIRouter()

# Modelo de datos para las citas
class Appointment(BaseModel):
    client_name: str
    pet_name: str
    date: date
    time: time
    reason: str

# Base de datos simulada en memoria
appointments_db = []

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: Appointment):
    appointments_db.append(appointment.dict())
    return appointment

@router.get("/", response_model=List[Appointment])
def get_appointments():
    return appointments_db

@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int):
    if 0 <= appointment_id < len(appointments_db):
        return appointments_db[appointment_id]
    raise HTTPException(status_code=404, detail="Cita no encontrada")

@router.put("/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: int, appointment_update: Appointment):
    if 0 <= appointment_id < len(appointments_db):
        appointments_db[appointment_id] = appointment_update.dict()
        return appointment_update
    raise HTTPException(status_code=404, detail="Cita no encontrada")

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int):
    if 0 <= appointment_id < len(appointments_db):
        appointments_db.pop(appointment_id)
        return {"message": "Cita eliminada exitosamente"}
    raise HTTPException(status_code=404, detail="Cita no encontrada")