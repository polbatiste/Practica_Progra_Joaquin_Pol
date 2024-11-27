# streamli/pages/8_Facturas.py

import streamlit as st
import requests
import pandas as pd

# URLs de la API
url_invoices = "http://app:8000/api/v1/invoices"

def obtener_facturas(filtrar_pagadas=None):
    try:
        params = {"paid": filtrar_pagadas} if filtrar_pagadas is not None else {}
        respuesta = requests.get(url_invoices, params=params)
        respuesta.raise_for_status()
        return respuesta.json()
    except:
        st.error("No se pudo obtener la lista de facturas")
        return []

def marcar_pagada(invoice_id):
    try:
        respuesta = requests.put(f"{url_invoices}/{invoice_id}/pay")
        if respuesta.status_code == 200:
            st.success("Factura marcada como pagada")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error al marcar como pagada: {respuesta.text}")
    except:
        st.error("No se pudo conectar con el servidor")

def descargar_factura(invoice_id):
    try:
        respuesta = requests.get(f"{url_invoices}/{invoice_id}/download")
        if respuesta.status_code == 200:
            st.success(f"Factura descargada: {respuesta.json().get('message')}")
        else:
            st.error(f"Error al descargar la factura: {respuesta.text}")
    except:
        st.error("No se pudo conectar con el servidor")

def enviar_factura_correo(invoice_id, recipient_email):
    try:
        data = {"recipient_email": recipient_email}
        respuesta = requests.post(f"{url_invoices}/{invoice_id}/send-email", json=data)
        if respuesta.status_code == 200:
            st.success("Factura enviada por correo")
        else:
            st.error(f"Error al enviar la factura: {respuesta.text}")
    except:
        st.error("No se pudo conectar con el servidor")

# Título de la página
st.title("Gestión de Facturas")

# Filtrar facturas por estado
filtro = st.radio("Filtrar por estado de pago", options=["Todas", "Pagadas", "Pendientes"])
filtrar_pagadas = None if filtro == "Todas" else (filtro == "Pagadas")

# Obtener facturas
facturas = obtener_facturas(filtrar_pagadas)

# Mostrar facturas en tabla
if facturas:
    df = pd.DataFrame(facturas)
    df["Estado"] = df["paid"].apply(lambda x: "Pagada" if x else "Pendiente")
    df = df.rename(columns={
        "id": "ID",
        "appointment_id": "ID Cita",
        "owner_id": "ID Dueño",
        "treatments": "Tratamientos",
        "total_price": "Total",
        "payment_method": "Método de Pago",
        "Estado": "Estado"
    })
    st.table(df[["ID", "Tratamientos", "Total", "Método de Pago", "Estado"]])

    # Seleccionar factura para realizar acciones
    id_factura = st.text_input("ID de la Factura para gestionar")
    if id_factura:
        col1, col2, col3 = st.columns(3)

        # Botón para marcar como pagada
        with col1:
            if st.button("Marcar como Pagada"):
                marcar_pagada(id_factura)

        # Botón para descargar factura
        with col2:
            if st.button("Descargar Factura"):
                descargar_factura(id_factura)

        # Formulario para enviar factura por correo
        with col3:
            correo = st.text_input("Correo para enviar la factura")
            if st.button("Enviar por Correo"):
                if correo:
                    enviar_factura_correo(id_factura, correo)
                else:
                    st.error("Por favor, ingrese un correo válido")
else:
    st.info("No hay facturas disponibles")