from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import date, time

router = APIRouter()

class Appointment(BaseModel):
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

@router.put("/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: int, appointment_update: Appointment):
    if 0 <= appointment_id < len(appointments_db):
        # Verificar conflictos de citas al actualizar
        for i, existing_appointment in enumerate(appointments_db):
            if (i != appointment_id and
                existing_appointment["date"] == appointment_update.date and
                existing_appointment["time"] == appointment_update.time and
                existing_appointment["consultation"] == appointment_update.consultation):
                raise HTTPException(
                    status_code=400,
                    detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
                )
        appointments_db[appointment_id] = appointment_update.dict()
        return appointment_update
    raise HTTPException(status_code=404, detail="Cita no encontrada")

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int):
    if 0 <= appointment_id < len(appointments_db):
        appointments_db.pop(appointment_id)
        return {"message": "Cita eliminada exitosamente"}
    raise HTTPException(status_code=404, detail="Cita no encontrada")