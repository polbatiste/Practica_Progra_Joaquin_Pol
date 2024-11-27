from fpdf import FPDF
import os

def generate_pdf(invoice, owner):
    """
    Genera un archivo PDF con los datos de la factura.
    :param invoice: Objeto de factura.
    :param owner: Objeto de propietario.
    :return: Ruta del archivo PDF generado.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Encabezado
    pdf.cell(200, 10, txt="Factura - Clínica Veterinaria", ln=True, align='C')

    # Información del propietario
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Propietario: {owner.nombre}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {owner.dni}", ln=True)
    pdf.cell(200, 10, txt=f"Dirección: {owner.direccion}", ln=True)
    pdf.cell(200, 10, txt=f"Teléfono: {owner.telefono}", ln=True)
    pdf.cell(200, 10, txt=f"Correo electrónico: {owner.correo_electronico}", ln=True)

    # Información de la factura
    pdf.ln(10)
    pdf.cell(200, 10, txt="Detalles de la factura:", ln=True)
    pdf.cell(200, 10, txt=f"ID de la factura: {invoice.id}", ln=True)
    pdf.cell(200, 10, txt=f"Tratamientos realizados: {invoice.treatments}", ln=True)
    pdf.cell(200, 10, txt=f"Total: {invoice.total_price} EUR", ln=True)
    pdf.cell(200, 10, txt=f"Método de pago: {invoice.payment_method}", ln=True)
    pdf.cell(200, 10, txt=f"Estado de pago: {'Pagada' if invoice.paid else 'Pendiente'}", ln=True)

    # Guardar el PDF
    output_dir = "generated_invoices"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"invoice_{invoice.id}.pdf")
    pdf.output(file_path)

    return file_path