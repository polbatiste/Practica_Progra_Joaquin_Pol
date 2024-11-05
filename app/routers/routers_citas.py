from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time
from uuid import uuid4

router = APIRouter()

class Appointment(BaseModel):
    id: str = str(uuid4())  # Genera un ID único al crear una cita
    client_name: str
    pet_name: str
    date: date
    time: time
    treatment: str
    reason: str
    consultation: str  # Campo para la consulta (ejemplo: "a", "b", "c", "d")

appointments_db = []  # Lista en memoria para almacenar las citas

@router.post("/appointments", response_model=Appointment, status_code=201)
def create_appointment(appointment: Appointment):
    # Verificar conflictos de citas en la misma fecha, hora y consulta
    for existing_appointment in appointments_db:
        if (existing_appointment["date"] == appointment.date and
            existing_appointment["time"] == appointment.time and
            existing_appointment["consultation"] == appointment.consultation):
            raise HTTPException(
                status_code=400,
                detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
            )
    appointments_db.append(appointment.dict())
    return appointment

@router.get("/appointments", response_model=List[Appointment])
def get_appointments():
    return appointments_db

@router.put("/appointments/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: str, appointment_update: Appointment):
    for i, existing_appointment in enumerate(appointments_db):
        if existing_appointment["id"] == appointment_id:
            # Verificar conflictos de citas al actualizar
            for j, conflict_appointment in enumerate(appointments_db):
                if (j != i and
                    conflict_appointment["date"] == appointment_update.date and
                    conflict_appointment["time"] == appointment_update.time and
                    conflict_appointment["consultation"] == appointment_update.consultation):
                    raise HTTPException(
                        status_code=400,
                        detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
                    )
            appointments_db[i] = appointment_update.dict()
            return appointment_update
    raise HTTPException(status_code=404, detail="Cita no encontrada")

@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: str):
    for i, existing_appointment in enumerate(appointments_db):
        if existing_appointment["id"] == appointment_id:
            appointments_db.pop(i)
            return {"message": "Cita eliminada exitosamente"}
    raise HTTPException(status_code=404, detail="Cita no encontrada")