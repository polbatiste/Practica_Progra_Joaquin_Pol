import streamlit as st
from streamlit_calendar import calendar
import requests

# URL de la API para las citas
backend = "http://app:8000/api/v1/appointments"

# Inicializar el estado de la sesión si no existe
if "events" not in st.session_state:
    st.session_state["events"] = []

st.title("Calendario Interactivo de Citas para la Clínica Veterinaria 📆")

# Función para enviar datos al backend
def send(data, method="POST"):
    if method == "POST":
        response = requests.post(backend, json=data)
    elif method == "PUT":
        response = requests.put(f"{backend}/{data['id']}", json=data)
    elif method == "DELETE":
        response = requests.delete(f"{backend}/{data['id']}")
    return response

# Popup para agregar o modificar citas
@st.dialog("Ingrese la información de la cita")
def popup():
    fecha_inicio = st.session_state.get("time_inicial")
    fecha_fin = st.session_state.get("time_final")
    st.write(f'Fecha de la cita: {fecha_inicio} - {fecha_fin}')
    
    with st.form("formulario_cita"):
        nombre_animal = st.text_input("Nombre del animal:")
        nombre_dueño = st.text_input("Nombre del dueño:")
        tratamiento = st.text_input("Tratamiento a realizar:")
        submitted = st.form_submit_button("Enviar")

    if submitted:
        if not (nombre_animal and nombre_dueño and tratamiento):
            st.error("Por favor, complete todos los campos obligatorios.")
        else:
            data = {
                "client_name": nombre_dueño,
                "pet_name": nombre_animal,
                "date": fecha_inicio.split('T')[0],  # Fecha en formato ISO
                "time": fecha_inicio.split('T')[1],  # Hora en formato ISO
                "treatment": tratamiento,
                "reason": "Consulta",
                "consultation": "a"
            }
            response = send(data)
            if response.status_code in [200, 201]:
                st.success("Cita registrada con éxito, puede cerrar!")
                # Actualizar la lista de eventos en la sesión
                st.session_state["events"].append({
                    "title": nombre_animal,
                    "start": fecha_inicio,
                    "end": fecha_fin,
                    "resourceId": "a"  # Ajusta esto según tu lógica
                })
                st.experimental_rerun()  # Actualiza la página para reflejar los cambios
            else:
                st.error(f"Error al registrar la cita: {response.status_code}")

# Configuración del calendario
events = st.session_state.get("events", [])
calendar_resources = [
    {"id": "a", "building": "Clínica Principal", "title": "Sala 1"},
    {"id": "b", "building": "Clínica Principal", "title": "Sala 2"},
]

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "resources": calendar_resources,
    "selectable": "true",
    "initialDate": "2023-07-01",
    "initialView": "resourceTimeGridDay",
    "resourceGroupField": "building",
}

state = calendar(
    events=events,
    options=calendar_options,
    custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
    """,
    key='timegrid',
)

# Sincronizar el estado del calendario con la aplicación
if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]

# Manejar la selección para agregar una nueva cita
if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    st.session_state["time_final"] = state["select"]["end"]
    popup()

# Manejar el cambio de eventos para modificar citas
if state.get('eventChange') is not None:
    event = state.get('eventChange').get('event')
    data = {
        "id": event.get("id"),
        "start": event.get("start"),
        "end": event.get("end")
    }
    response = send(data, method="PUT")
    if response.status_code in [200, 201]:
        st.success('Cita modificada con éxito')
    else:
        st.error(f'Error al modificar la cita: {response.status_code}')

# Manejar la eliminación de eventos al hacer clic
if state.get('eventClick') is not None:
    event_id = state.get('eventClick').get('event').get('id')
    response = send({"id": event_id}, method="DELETE")
    if response.status_code in [200, 204]:
        st.success("Cita cancelada con éxito")
    else:
        st.error(f"Error al cancelar la cita: {response.status_code}")