from pydantic import BaseModel, EmailStr

class DuenoCreate(BaseModel):
    nombre: str
    dni: str
    direccion: str
    telefono: str
    correo: EmailStr