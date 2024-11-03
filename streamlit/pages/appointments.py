import streamlit as st
import requests
import pandas as pd

# Configuración del endpoint de la API
API_URL = "http://localhost:8000/api/v1/appointments"

# Función para obtener todas las citas
def get_appointments():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = pd.DataFrame(response.json())
        data["date"] = pd.to_datetime(data["date"]).dt.strftime('%d-%m-%Y')
        data["time"] = pd.to_datetime(data["time"]).dt.strftime('%H:%M')
        return data
    except requests.exceptions.RequestException:
        st.error("No se puede conectar con el servidor. Inténtelo más tarde.")
        return pd.DataFrame()

# Función para crear una nueva cita
def create_appointment(client_name, pet_name, date, time, reason):
    data = {
        "client_name": client_name,
        "pet_name": pet_name,
        "date": date,
        "time": time,
        "reason": reason
    }
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 201:
            st.success("Cita creada exitosamente")
        else:
            st.error("Error al crear la cita")
    except requests.exceptions.RequestException:
        st.error("No se puede conectar con el servidor para crear la cita.")

# Función para actualizar una cita
def update_appointment(appointment_id, client_name, pet_name, date, time, reason):
    data = {
        "client_name": client_name,
        "pet_name": pet_name,
        "date": date,
        "time": time,
        "reason": reason
    }
    try:
        response = requests.put(f"{API_URL}/{appointment_id}", json=data)
        if response.status_code == 200:
            st.success("Cita actualizada exitosamente")
        else:
            st.error("Error al actualizar la cita")
    except requests.exceptions.RequestException:
        st.error("No se puede conectar con el servidor para actualizar la cita.")

# Función para eliminar una cita
def delete_appointment(appointment_id):
    try:
        response = requests.delete(f"{API_URL}/{appointment_id}")
        if response.status_code == 204:
            st.success("Cita eliminada exitosamente")
        else:
            st.error("Error al eliminar la cita")
    except requests.exceptions.RequestException:
        st.error("No se puede conectar con el servidor para eliminar la cita.")

# Mostrar las citas existentes
st.subheader("Citas Existentes")
appointments_df = get_appointments()
if not appointments_df.empty:
    st.dataframe(appointments_df)

# Formulario para crear o actualizar citas
st.subheader("Crear o Actualizar Cita")
with st.form("appointment_form"):
    client_name = st.text_input("Nombre del Cliente")
    pet_name = st.text_input("Nombre de la Mascota")
    date = st.date_input("Fecha de la Cita")
    time = st.time_input("Hora de la Cita")
    reason = st.text_area("Motivo de la Cita")
    appointment_id = st.text_input("ID de Cita (solo para actualización)", "")

    submitted = st.form_submit_button("Enviar")
    if submitted:
        if not client_name or not pet_name or not date or not time or not reason:
            st.error("Por favor, complete todos los campos del formulario.")
        else:
            if appointment_id:
                update_appointment(appointment_id, client_name, pet_name, date, time, reason)
            else:
                create_appointment(client_name, pet_name, date, time, reason)

# Sección para eliminar una cita
st.subheader("Eliminar Cita")
delete_id = st.text_input("ID de la Cita a Eliminar", "")
if delete_id and st.button("Confirmar Eliminación"):
    delete_appointment(delete_id)
