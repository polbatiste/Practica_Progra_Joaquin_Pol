import streamlit as st
from streamlit_calendar import calendar
import requests

# URL de la API de citas
url_api = "http://app:8000/api/v1/appointments"

st.title("Calendario para Citas Veterinarias 📆")

# Función para enviar datos a la API
def send(data, method="POST", appointment_id=None):
    try:
        if method == "POST":
            response = requests.post(url_api, json=data)
        elif method == "PUT" and appointment_id:
            response = requests.put(f"{url_api}/{appointment_id}", json=data)
        elif method == "DELETE" and appointment_id:
            response = requests.delete(f"{url_api}/{appointment_id}")
        
        return response.status_code
    except requests.exceptions.RequestException:
        return None

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
                datos = {
                    "client_name": nombre_cliente,
                    "pet_name": nombre_mascota,
                    "date": st.session_state["time_inicial"].split('T')[0],
                    "time": st.session_state["time_inicial"].split('T')[1][:5],
                    "treatment": tratamiento,
                    "reason": motivo,
                    "consultation": asignar_consulta()  # Llamar a la función de asignación automática de consulta
                }
                envio = send(datos)
                if envio == 201:
                    st.success("Cita creada exitosamente")
                    st.write('<script>setTimeout(function(){ window.location.reload(); }, 1000);</script>', unsafe_allow_html=True)
                else:
                    st.error("Error al crear la cita. Por favor, inténtelo de nuevo.")

# Función para asignar automáticamente una consulta
def asignar_consulta():
    consultas_disponibles = ["1", "2", "3"]
    return consultas_disponibles[hash(st.session_state["time_inicial"]) % 3]  # Asignación simple y automática

# Cargar citas existentes
def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con el servidor para obtener las citas.")
        return []

# Preparar eventos para el calendario
citas = obtener_citas()
consulta_colores = {
    "1": "#FF6C6C",  # Rojo para Consulta 1
    "2": "#6CFF6C",  # Verde para Consulta 2
    "3": "#6C6CFF"   # Azul para Consulta 3
}

events = [
    {
        "title": f"{cita['client_name']} - {cita['treatment']}",
        "start": f"{cita['date']}T{cita['time']}",
        "end": f"{cita['date']}T{cita['time']}",
        "id": cita['id'],
        "color": consulta_colores.get(cita['consultation'], "#CCCCCC")  # Color basado en la consulta
    }
    for cita in citas
]

# Cambiar la vista del calendario a 'timeGridWeek' para mostrar semanas de lunes a domingo
calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "selectable": "true",
    "initialDate": "2024-11-05",  # Fecha inicial ajustada a la fecha actual
    "initialView": "timeGridWeek",  # Vista de semana completa
    "slotMinTime": "09:00:00",  # Hora de inicio
    "slotMaxTime": "21:00:00",  # Hora de fin
    "hiddenDays": [0],  # Ocultar domingos (día 0)
    "weekends": True,  # Mostrar fines de semana
    "businessHours": [
        {
            "daysOfWeek": [1, 2, 3, 4, 5, 6],  # Lunes a sábado
            "startTime": "09:00",
            "endTime": "21:00"
        }
    ]
}

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

# Mostrar leyenda visual
st.sidebar.subheader("Leyenda de Consultas")
st.sidebar.markdown(f"<div style='background-color: #FF6C6C; padding: 5px;'>Consulta 1</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color: #6CFF6C; padding: 5px;'>Consulta 2</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color: #6C6CFF; padding: 5px;'>Consulta 3</div>", unsafe_allow_html=True)

# Acciones basadas en la interacción con el calendario
if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]

if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    st.session_state["time_final"] = state["select"]["end"]
    popup()

if state.get('eventChange') is not None:
    event_data = state.get('eventChange').get('event')
    id_evento = event_data['id']
    fecha_nueva = event_data['start'].split('T')[0]
    hora_nueva = event_data['start'].split('T')[1][:5]

    # Recuperar la cita original para obtener los campos restantes
    cita_original = next((cita for cita in citas if cita['id'] == id_evento), None)
    if cita_original:
        datos_actualizados = {
            "id": id_evento,
            "client_name": cita_original['client_name'],  # Mantener el nombre del cliente
            "pet_name": cita_original['pet_name'],        # Mantener el nombre de la mascota
            "date": fecha_nueva,
            "time": hora_nueva,
            "treatment": cita_original['treatment'],      # Mantener el tratamiento
            "reason": cita_original['reason'],            # Mantener el motivo
            "consultation": event_data.get('resourceId', cita_original['consultation'])
        }

        status = send(datos_actualizados, method="PUT", appointment_id=id_evento)
        if status == 200:
            st.success("Cita actualizada con éxito")
            st.write('<script>setTimeout(function(){ window.location.reload(); }, 1000);</script>', unsafe_allow_html=True)
        else:
            st.error("Error al actualizar la cita.")
            st.write(f"Detalles del error: {status}")

if state.get('eventClick') is not None:
    id_evento = state['eventClick']['event']['id']
    if st.button(f"Eliminar cita ID {id_evento}"):
        status = send(None, method="DELETE", appointment_id=id_evento)
        if status == 204:
            st.success("Cita eliminada exitosamente")
            st.write('<script>setTimeout(function(){ window.location.reload(); }, 1000);</script>', unsafe_allow_html=True)
        else:
            st.error("Error al eliminar la cita.")