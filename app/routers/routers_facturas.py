# app/routers/routers_facturas.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.data.models import Invoice as InvoiceModel, Owner as OwnerModel
from database.engine import get_db
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Modelo Pydantic para facturas
class Invoice(BaseModel):
    id: Optional[int] = None
    appointment_id: int
    owner_id: int
    treatments: str
    total_price: float
    payment_method: str
    paid: bool

    class Config:
        orm_mode = True

# Obtener todas las facturas con filtros opcionales
@router.get("/invoices", response_model=List[Invoice])
def get_invoices(paid: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(InvoiceModel)
    if paid is not None:
        query = query.filter(InvoiceModel.paid == paid)
    return query.all()

# Obtener una factura por ID
@router.get("/invoices/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice

# Actualizar el estado de pago de una factura
@router.put("/invoices/{invoice_id}/pay", response_model=Invoice)
def pay_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    invoice.paid = True
    db.commit()
    db.refresh(invoice)
    return invoice

# Descargar factura en formato PDF
@router.get("/invoices/{invoice_id}/download", status_code=200)
def download_invoice(invoice_id: int, db: Session = Depends(get_db)):
    from app.utils.pdf_generator import generate_pdf  # Importa la función para generar PDFs

    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    owner = db.query(OwnerModel).filter(OwnerModel.id == invoice.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    # Generar PDF con los datos de la factura
    pdf_path = generate_pdf(invoice, owner)
    return {"message": f"Factura descargada: {pdf_path}"}

# Enviar factura por correo
@router.post("/invoices/{invoice_id}/send-email", status_code=200)
def send_invoice_email(invoice_id: int, recipient_email: str, db: Session = Depends(get_db)):
    from app.utils.email_sender import send_email_with_attachment  # Importa la función para enviar correos
    from app.utils.pdf_generator import generate_pdf  # Genera el PDF antes de enviarlo

    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    owner = db.query(OwnerModel).filter(OwnerModel.id == invoice.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    # Generar el PDF de la factura
    pdf_path = generate_pdf(invoice, owner)

    # Enviar el PDF como archivo adjunto
    send_email_with_attachment(
        recipient_email,
        subject="Factura de la Clínica Veterinaria",
        body="Adjunto encontrará la factura correspondiente a su cita.",
        attachment_path=pdf_path
    )
    return {"message": f"Factura enviada a {recipient_email}"}