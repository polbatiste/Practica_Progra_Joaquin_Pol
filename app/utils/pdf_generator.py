from fpdf import FPDF
import os
from datetime import datetime

# Crear directorios necesarios al importar el módulo
os.makedirs("downloads", exist_ok=True)
os.makedirs("generated_invoices", exist_ok=True)

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_pdf(invoice, owner):
    """
    Genera un archivo PDF con los datos de la factura.
    :param invoice: Objeto de factura.
    :param owner: Objeto de propietario.
    :return: Ruta del archivo PDF generado.
    """
    # Configuración inicial del PDF
    pdf = PDF()
    pdf.set_display_mode('real')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Agregar logo
    logo_path = "streamlit/logo.jpg"
    if os.path.exists(logo_path):
        pdf.image(logo_path, 10, 8, 30)
    
    # Encabezado con datos de la clínica
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40)  # Espacio para el logo
    pdf.cell(150, 10, 'Clínica Veterinaria Mentema', 0, 1, 'R')
    pdf.set_font('Arial', '', 9)
    pdf.cell(40)
    pdf.cell(150, 5, 'C/ Principal, 123', 0, 1, 'R')
    pdf.cell(40)
    pdf.cell(150, 5, '28001 Madrid', 0, 1, 'R')
    pdf.cell(40)
    pdf.cell(150, 5, 'Tel: +34 911 234 567', 0, 1, 'R')
    pdf.cell(40)
    pdf.cell(150, 5, 'Email: info@mentema.com', 0, 1, 'R')

    # Línea separadora
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Número de factura y fecha
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'FACTURA Nº: {invoice.id}', 0, 1)
    pdf.set_font('Arial', '', 10)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 5, f'Fecha: {fecha_actual}', 0, 1)
    pdf.ln(10)

    # Información del cliente
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DATOS DEL CLIENTE', 1, 1, 'L', 1)
    pdf.set_font('Arial', '', 10)
    
    info_cliente = [
        f'Nombre: {owner.nombre}',
        f'DNI: {owner.dni}',
        f'Dirección: {owner.direccion}',
        f'Teléfono: {owner.telefono}',
        f'Email: {owner.correo_electronico}'
    ]
    
    for info in info_cliente:
        pdf.cell(0, 6, info, 'LR', 1)
    pdf.cell(0, 0, '', 'LRB', 1)  # Línea inferior del marco
    pdf.ln(10)
    
    # Información del animal
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DATOS DEL ANIMAL', 1, 1, 'L', 1)
    pdf.set_font('Arial', '', 10)
    
    # Necesitamos obtener el animal del appointment, asumiendo que está en invoice.appointment.animal
    if hasattr(invoice, 'appointment') and hasattr(invoice.appointment, 'animal'):
        animal = invoice.appointment.animal
        info_animal = [
            f'Nombre: {animal.name}',
            f'Especie: {animal.species}',
            f'Raza: {animal.breed}',
            f'Edad: {animal.age} años'
        ]
        
        for info in info_animal:
            pdf.cell(0, 6, info, 'LR', 1)
        pdf.cell(0, 0, '', 'LRB', 1)  # Línea inferior del marco
        
    pdf.ln(10)

    # Detalles de los servicios
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DETALLES DE LOS SERVICIOS', 1, 1, 'L', 1)
    
    # Cabecera de la tabla
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(130, 8, 'Descripción', 1, 0)
    pdf.cell(30, 8, 'Precio', 1, 1, 'R')
    
    # Contenido de la tabla
    pdf.set_font('Arial', '', 10)
    treatments = invoice.treatments.split(',')
    subtotal = invoice.total_price / (1 + 0.21)  # Asumiendo IVA del 21%
    
    for treatment in treatments:
        pdf.cell(130, 8, treatment.strip(), 1)
        pdf.cell(30, 8, f'{subtotal/len(treatments):.2f} EUR', 1, 1, 'R')

    # Totales
    pdf.ln(5)
    pdf.cell(130)
    pdf.cell(30, 8, f'Subtotal: {subtotal:.2f} EUR', 0, 1, 'R')
    pdf.cell(130)
    pdf.cell(30, 8, f'IVA (21%): {(invoice.total_price - subtotal):.2f} EUR', 0, 1, 'R')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(130)
    pdf.cell(30, 10, f'Total: {invoice.total_price:.2f} EUR', 0, 1, 'R')

    # Método de pago y estado
    pdf.ln(10)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f'Método de pago: {invoice.payment_method}', 0, 1)
    pdf.cell(0, 6, f'Estado: {"Pagada" if invoice.paid else "Pendiente"}', 0, 1)

    # Nota legal
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 4, 'Esta factura sirve como comprobante de pago y garantía de los servicios prestados. ' +
                        'Conserve este documento para futuras referencias. Gracias por confiar en Clínica Veterinaria Mentema.')

    # Guardar el PDF
    downloads_dir = "downloads"
    generated_dir = "generated_invoices"
    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(generated_dir, exist_ok=True)

    generated_path = os.path.join(generated_dir, f"invoice_{invoice.id}.pdf")
    download_path = os.path.join(downloads_dir, f"factura_{invoice.id}.pdf")

    try:
        pdf.output(generated_path, 'F')
        import shutil
        shutil.copy2(generated_path, download_path)
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        raise

    return generated_path