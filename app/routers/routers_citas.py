from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time
import random

router = APIRouter()

# Modelo de datos para las citas
class Appointment(BaseModel):
    id: Optional[str] = None  # ID opcional, se generará si no se proporciona
    client_name: str          # Nombre del cliente
    pet_name: str             # Nombre de la mascota
    date: date                # Fecha de la cita
    time: time                # Hora de la cita
    treatment: str            # Tipo de tratamiento
    reason: str               # Razón de la cita
    consultation: str         # Consulta en la que se realiza (ej., "a", "b", "c")

appointments_db = []  # Base de datos simulada en memoria para citas

# Genera un ID único de 4 dígitos para una nueva cita
def generate_appointment_id():
    return str(random.randint(1000, 9999))

# Crear una nueva cita
@router.post("/appointments", response_model=Appointment, status_code=201)
def create_appointment(appointment: Appointment):
    # Generar un ID único si no se proporciona uno
    if appointment.id is None:
        appointment.id = generate_appointment_id()
        # Evitar colisiones de ID
        while any(existing["id"] == appointment.id for existing in appointments_db):
            appointment.id = generate_appointment_id()

    # Verificar conflictos de fecha, hora y consulta
    for existing in appointments_db:
        if (existing["date"] == appointment.date and
            existing["time"] == appointment.time and
            existing["consultation"] == appointment.consultation):
            raise HTTPException(
                status_code=400,
                detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
            )

    # Almacenar la nueva cita
    appointments_db.append(appointment.dict())
    return appointment

# Obtener todas las citas
@router.get("/appointments", response_model=List[Appointment])
def get_appointments():
    return appointments_db

# Actualizar una cita existente
@router.put("/appointments/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: str, appointment_update: Appointment):
    for i, existing in enumerate(appointments_db):
        if existing["id"] == appointment_id:
            # Verificar conflictos al actualizar
            for j, conflict in enumerate(appointments_db):
                if (j != i and
                    conflict["date"] == appointment_update.date and
                    conflict["time"] == appointment_update.time and
                    conflict["consultation"] == appointment_update.consultation):
                    raise HTTPException(
                        status_code=400,
                        detail="Conflicto: Ya existe una cita en esa fecha, hora y consulta."
                    )

            # Actualizar la cita manteniendo el mismo ID
            appointment_update.id = appointment_id
            appointments_db[i] = appointment_update.dict()
            return appointment_update

    raise HTTPException(status_code=404, detail="Cita no encontrada")

# Eliminar una cita
@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: str):
    for i, existing in enumerate(appointments_db):
        if existing["id"] == appointment_id:
            appointments_db.pop(i)
            return {"message": "Cita eliminada exitosamente"}

    raise HTTPException(status_code=404, detail="Cita no encontrada")