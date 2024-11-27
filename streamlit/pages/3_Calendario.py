import streamlit as st
from streamlit_calendar import calendar
import requests
import pandas as pd
from datetime import datetime, time

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Calendario",
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
        margin-bottom: 2rem;
    }
    h2 {
        color: #34495e;
        margin-top: 2rem;
        font-size: 1.5rem;
    }
    .calendar-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .consultation-legend {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        color: white;
        font-weight: 500;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# URLs de la API
url_api = "http://app:8000/api/v1/appointments"
url_tratamientos = "http://app:8000/api/v1/tratamientos"  
url_owners = "http://app:8000/api/v1/owners"
url_animals = "http://app:8000/api/v1/animals"

st.title("Sistema de Agenda Médica")

# Funciones de utilidad
def obtener_dueños():
    try:
        respuesta = requests.get(url_owners)
        return respuesta.json() if respuesta.status_code == 200 else []
    except:
        st.error("Error de conexión: No se pudieron obtener los datos de propietarios")
        return []

def obtener_animales():
    try:
        respuesta = requests.get(url_animals)
        return respuesta.json() if respuesta.status_code == 200 else []
    except:
        st.error("Error de conexión: No se pudieron obtener los datos de pacientes")
        return []

def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        return respuesta.json() if respuesta.status_code == 200 else []
    except:
        st.error("Error de conexión: No se pudieron obtener las citas programadas")
        return []

def obtener_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        return [t["nombre"] for t in respuesta.json()] if respuesta.status_code == 200 else []
    except:
        st.error("Error de conexión: No se pudieron obtener los tratamientos disponibles")
        return []

def asignar_consulta(fecha, hora, citas, cita_actual_id=None):
    # Filtrar las citas para esa fecha y hora, excluyendo la cita actual si existe
    citas_hora = [
        c for c in citas 
        if c["date"] == fecha and 
        c["time"] == hora and 
        str(c["id"]) != str(cita_actual_id)
    ]
    
    # Ver qué consultas están ocupadas
    consultas_ocupadas = {c["consultation"] for c in citas_hora}
    
    # Buscar primera consulta disponible
    for consulta in ["1", "2", "3"]:
        if consulta not in consultas_ocupadas:
            return consulta
            
    return None

def crear_actualizar_cita(id_cita, owner_id, animal_id, fecha, hora, tratamiento, motivo, citas, es_actualizacion=False):
    fecha_str = fecha.strftime('%Y-%m-%d')
    hora_str = hora.strftime('%H:%M:%S')
    
    # Verificar disponibilidad de consulta
    consulta = asignar_consulta(fecha_str, hora_str, citas, id_cita)
    if not consulta:
        st.error("No hay consultorios disponibles para el horario seleccionado")
        return False

    datos_cita = {
        "id": id_cita if id_cita else None,
        "date": fecha_str,
        "time": hora_str,
        "treatment": tratamiento,
        "reason": motivo,
        "consultation": consulta,
        "owner_id": owner_id,
        "animal_id": animal_id
    }

    try:
        if es_actualizacion and id_cita:
            respuesta = requests.put(f"{url_api}/{id_cita}", json=datos_cita)
        else:
            respuesta = requests.post(url_api, json=datos_cita)

        if respuesta.status_code in [200, 201]:
            st.success(f"Cita registrada exitosamente en consultorio {consulta}")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
            return True
        else:
            st.error(f"Error en el registro: {respuesta.text}")
            return False
    except:
        st.error("Error de conexión con el servidor")
        return False

# Cargar datos necesarios
citas = obtener_citas()
dueños = obtener_dueños()
animales = obtener_animales()
tratamientos = obtener_tratamientos()

# Control de estado
if 'previous_owner' not in st.session_state:
    st.session_state.previous_owner = None

# Configuración de colores para consultorios
consulta_colores = {
    "1": "#3498db",  # Azul profesional
    "2": "#2ecc71",  # Verde suave
    "3": "#9b59b6"   # Púrpura suave
}

# Preparar eventos para el calendario
events = []
for cita in citas:
    dueño = next((d for d in dueños if d['id'] == cita['owner_id']), None)
    animal = next((a for a in animales if a['id'] == cita['animal_id']), None)
    if dueño and animal:
        events.append({
            "title": f"{dueño['nombre']} - {animal['name']}\n{cita['treatment']}",
            "start": f"{cita['date']}T{cita['time']}",
            "end": f"{cita['date']}T{cita['time']}",
            "id": cita['id'],
            "color": consulta_colores.get(cita['consultation'], "#95a5a6")
        })

# Configuración del calendario
calendar_options = {
    "editable": True,
    "selectable": True,
    "initialDate": datetime.today().strftime('%Y-%m-%d'),
    "initialView": "timeGridWeek",
    "slotMinTime": "09:00:00",
    "slotMaxTime": "21:00:00", 
    "hiddenDays": [0],
    "businessHours": [{"daysOfWeek": [1, 2, 3, 4, 5, 6], "startTime": "09:00", "endTime": "21:00"}],
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "timeGridWeek,timeGridDay"
    },
    "eventDrop": True,
    "eventResize": True,
    "slotDuration": "00:30:00"
}

# Sidebar con leyenda
st.sidebar.title("Información")
st.sidebar.header("Consultorios Disponibles")
for consulta, color in consulta_colores.items():
    st.sidebar.markdown(
        f"""<div style='background-color: {color}; padding: 10px; border-radius: 4px; color: white; margin: 5px 0;'>
            Consultorio {consulta}</div>""", 
        unsafe_allow_html=True
    )

# Renderizar calendario
st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
state = calendar(
    events=st.session_state.get("events", events),
    options=calendar_options,
    custom_css="""
    .fc-event {
        border: none;
        padding: 2px;
        font-size: 0.85em;
    }
    .fc-event-title {
        font-weight: 500;
        padding: 2px;
    }
    .fc-toolbar-title {
        font-size: 1.2rem !important;
        color: #2c3e50;
    }
    .fc-button {
        background-color: #2c3e50 !important;
        border: none !important;
    }
    .fc-button:hover {
        background-color: #34495e !important;
    }
    .fc-today-button {
        background-color: #16a085 !important;
    }
    """,
    key='calendario'
)
st.markdown('</div>', unsafe_allow_html=True)

# Diálogo de nueva cita
@st.dialog("Registro de Nueva Cita")
def popup():
    if 'previous_owner' not in st.session_state:
        st.session_state.previous_owner = None
        
    st.write(f'Fecha seleccionada: {st.session_state["time_inicial"]}')
    
    dueño_options = {f"{d['nombre']} (DNI: {d['dni']})": d['id'] for d in dueños}
    selected_dueño = st.selectbox("Seleccionar Propietario", options=list(dueño_options.keys()))
    owner_id = dueño_options[selected_dueño] if selected_dueño else None

    if owner_id != st.session_state.previous_owner:
        st.session_state.previous_owner = owner_id
        st.rerun()

    with st.form("formulario_cita", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            animal_id = None
            if owner_id:
                animales_dueño = [a for a in animales if a['owner_id'] == owner_id]
                if animales_dueño:
                    animal_options = {a['name']: a['id'] for a in animales_dueño}
                    selected_animal = st.selectbox(
                        "Seleccionar Paciente", 
                        options=list(animal_options.keys()),
                        key=f"animal_select_{owner_id}"
                    )
                    animal_id = animal_options[selected_animal] if selected_animal else None
                else:
                    st.warning("El propietario no tiene pacientes registrados")
        
        with col2:
            tratamiento = st.selectbox("Tipo de Tratamiento", tratamientos, key="tratamiento_select")
            
        motivo = st.text_area("Motivo de la Consulta", key="motivo_input")

        if st.form_submit_button("Registrar Cita"):
            if all([owner_id, animal_id, tratamiento, motivo]):
                fecha, hora = st.session_state["time_inicial"].split('T')
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                hora_dt = datetime.strptime(hora[:5], '%H:%M').time()
                if fecha_dt.weekday() == 6:
                    st.error("No se realizan atenciones los días domingo")
                else:
                    crear_actualizar_cita(None, owner_id, animal_id, fecha_dt, hora_dt, tratamiento, motivo, citas)
            else:
                st.error("Todos los campos son obligatorios")

# Manejar eventos del calendario
if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    popup()

# Manejar cambios en eventos (arrastrar y soltar)
if state.get('eventChange') is not None:
    event_data = state.get('eventChange')
    id_evento = event_data['event']['id']
    fecha_nueva, hora_nueva = event_data['event']['start'].split('T')
    cita_original = next((c for c in citas if str(c['id']) == str(id_evento)), None)
    
    if cita_original:
        fecha_dt = datetime.strptime(fecha_nueva, '%Y-%m-%d')
        hora_dt = datetime.strptime(hora_nueva[:5], '%H:%M').time()
        
        # Verificar que no sea domingo
        if fecha_dt.weekday() == 6:
            st.error("No se pueden programar citas los domingos")
            st.rerun()
        else:
            # Intentar actualizar la cita
            exito = crear_actualizar_cita(
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
            if not exito:
                st.rerun()  # Recargar si falla para volver al estado anterior

# Manejar clic en eventos
if state.get('eventClick') is not None:
    event_data = state['eventClick']['event']
    id_evento = event_data['id']
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Gestionar Cita Seleccionada")
    if st.sidebar.button("Cancelar Esta Cita"):
        try:
            respuesta = requests.delete(f"{url_api}/{id_evento}")
            if respuesta.status_code == 204:
                st.sidebar.success("Cita cancelada exitosamente")
                st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
            else:
                st.sidebar.error("Error al cancelar la cita")
        except:
            st.sidebar.error