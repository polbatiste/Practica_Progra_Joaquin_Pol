import streamlit as st
import requests
from datetime import datetime

# URL del microservicio FastAPI
url = "http://app:8000/citas/"

st.title("Alta de Citas para la Clínica Veterinaria 🐾")

# Crear el formulario para dar de alta una cita
with st.form("alta_cita"):
    nombre_animal = st.text_input("Nombre del animal")
    nombre_dueño = st.text_input("Nombre del dueño")
    tratamiento = st.text_area("Tratamiento a realizar")
    fecha_cita = st.date_input("Fecha de la cita", datetime.now())
    hora_cita = st.time_input("Hora de la cita", datetime.now().time())

    submit_button = st.form_submit_button(label="Registrar Cita")

if submit_button:
    # Validar que todos los campos requeridos estén llenos
    if not (nombre_animal and nombre_dueño and tratamiento):
        st.error("Por favor, complete todos los campos obligatorios.")
    else:
        fecha_hora_cita = datetime.combine(fecha_cita, hora_cita).isoformat()

        # Crear el payload para enviar al microservicio
        payload = {
            "nombre_animal": nombre_animal,
            "nombre_dueño": nombre_dueño,
            "tratamiento": tratamiento,
            "fecha_hora": fecha_hora_cita
        }

        # Enviar los datos al microservicio usando requests
        response = requests.post(url, json=payload)

        # Mostrar el resultado de la solicitud
        if response.status_code == 200:
            st.success("Cita registrada correctamente")
            st.json(response.json())
        else:
            st.error(f"Error al registrar la cita: {response.status_code}")
            st.text(response.text)