import streamlit as st
import requests
import pandas as pd
import os

# URLs de la API
url_invoices = "http://app:8000/api/v1/invoices"
url_tratamientos = "http://app:8000/api/v1/tratamientos"

def obtener_precios_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        respuesta.raise_for_status()
        tratamientos_data = respuesta.json()
        return {t["nombre"]: t["precio"] for t in tratamientos_data}
    except:
        st.error("No se pudo obtener los precios de los tratamientos")
        return {}

def obtener_facturas(filtrar_pagadas=None):
    try:
        params = {"paid": filtrar_pagadas} if filtrar_pagadas is not None else {}
        respuesta = requests.get(url_invoices, params=params)
        respuesta.raise_for_status()
        facturas = respuesta.json()
        
        # Obtener precios de tratamientos
        precios_tratamientos = obtener_precios_tratamientos()
        
        # Actualizar precios basados en los tratamientos
        for factura in facturas:
            if isinstance(factura["treatments"], str) and factura["treatments"]:
                tratamientos_lista = [t.strip() for t in factura["treatments"].split(",")]
                factura["total_price"] = sum(precios_tratamientos.get(t, 0) for t in tratamientos_lista)
        
        return facturas
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
        download_url = f"{url_invoices}/{invoice_id}/download"
        response = requests.get(download_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error al descargar la factura: {e}")
        return None
        
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
    # Formatear el precio total con 2 decimales y añadir el símbolo €
    df["total_price"] = df["total_price"].apply(lambda x: f"{float(x):.2f} €")
    
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
            pdf_data = descargar_factura(id_factura)
            if pdf_data is not None:
                st.download_button(
                    label="Descargar Factura",
                    data=pdf_data,
                    file_name=f"factura_{id_factura}.pdf",
                    mime="application/pdf"
                )

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