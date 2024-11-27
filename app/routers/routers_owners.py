# app/routers/routers_owners.py

from fastapi import APIRouter, HTTPException, status, Query, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database.data.models import Owner as OwnerModel, Animal as AnimalModel
from database.engine import get_db
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from utils.email_sender import send_email_with_attachment

router = APIRouter()

class Owner(BaseModel):
    id: Optional[int] = None
    nombre: str
    dni: str
    direccion: str
    telefono: str
    correo_electronico: EmailStr

    class Config:
        from_attributes = True

class DeleteRequest(BaseModel):
    dni: str
    email: EmailStr
    reason: Optional[str] = None

async def delete_owner_and_pets(dni: str, db: Session):
    try:
        db_owner = db.query(OwnerModel).filter(OwnerModel.dni == dni).first()
        if not db_owner:
            raise HTTPException(status_code=404, detail="Dueño no encontrado")
        
        # Eliminar mascotas asociadas
        db.query(AnimalModel).filter(AnimalModel.owner_id == db_owner.id).delete()
        
        # Eliminar dueño
        db.delete(db_owner)
        db.commit()
        
        return {"message": "Dueño y mascotas eliminados exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")

@router.post("/owners", response_model=Owner, status_code=status.HTTP_201_CREATED)
def create_owner(owner: Owner, db: Session = Depends(get_db)):
    db_owner = db.query(OwnerModel).filter(OwnerModel.dni == owner.dni).first()
    if db_owner:
        raise HTTPException(status_code=400, detail="DNI ya registrado")
    db_owner = OwnerModel(**owner.dict())
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    return db_owner

@router.get("/owners", response_model=List[Owner])
def get_owners(db: Session = Depends(get_db)):
    return db.query(OwnerModel).all()

@router.get("/owners/search", response_model=List[Owner])
def search_owners(
    db: Session = Depends(get_db),
    nombre: Optional[str] = Query(None),
    dni: Optional[str] = Query(None),
    direccion: Optional[str] = Query(None),
    telefono: Optional[str] = Query(None),
    correo_electronico: Optional[str] = Query(None)
):
    query = db.query(OwnerModel)
    
    if nombre:
        query = query.filter(OwnerModel.nombre == nombre)
    if dni:
        query = query.filter(OwnerModel.dni == dni)
    if direccion:
        query = query.filter(OwnerModel.direccion == direccion)
    if telefono:
        query = query.filter(OwnerModel.telefono == telefono)
    if correo_electronico:
        query = query.filter(OwnerModel.correo_electronico == correo_electronico)
    
    results = query.all()
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron dueños con los criterios de búsqueda")
    return results

@router.get("/owners/{dni}", response_model=Owner)
def get_owner(dni: str, db: Session = Depends(get_db)):
    owner = db.query(OwnerModel).filter(OwnerModel.dni == dni).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return owner

@router.put("/owners/{dni}", response_model=Owner)
def update_owner(dni: str, owner_update: Owner, db: Session = Depends(get_db)):
    db_owner = db.query(OwnerModel).filter(OwnerModel.dni == dni).first()
    if not db_owner:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    
    for key, value in owner_update.dict().items():
        setattr(db_owner, key, value)
    
    db.commit()
    db.refresh(db_owner)
    return db_owner

@router.post("/owners/delete-request")
async def request_deletion(
    delete_request: DeleteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_owner = db.query(OwnerModel).filter(
        OwnerModel.dni == delete_request.dni,
        OwnerModel.correo_electronico == delete_request.email
    ).first()
    
    if not db_owner:
        raise HTTPException(
            status_code=404,
            detail="No se encontró un dueño con el DNI y correo proporcionados"
        )
    
    # Preparar el correo de confirmación
    subject = "Confirmación de eliminación de datos - Clínica Veterinaria"
    body = f"""
    Estimado/a {db_owner.nombre},

    Hemos recibido su solicitud de eliminación de datos de nuestro sistema.
    Para confirmar la eliminación de sus datos y los de sus mascotas asociadas, por favor haga clic en el siguiente enlace:
    
    http://localhost:8501/?delete={db_owner.dni}
    
    Si no ha solicitado esta eliminación, por favor ignore este correo.

    Razón proporcionada para la eliminación: {delete_request.reason if delete_request.reason else 'No especificada'}

    Atentamente,
    Clínica Veterinaria
    """
    
    email_sent = send_email_with_attachment(
        recipient_email=delete_request.email,
        subject=subject,
        body=body,
        attachment_path=None
    )
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo de confirmación"
        )
    
    return {"message": "Solicitud de eliminación recibida. Se ha enviado un correo de confirmación."}

@router.delete("/owners/{dni}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_owner(dni: str, db: Session = Depends(get_db)):
    try:
        result = await delete_owner_and_pets(dni, db)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))