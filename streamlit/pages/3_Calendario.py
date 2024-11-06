import streamlit as st
from streamlit_calendar import calendar
import requests
import pandas as pd
from datetime import datetime, time, timedelta

# URL de la API de citas
url_api = "http://app:8000/api/v1/appointments"

st.title("Calendario para Citas Veterinarias 📆")

# Función para obtener todas las citas existentes de la API
def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        respuesta.raise_for_status()
        return respuesta.json()  # Devuelve una lista de citas en formato JSON
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con el servidor para obtener las citas.")
        return []

# Función para asignar automáticamente una consulta a la cita
def asignar_consulta(fecha, hora, citas):
    consultas_disponibles = ["1", "2", "3"]  # Consultas disponibles
    for consulta in consultas_disponibles:
        if not any(cita["date"] == fecha and cita["time"] == hora and cita["consultation"] == consulta for cita in citas):
            return consulta  # Devuelve la consulta disponible
    st.error("No hay consultas disponibles para la fecha y hora seleccionadas.")
    return None  # Devuelve None si no hay consultas disponibles

# Función para crear o actualizar una cita en la API
def crear_actualizar_cita(id_cita, nombre_cliente, nombre_mascota, fecha, hora, tratamiento, motivo, citas, es_actualizacion=False):
    fecha_formateada = fecha.strftime('%Y-%m-%d')
    hora_formateada = hora.strftime('%H:%M:%S')
    consulta = asignar_consulta(fecha_formateada, hora_formateada, citas)
    if not consulta:
        return  # Salir si no hay consulta disponible

    # Crear el cuerpo de la solicitud con los datos de la cita
    datos_cita = {
        "id": id_cita if id_cita else None,
        "client_name": nombre_cliente,
        "pet_name": nombre_mascota,
        "date": fecha_formateada,
        "time": hora_formateada,
        "treatment": tratamiento,
        "reason": motivo,
        "consultation": consulta
    }

    try:
        if es_actualizacion and id_cita:
            respuesta = requests.put(f"{url_api}/{id_cita}", json=datos_cita)
        else:
            respuesta = requests.post(url_api, json=datos_cita)

        if respuesta.status_code in [200, 201]:
            st.success(f"Cita gestionada exitosamente en la consulta {consulta}")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error al gestionar la cita: {respuesta.text}")
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con el servidor para gestionar la cita.")

# Función para enviar datos a la API
def send(data, method="POST", appointment_id=None):
    try:
        if method == "POST":
            response = requests.post(url_api, json=data)
        elif method == "PUT" and appointment_id:
            response = requests.put(f"{url_api}/{appointment_id}", json=data)
        elif method == "DELETE" and appointment_id:
            response = requests.delete(f"{url_api}/{appointment_id}")
        
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, str(e)

# Cargar citas existentes
citas = obtener_citas()
consulta_colores = {
    "1": "#FF6C6C",
    "2": "#6CFF6C",
    "3": "#6C6CFF"
}

# Preparar eventos para el calendario
events = [
    {
        "title": f"{cita['client_name']} - {cita['treatment']}",
        "start": f"{cita['date']}T{cita['time']}",
        "end": f"{cita['date']}T{cita['time']}",
        "id": cita['id'],
        "color": consulta_colores.get(cita['consultation'], "#CCCCCC")
    }
    for cita in citas
]

# Configuración de la vista del calendario
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "selectable": "true",
    "initialDate": "2024-11-05",
    "initialView": "timeGridWeek",
    "slotMinTime": "09:00:00",
    "slotMaxTime": "21:00:00",
    "hiddenDays": [0],
    "weekends": True,
    "businessHours": [
        {
            "daysOfWeek": [1, 2, 3, 4, 5, 6],
            "startTime": "09:00",
            "endTime": "21:00"
        }
    ]
}

# Mostrar el calendario interactivo
state = calendar(
    events=st.session_state.get("events", events),
    options=calendar_options,
    custom_css="""
    .fc-event-past { opacity: 0.8; }
    .fc-event-title { font-weight: 700; }
    .fc-toolbar-title { font-size: 1.5rem; }
    """,
    key='calendario',
)

# Leyenda visual para las consultas
st.sidebar.subheader("Leyenda de Consultas")
st.sidebar.markdown(f"<div style='background-color: #FF6C6C; padding: 5px;'>Consulta 1</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color: #6CFF6C; padding: 5px;'>Consulta 2</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color: #6C6CFF; padding: 5px;'>Consulta 3</div>", unsafe_allow_html=True)

# Función emergente para crear una nueva cita
@st.dialog("Información de la cita")
def popup():
    st.write(f'Fecha de la cita: {st.session_state["time_inicial"]}')
    with st.form("formulario_cita"):
        nombre_cliente = st.text_input("Nombre del cliente")
        nombre_mascota = st.text_input("Nombre de la mascota")
        tratamiento = st.text_input("Tratamiento")
        motivo = st.text_area("Motivo")

        enviado = st.form_submit_button("Enviar")
        if enviado:
            if nombre_cliente and nombre_mascota and tratamiento and motivo:
                fecha = st.session_state["time_inicial"].split('T')[0]
                hora = st.session_state["time_inicial"].split('T')[1][:5]
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                hora_dt = datetime.strptime(hora, '%H:%M').time()

                if fecha_dt.weekday() == 6:
                    st.error("No se pueden programar citas los domingos. Por favor, elija otra fecha.")
                else:
                    crear_actualizar_cita(None, nombre_cliente, nombre_mascota, fecha_dt, hora_dt, tratamiento, motivo, citas)

# Acciones para seleccionar y mostrar el popup de cita
if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    popup()

# Actualización de cita si cambia la fecha
if state.get('eventChange') is not None:
    event_data = state.get('eventChange').get('event')
    id_evento = event_data['id']
    fecha_nueva = event_data['start'].split('T')[0]
    hora_nueva = event_data['start'].split('T')[1][:5]

    cita_original = next((cita for cita in citas if cita['id'] == id_evento), None)
    if cita_original:
        fecha_dt = datetime.strptime(fecha_nueva, '%Y-%m-%d')
        hora_dt = datetime.strptime(hora_nueva, '%H:%M').time()
        crear_actualizar_cita(id_evento, cita_original['client_name'], cita_original['pet_name'], fecha_dt, hora_dt, cita_original['treatment'], cita_original['reason'], citas, es_actualizacion=True)

# Eliminación de cita si se selecciona en el calendario
if state.get('eventClick') is not None:
    id_evento = state['eventClick']['event']['id']
    if st.button(f"Eliminar cita ID {id_evento}"):
        status, _ = send(None, method="DELETE", appointment_id=id_evento)
        if status == 204:
            st.success("Cita eliminada exitosamente")
            st.write('<script>setTimeout(function(){ window.location.reload(); }, 1000);</script>', unsafe_allow_html=True)
        else:
            st.error("Error al eliminar la cita.")