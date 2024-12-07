from fpdf import FPDF
import os
from datetime import datetime

# Crear directorios necesarios al importar el módulo
os.makedirs("downloads", exist_ok=True)
os.makedirs("generated_invoices", exist_ok=True)

class PDF(FPDF):
    def footer(self):
        # Agregar línea separadora
        self.set_y(-20)
        self.line(10, self.get_y(), 200, self.get_y())
        
        # Agregar footer con número de página
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
    pdf.set_auto_page_break(auto=True, margin=20)

    # Catálogo completo de tratamientos con precios y descripciones
    tratamientos_info = {
        # Tratamientos básicos
        "Análisis de sangre": {"precio": 50.0, "descripcion": "Análisis de sangre completo"},
        "Análisis hormonales": {"precio": 70.0, "descripcion": "Detección de niveles hormonales"},
        "Vacunación": {"precio": 30.0, "descripcion": "Vacunas generales"},
        "Desparasitación": {"precio": 25.0, "descripcion": "Eliminación de parásitos internos y externos"},
        
        # Revisión general
        "Revisión general": {"precio": 60.0, "descripcion": "Revisión completa del animal"},
        
        # Revisión específica
        "Revisión cardiológica": {"precio": 120.0, "descripcion": "Examen especializado del corazón"},
        "Revisión cutánea": {"precio": 80.0, "descripcion": "Evaluación de la piel y pelaje"},
        "Revisión broncológica": {"precio": 90.0, "descripcion": "Revisión de vías respiratorias"},
        
        # Ecografías
        "Ecografía abdominal": {"precio": 150.0, "descripcion": "Ecografía de la cavidad abdominal"},
        "Ecografía cardíaca": {"precio": 180.0, "descripcion": "Ecografía para evaluar el corazón"},
        
        # Tratamientos dentales
        "Limpieza bucal": {"precio": 100.0, "descripcion": "Limpieza profunda de dientes"},
        "Extracción de piezas dentales": {"precio": 200.0, "descripcion": "Extracción quirúrgica de dientes dañados"},
        
        # Cirugías
        "Castración": {"precio": 150.0, "descripcion": "Castración quirúrgica"},
        "Cirugía abdominal": {"precio": 300.0, "descripcion": "Procedimientos quirúrgicos abdominales"},
        "Cirugía cardíaca": {"precio": 500.0, "descripcion": "Cirugía en el corazón"},
        "Cirugía articular y ósea": {"precio": 400.0, "descripcion": "Reparación de articulaciones y huesos"},
        "Cirugía de hernias": {"precio": 250.0, "descripcion": "Reparación de hernias"}
    }

    # Agregar logo
    logo_path = "streamlit/logo.jpg"
    if os.path.exists(logo_path):
        pdf.image(logo_path, 10, 8, 30)

    # Estilo para el encabezado de la clínica
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40)
    pdf.cell(150, 10, 'Clínica Veterinaria Mentema', 0, 1, 'R')
    
    # Información de contacto de la clínica
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(100, 100, 100)
    for info in ['C/ Principal, 123', '28001 Madrid', 'Tel: +34 911 234 567', 'Email: veterinaria.mentema@gmail.com']:
        pdf.cell(40)
        pdf.cell(150, 5, info, 0, 1, 'R')

    # Línea separadora con degradado
    pdf.ln(5)
    pdf.set_draw_color(44, 62, 80)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Número de factura y fecha con estilo mejorado
    pdf.set_text_color(44, 62, 80)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'FACTURA Nº: {invoice.id}', 0, 1)
    pdf.set_font('Arial', '', 10)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 5, f'Fecha de emisión: {fecha_actual}', 0, 1)
    pdf.ln(10)

    # Información del cliente con estilo mejorado
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DATOS DEL CLIENTE', 1, 1, 'L', 1)
    
    # Restaurar colores para el contenido
    pdf.set_text_color(0, 0, 0)
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
    pdf.cell(0, 0, '', 'LRB', 1)
    pdf.ln(10)

    # Detalles de los servicios con estilo mejorado
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DETALLES DE LOS SERVICIOS', 1, 1, 'L', 1)
    
    # Cabecera de la tabla
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 8, 'Descripción', 1, 0, 'L', 1)
    pdf.cell(70, 8, 'Detalle', 1, 0, 'L', 1)
    pdf.cell(30, 8, 'Precio', 1, 1, 'R', 1)
    
    # Contenido de la tabla
    pdf.set_font('Arial', '', 9)
    treatments = invoice.treatments.split(',') if invoice.treatments else []
    subtotal = 0

    for treatment in treatments:
        treatment = treatment.strip()
        if treatment in tratamientos_info:
            info = tratamientos_info[treatment]
            pdf.cell(90, 8, treatment, 1)
            pdf.cell(70, 8, info["descripcion"], 1)
            pdf.cell(30, 8, f'{info["precio"]:.2f} EUR', 1, 1, 'R')
            subtotal += info["precio"]

    # Resumen financiero con estilo mejorado
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    
    # Calcular totales
    iva = round(subtotal * 0.21, 2)
    total = round(subtotal + iva, 2)
    
    # Cuadro de totales alineado a la derecha
    pdf.cell(130)
    pdf.cell(30, 8, 'Subtotal:', 0)
    pdf.cell(30, 8, f'{subtotal:.2f} EUR', 0, 1, 'R')
    
    pdf.cell(130)
    pdf.cell(30, 8, 'IVA (21%):', 0)
    pdf.cell(30, 8, f'{iva:.2f} EUR', 0, 1, 'R')
    
    # Línea separadora para el total
    pdf.cell(130)
    pdf.set_draw_color(44, 62, 80)
    pdf.line(160, pdf.get_y(), 200, pdf.get_y())
    
    # Total en negrita
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(130)
    pdf.cell(30, 10, 'Total:', 0)
    pdf.cell(30, 10, f'{total:.2f} EUR', 0, 1, 'R')

    # Información de pago y estado
    pdf.ln(10)
    pdf.set_font('Arial', '', 10)
    pdf.set_draw_color(200, 200, 200)
    pdf.cell(0, 6, f'Método de pago: {invoice.payment_method}', 'T', 1)
    pdf.cell(0, 6, f'Estado: {"Pagada" if invoice.paid else "Pendiente"}', 'B', 1)

    # Nota legal con estilo mejorado
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128)
    pdf.multi_cell(0, 4, 'Esta factura sirve como comprobante de pago y garantía de los servicios prestados. ' +
                        'Los precios incluyen IVA según la legislación vigente. ' +
                        'Conserve este documento para futuras referencias. ' +
                        'Gracias por confiar en Clínica Veterinaria Mentema.')

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