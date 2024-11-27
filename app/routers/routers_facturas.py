from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.data.models import Invoice as InvoiceModel, Owner as OwnerModel
from database.engine import get_db
from pydantic import BaseModel, EmailStr
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

# Modelo para el email
class EmailSchema(BaseModel):
    recipient_email: EmailStr

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
@router.get("/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: int, db: Session = Depends(get_db)):
    try:
        from utils.pdf_generator import generate_pdf
        
        invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        
        owner = db.query(OwnerModel).filter(OwnerModel.id == invoice.owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Propietario no encontrado")
        
        pdf_path = generate_pdf(invoice, owner)
        
        headers = {
            "Content-Disposition": f"attachment; filename=factura_{invoice_id}.pdf",
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Access-Control-Allow-Headers": "Content-Disposition"
        }
        
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"factura_{invoice_id}.pdf",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar o descargar la factura: {str(e)}")

# Enviar factura por correo
@router.post("/invoices/{invoice_id}/send-email", status_code=200)
def send_invoice_email(
    invoice_id: int, 
    email_data: EmailSchema,
    db: Session = Depends(get_db)
):
    from utils.email_sender import send_email_with_attachment
    from utils.pdf_generator import generate_pdf

    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    owner = db.query(OwnerModel).filter(OwnerModel.id == invoice.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    # Generar el PDF de la factura
    pdf_path = generate_pdf(invoice, owner)

    try:
        # Enviar el PDF como archivo adjunto
        send_email_with_attachment(
            email_data.recipient_email,
            subject="Factura de la Clínica Veterinaria",
            body="Adjunto encontrará la factura correspondiente a su cita.",
            attachment_path=pdf_path
        )
        return {"message": f"Factura enviada a {email_data.recipient_email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el email: {str(e)}")