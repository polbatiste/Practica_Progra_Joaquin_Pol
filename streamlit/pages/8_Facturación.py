import streamlit as st
import requests
import pandas as pd
import os

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Facturación",
    page_icon="🏥",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        background-color: #2c3e50;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div > input {
        border-radius: 4px;
    }
    h1 {
        color: #2c3e50;
        padding-bottom: 1rem;
        border-bottom: 2px solid #eee;
    }
    h2 {
        color: #34495e;
        margin-top: 2rem;
    }
    .success {
        padding: 1rem;
        border-radius: 4px;
        background-color: #d4edda;
        color: #155724;
    }
    .error {
        padding: 1rem;
        border-radius: 4px;
        background-color: #f8d7da;
        color: #721c24;
    }
    .warning {
        padding: 1rem;
        border-radius: 4px;
        background-color: #fff3cd;
        color: #856404;
    }
    .status-paid {
        color: #28a745;
        font-weight: 500;
    }
    .status-pending {
        color: #dc3545;
        font-weight: 500;
    }
    .invoice-table {
        margin: 2rem 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .price-column {
        text-align: right !important;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# URLs de la API
url_invoices = "http://app:8000/api/v1/invoices"
url_tratamientos = "http://app:8000/api/v1/tratamientos"

# Funciones de utilidad
def obtener_precios_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        respuesta.raise_for_status()
        tratamientos_data = respuesta.json()
        return {t["nombre"]: t["precio"] for t in tratamientos_data}
    except:
        st.error("Error de conexión: No se pudieron obtener los precios de los tratamientos")
        return {}

def obtener_facturas(filtrar_pagadas=None):
    try:
        params = {"paid": filtrar_pagadas} if filtrar_pagadas is not None else {}
        respuesta = requests.get(url_invoices, params=params)
        respuesta.raise_for_status()
        facturas = respuesta.json()
        
        precios_tratamientos = obtener_precios_tratamientos()
        
        for factura in facturas:
            if isinstance(factura["treatments"], str) and factura["treatments"]:
                tratamientos_lista = [t.strip() for t in factura["treatments"].split(",")]
                factura["total_price"] = sum(precios_tratamientos.get(t, 0) for t in tratamientos_lista)
        
        return facturas
    except:
        st.error("Error de conexión: No se pudo obtener la lista de facturas")
        return []

def marcar_pagada(invoice_id):
    try:
        respuesta = requests.put(f"{url_invoices}/{invoice_id}/pay")
        if respuesta.status_code == 200:
            st.success("Factura marcada como pagada exitosamente")
            st.rerun()
        else:
            st.error(f"Error en la actualización: {respuesta.text}")
    except Exception as e:
        st.error(f"Error de conexión con el servidor: {str(e)}")

def descargar_factura(invoice_id):
    try:
        download_url = f"{url_invoices}/{invoice_id}/download"
        response = requests.get(download_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error en la descarga: {e}")
        return None
        
def enviar_factura_correo(invoice_id, recipient_email):
    try:
        data = {"recipient_email": recipient_email}
        respuesta = requests.post(f"{url_invoices}/{invoice_id}/send-email", json=data)
        if respuesta.status_code == 200:
            st.success("Factura enviada exitosamente por correo")
            return True
        else:
            st.error(f"Error en el envío: {respuesta.text}")
            return False
    except Exception as e:
        st.error(f"Error de conexión con el servidor: {str(e)}")
        return False

st.title("Sistema de Facturación")

# Crear tabs para mejor organización
tab1, tab2 = st.tabs(["Facturas", "Gestión de Facturas"])

with tab1:
    st.header("Estado de Facturación")
    
    # Filtros
    col1, col2, col3 = st.columns([2,2,8])
    with col1:
        filtro = st.radio(
            "Filtrar por estado",
            options=["Todas", "Pagadas", "Pendientes"],
            horizontal=True
        )
    
    filtrar_pagadas = None if filtro == "Todas" else (filtro == "Pagadas")
    
    # Mostrar facturas
    facturas = obtener_facturas(filtrar_pagadas)
    if facturas:
        df = pd.DataFrame(facturas)
        df["Estado"] = df["paid"].apply(lambda x: 
            '<span class="status-paid">Pagada</span>' if x else 
            '<span class="status-pending">Pendiente</span>'
        )
        df["total_price"] = df["total_price"].apply(lambda x: f"{float(x):.2f} €")
        
        df = df.rename(columns={
            "id": "ID",
            "appointment_id": "ID Cita",
            "owner_id": "ID Propietario",
            "treatments": "Tratamientos",
            "total_price": "Total",
            "payment_method": "Método de Pago",
            "Estado": "Estado"
        })
        
        st.markdown('<div class="invoice-table">', unsafe_allow_html=True)
        st.write(
            df[["ID", "Tratamientos", "Total", "Método de Pago", "Estado"]].to_html(
                escape=False,
                index=False,
                classes=['table', 'table-striped']
            ),
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No hay facturas registradas en el sistema")

with tab2:
    st.header("Gestión de Facturas")
    
    # Formulario para recoger los datos
    col1, col2 = st.columns(2)
    with col1:
        id_factura = st.text_input("ID de la Factura")
    with col2:
        correo = st.text_input("Correo electrónico para envío")
    
    if id_factura:  # Solo mostrar botones si hay ID de factura
        st.markdown("### Acciones Disponibles")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Marcar como Pagada", type="primary", key="btn_pago"):
                marcar_pagada(id_factura)
        
        with col2:
            pdf_data = descargar_factura(id_factura)
            if pdf_data is not None:
                st.download_button(
                    label="Descargar PDF",
                    data=pdf_data,
                    file_name=f"factura_{id_factura}.pdf",
                    mime="application/pdf",
                    key="download_pdf"
                )
        
        with col3:
            if correo:
                if st.button("Enviar por Email", key="btn_email"):
                    enviar_factura_correo(id_factura, correo)
            else:
                st.warning("Ingrese un correo para enviar la factura")
    else:
        st.warning("Por favor, ingrese un ID de factura")