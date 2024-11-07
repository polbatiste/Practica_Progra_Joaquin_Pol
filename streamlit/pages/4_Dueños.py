import streamlit as st
import requests

API_BASE_URL = "http://app:8000/api/v1/owners"

st.title("Alta de Dueños - Clínica Veterinaria")

with st.form("owner_form"):
    nombre = st.text_input("Nombre")
    dni = st.text_input("DNI")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    correo_electronico = st.text_input("Correo Electrónico")
    submit_button = st.form_submit_button("Registrar")

    if submit_button:
        response = requests.post(API_BASE_URL, json={
            "nombre": nombre,
            "dni": dni,
            "direccion": direccion,
            "telefono": telefono,
            "correo_electronico": correo_electronico
        })
        if response.status_code == 201:
            st.success("Dueño registrado exitosamente")
        else:
            st.error("Error al registrar dueño")