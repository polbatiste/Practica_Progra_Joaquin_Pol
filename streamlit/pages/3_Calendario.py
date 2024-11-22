# streamli/pages/3_Calendario.py

import streamlit as st
from streamlit_calendar import calendar
import requests
import pandas as pd
from datetime import datetime, time

url_api = "http://app:8000/api/v1/appointments"
url_tratamientos = "http://app:8000/api/v1/tratamientos"  
url_owners = "http://app:8000/api/v1/owners"
url_animals = "http://app:8000/api/v1/animals"

st.title("Calendario para Citas Veterinarias 📆")

def obtener_dueños():
    try:
        respuesta = requests.get(url_owners)
        return respuesta.json() if respuesta.status_code == 200 else []
    except:
        st.error("Error al obtener dueños")
        return []

def obtener_animales():
    try:
        respuesta = requests.get(url_animals)
        return respuesta.json() if respuesta.status_code == 200 else []
    except:
        st.error("Error al obtener animales")
        return []

def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        return respuesta.json() if respuesta.status_code == 200 else []
    except:
        st.error("Error al obtener citas")
        return []

def obtener_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        return [t["nombre"] for t in respuesta.json()] if respuesta.status_code == 200 else []
    except:
        st.error("Error al obtener tratamientos")
        return []

def asignar_consulta(fecha, hora, citas):
    consultas_disponibles = ["1", "2", "3"]
    for consulta in consultas_disponibles:
        if not any(cita["date"] == fecha and cita["time"] == hora and cita["consultation"] == consulta for cita in citas):
            return consulta
    st.error("No hay consultas disponibles")
    return None

def crear_actualizar_cita(id_cita, owner_id, animal_id, fecha, hora, tratamiento, motivo, citas, es_actualizacion=False):
    consulta = asignar_consulta(fecha.strftime('%Y-%m-%d'), hora.strftime('%H:%M:%S'), citas)
    if not consulta:
        return

    datos_cita = {
        "id": id_cita if id_cita else None,
        "date": fecha.strftime('%Y-%m-%d'),
        "time": hora.strftime('%H:%M:%S'),
        "treatment": tratamiento,
        "reason": motivo,
        "consultation": consulta,
        "owner_id": owner_id,
        "animal_id": animal_id
    }

    try:
        if es_actualizacion:
            respuesta = requests.put(f"{url_api}/{id_cita}", json=datos_cita)
        else:
            respuesta = requests.post(url_api, json=datos_cita)

        if respuesta.status_code in [200, 201]:
            st.success(f"Cita gestionada en consulta {consulta}")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error: {respuesta.text}")
    except:
        st.error("Error de conexión")

# Cargar datos
citas = obtener_citas()
dueños = obtener_dueños()
animales = obtener_animales()
tratamientos = obtener_tratamientos()

# Control de estado para el dueño seleccionado
if 'previous_owner' not in st.session_state:
    st.session_state.previous_owner = None

# Colores para consultas
consulta_colores = {
    "1": "#FF6C6C",
    "2": "#6CFF6C",
    "3": "#6C6CFF"
}

# Preparar eventos
events = []
for cita in citas:
    dueño = next((d for d in dueños if d['id'] == cita['owner_id']), None)
    animal = next((a for a in animales if a['id'] == cita['animal_id']), None)
    if dueño and animal:
        events.append({
            "title": f"{dueño['nombre']} - {animal['name']} ({cita['treatment']})",
            "start": f"{cita['date']}T{cita['time']}",
            "end": f"{cita['date']}T{cita['time']}",
            "id": cita['id'],
            "color": consulta_colores.get(cita['consultation'], "#CCCCCC")
        })

# Configuración calendario
calendar_options = {
    "editable": "true",
    "selectable": "true",
    "initialDate": datetime.today().strftime('%Y-%m-%d'),
    "initialView": "timeGridWeek",
    "slotMinTime": "09:00:00",
    "slotMaxTime": "21:00:00", 
    "hiddenDays": [0],
    "businessHours": [{"daysOfWeek": [1, 2, 3, 4, 5, 6], "startTime": "09:00", "endTime": "21:00"}]
}

state = calendar(
    events=st.session_state.get("events", events),
    options=calendar_options,
    custom_css="""
    .fc-event-past { opacity: 0.8; }
    .fc-event-title { font-weight: 700; }
    .fc-toolbar-title { font-size: 1.5rem; }
    """,
    key='calendario'
)

# Leyenda
st.sidebar.subheader("Leyenda de Consultas")
for consulta, color in consulta_colores.items():
    st.sidebar.markdown(f"<div style='background-color: {color}; padding: 5px;'>Consulta {consulta}</div>", unsafe_allow_html=True)

# Popup nueva cita
@st.dialog("Nueva Cita")
def popup():
    st.write(f'Fecha: {st.session_state["time_inicial"]}')
    with st.form("formulario_cita"):
        # Selector de dueño fuera del formulario
        dueño_options = {f"{d['nombre']} (DNI: {d['dni']})": d['id'] for d in dueños}
        selected_dueño = st.selectbox("Dueño", options=list(dueño_options.keys()))
        owner_id = dueño_options[selected_dueño] if selected_dueño else None

        # Forzar recarga si cambia el dueño
        if owner_id != st.session_state.previous_owner:
            st.session_state.previous_owner = owner_id
            st.rerun()

        # Selector de animal filtrado
        animal_id = None
        if owner_id:
            animales_dueño = [a for a in animales if a['owner_id'] == owner_id]
            if animales_dueño:
                animal_options = {a['name']: a['id'] for a in animales_dueño}
                selected_animal = st.selectbox(
                    "Mascota", 
                    options=list(animal_options.keys()),
                    key=f"animal_select_{owner_id}"
                )
                animal_id = animal_options[selected_animal] if selected_animal else None
            else:
                st.warning("Este dueño no tiene mascotas registradas")

        tratamiento = st.selectbox("Tratamiento", tratamientos, key="tratamiento_select")
        motivo = st.text_area("Motivo", key="motivo_input")

        if st.form_submit_button("Enviar") and all([owner_id, animal_id, tratamiento, motivo]):
            fecha, hora = st.session_state["time_inicial"].split('T')
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
            hora_dt = datetime.strptime(hora[:5], '%H:%M').time()
            if fecha_dt.weekday() == 6:
                st.error("No se aceptan citas en domingo")
            else:
                crear_actualizar_cita(None, owner_id, animal_id, fecha_dt, hora_dt, tratamiento, motivo, citas)

if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    popup()

# Actualizar cita
if state.get('eventChange') is not None:
    event_data = state.get('eventChange').get('event')
    id_evento = event_data['id']
    fecha_nueva, hora_nueva = event_data['start'].split('T')
    cita_original = next((c for c in citas if c['id'] == id_evento), None)
    if cita_original:
        fecha_dt = datetime.strptime(fecha_nueva, '%Y-%m-%d')
        hora_dt = datetime.strptime(hora_nueva[:5], '%H:%M').time()
        crear_actualizar_cita(
            id_evento, 
            cita_original['owner_id'],
            cita_original['animal_id'],
            fecha_dt,
            hora_dt,
            cita_original['treatment'],
            cita_original['reason'],
            citas,
            True
        )

# Eliminar cita
if state.get('eventClick') is not None:
    id_evento = state['eventClick']['event']['id']
    if st.button(f"Eliminar cita ID {id_evento}"):
        try:
            respuesta = requests.delete(f"{url_api}/{id_evento}")
            if respuesta.status_code == 204:
                st.success("Cita eliminada")
                st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
            else:
                st.error("Error al eliminar")
        except:
            st.error("Error de conexión")