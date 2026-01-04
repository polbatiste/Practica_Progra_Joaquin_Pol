import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Facturación",
    page_icon="🏥",
    layout="wide"
)

# Estilos personalizados (Mantenidos exactamente igual)
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton button {
        background-color: #2c3e50;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    h1 { color: #2c3e50; padding-bottom: 1rem; border-bottom: 2px solid #eee; }
    h2 { color: #34495e; margin-top: 2rem; }
    .status-paid { color: #28a745; font-weight: 500; }
    .status-pending { color: #dc3545; font-weight: 500; }
    .invoice-table { margin: 2rem 0; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# URLs de la API
url_invoices = "http://localhost:8000/api/v1/invoices"
url_tratamientos = "http://localhost:8000/api/v1/tratamientos"


# --- NUEVA FUNCIÓN: GENERACIÓN DE PDF LOCAL ---
def generar_pdf_local(factura):
    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "CLINICA VETERINARIA MENTEMA", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, "Factura de Servicios Profesionales", ln=True, align='C')
    pdf.ln(10)

    # Datos de la factura
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, f"Factura ID:", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(factura['id']), ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, f"Fecha:", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, f"ID Propietario:", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(factura['owner_id']), ln=True)
    pdf.ln(5)

    # Detalle
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Servicios y Tratamientos:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, str(factura['treatments']))
    pdf.ln(5)

    # Total
    pdf.set_font("Arial", 'B', 14)
    total = factura.get('total_price', '0.00')
    pdf.cell(190, 10, f"TOTAL A PAGAR: {total} EUR", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')


# --- FUNCIONES DE UTILIDAD (REESCRITAS) ---
def obtener_facturas(filtrar_pagadas=None):
    try:
        params = {"paid": filtrar_pagadas} if filtrar_pagadas is not None else {}
        respuesta = requests.get(url_invoices, params=params, timeout=5)
        respuesta.raise_for_status()
        return respuesta.json()
    except:
        st.error("Error de conexión con MongoDB / API")
        return []


def marcar_pagada(invoice_id):
    try:
        respuesta = requests.put(f"{url_invoices}/{invoice_id}/pay")
        if respuesta.status_code == 200:
            st.success("Factura actualizada")
            st.rerun()
    except:
        st.error("No se pudo conectar con el servidor")


# --- INTERFAZ PRINCIPAL ---
st.title("Sistema de Facturación")

# Sidebar con botón de refresco
with st.sidebar:
    if st.button("🔄 Refrescar Datos"):
        st.cache_data.clear()
        st.rerun()

tab1, tab2 = st.tabs(["Facturas", "Gestión de Facturas"])

with tab1:
    st.header("Estado de Facturación")
    col1, col2 = st.columns([4, 6])
    with col1:
        filtro = st.radio("Filtrar por estado", options=["Todas", "Pagadas", "Pendientes"], horizontal=True)

    filtrar_pagadas = None if filtro == "Todas" else (filtro == "Pagadas")
    facturas = obtener_facturas(filtrar_pagadas)

    if facturas:
        df = pd.DataFrame(facturas)
        df["Estado"] = df["paid"].apply(lambda
                                            x: '<span class="status-paid">Pagada</span>' if x else '<span class="status-pending">Pendiente</span>')

        df_mostrar = df.rename(columns={
            "id": "ID", "appointment_id": "ID Cita", "owner_id": "ID Propietario",
            "treatments": "Tratamientos", "payment_method": "Método", "Estado": "Estado"
        })

        st.markdown('<div class="invoice-table">', unsafe_allow_html=True)
        st.write(df_mostrar[["ID", "Tratamientos", "Método", "Estado"]].to_html(escape=False, index=False,
                                                                                classes=['table']),
                 unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No hay facturas registradas")

with tab2:
    st.header("Gestión de Facturas")
    col_id, col_mail = st.columns(2)
    with col_id:
        id_factura = st.text_input("ID de la Factura (Copiar de la tabla)")
    with col_mail:
        correo = st.text_input("Correo electrónico del cliente")

    if id_factura:
        # Buscamos los datos de la factura seleccionada para el PDF
        factura_sel = next((f for f in facturas if str(f['id']) == id_factura), None)

        if factura_sel:
            st.markdown("### Acciones Disponibles")
            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("Marcar como Pagada", key="pago"):
                    marcar_pagada(id_factura)

            with c2:
                # GENERACIÓN LOCAL
                pdf_bytes = generar_pdf_local(factura_sel)
                st.download_button(
                    label="Descargar PDF (Local)",
                    data=pdf_bytes,
                    file_name=f"factura_{id_factura}.pdf",
                    mime="application/pdf"
                )

            with c3:
                if st.button("Simular Envío Email"):
                    if correo:
                        st.success(f"Factura preparada para enviar a {correo}")
                    else:
                        st.warning("Falta el correo")
        else:
            st.error("ID de factura no encontrado en los registros actuales")
    else:
        st.warning("Ingrese un ID de factura para operar")