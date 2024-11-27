import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, time

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Citas",
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
    }
    h2 {
        color: #34495e;
        margin-top: 2rem;
    }
    .table-container {
        margin: 2rem 0;
        border-radius: 4px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .success {
        padding: 1rem;
        border-radius: 4px;
        background-color: #d4edda;
        color: #155724;
    }
    .error {
        padding: 1rem;
        border-radius: 4px;
        background-color: #f8d7da;
        color: #721c24;
    }
    .warning {
        padding: 1rem;
        border-radius: 4px;
        background-color: #fff3cd;
        color: #856404;
    }
    .info {
        padding: 1rem;
        border-radius: 4px;
        background-color: #e2e3e5;
        color: #383d41;
    }
    </style>
""", unsafe_allow_html=True)

# URLs de la API
url_api = "http://app:8000/api/v1/appointments"
url_tratamientos = "http://app:8000/api/v1/tratamientos"
url_owners = "http://app:8000/api/v1/owners"
url_animals = "http://app:8000/api/v1/animals"

# Funciones auxiliares
def obtener_dueños():
    try:
        respuesta = requests.get(url_owners)
        respuesta.raise_for_status()
        return respuesta.json()
    except:
        st.error("Error en la conexión: No se pudo obtener la lista de propietarios")
        return []

def obtener_animales():
    try:
        respuesta = requests.get(url_animals)
        respuesta.raise_for_status()
        return respuesta.json()
    except:
        st.error("Error en la conexión: No se pudo obtener la lista de pacientes")
        return []

def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        respuesta.raise_for_status()
        citas = respuesta.json()
        return [cita for cita in citas if not cita.get("completed", False)]
    except:
        st.error("Error en la conexión: No se pudo obtener la lista de citas")
        return []

def obtener_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        respuesta.raise_for_status()
        return [tratamiento["nombre"] for tratamiento in respuesta.json()]
    except:
        st.error("Error en la conexión: No se pudo obtener la lista de tratamientos")
        return []

def obtener_precios_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        respuesta.raise_for_status()
        tratamientos_data = respuesta.json()
        return {t["nombre"]: t["precio"] for t in tratamientos_data}
    except:
        st.error("Error en la conexión: No se pudo obtener los precios de los tratamientos")
        return {}

def generar_horas_inicio():
    horas = []
    hora_actual = time(9, 0)
    fin = time(20, 0)
    while hora_actual <= fin:
        horas.append(hora_actual)
        hora_actual = (datetime.combine(datetime.today(), hora_actual) + timedelta(minutes=30)).time()
    return horas

def asignar_consulta(fecha, hora, citas):
    consultas_disponibles = ["1", "2", "3"]
    for consulta in consultas_disponibles:
        if not any(cita["date"] == fecha and cita["time"] == hora and cita["consultation"] == consulta for cita in citas):
            return consulta
    st.error("No hay consultas disponibles para el horario seleccionado")
    return None

def crear_actualizar_cita(id_cita, owner_id, animal_id, fecha, hora, tratamiento, motivo, citas, es_actualizacion=False):
    fecha_formateada = fecha.strftime('%Y-%m-%d')
    hora_formateada = hora.strftime('%H:%M:%S')
    consulta = asignar_consulta(fecha_formateada, hora_formateada, citas)
    if not consulta:
        return

    datos_cita = {
        "id": id_cita if id_cita else None,
        "date": fecha_formateada,
        "time": hora_formateada,
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
            st.success(f"Cita registrada exitosamente en consulta {consulta}")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error en el registro: {respuesta.text}")
    except:
        st.error("Error en la conexión con el servidor")

# Título principal
st.title("Sistema de Gestión de Citas")

# Obtener datos necesarios
citas = obtener_citas()
dueños = obtener_dueños()
animales = obtener_animales()
tratamientos = obtener_tratamientos()
opciones_de_horas = generar_horas_inicio()

# Sección de citas programadas
st.header("Agenda de Citas")
if citas:
    citas_enriquecidas = []
    for cita in citas:
        dueño = next((d for d in dueños if d['id'] == cita['owner_id']), None)
        animal = next((a for a in animales if a['id'] == cita['animal_id']), None)
        citas_enriquecidas.append({
            "ID": cita['id'],
            "Propietario": dueño['nombre'] if dueño else "No registrado",
            "Paciente": animal['name'] if animal else "No registrado",
            "Fecha": cita['date'],
            "Hora": cita['time'],
            "Tratamiento": cita['treatment'],
            "Motivo": cita['reason'],
            "Consulta": cita['consultation']
        })
    st.dataframe(
        pd.DataFrame(citas_enriquecidas),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No hay citas pendientes en el sistema")

# Control de estado para el propietario seleccionado
if 'previous_owner' not in st.session_state:
    st.session_state.previous_owner = None

# Sección de registro/modificación de citas
st.header("Registro de Citas")

# Selector de propietario
dueño_options = {f"{d['nombre']} (DNI: {d['dni']})": d['id'] for d in dueños}
selected_dueño = st.selectbox("Seleccionar Propietario", options=list(dueño_options.keys()))
owner_id = dueño_options[selected_dueño] if selected_dueño else None

# Actualizar si cambia el propietario
if owner_id != st.session_state.previous_owner:
    st.session_state.previous_owner = owner_id
    st.rerun()

with st.form("formulario_cita", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        id_cita = st.text_input("ID de Cita (solo para modificaciones)")
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
        else:
            st.warning("Seleccione un propietario para continuar")
            animal_id = None
        
        fecha = st.date_input("Fecha de la Cita")
    
    with col2:
        hora = st.selectbox("Hora de la Cita", opciones_de_horas)
        tratamiento = st.selectbox("Tipo de Tratamiento", tratamientos)
        motivo = st.text_area("Motivo de la Consulta")

    enviado = st.form_submit_button("Registrar Cita")
    if enviado:
        if fecha.weekday() == 6:
            st.error("No se realizan atenciones los días domingo")
        elif not all([owner_id, animal_id, fecha, hora, tratamiento, motivo]):
            st.error("Todos los campos son obligatorios")
        else:
            crear_actualizar_cita(id_cita, owner_id, animal_id, fecha, hora, tratamiento, motivo, citas, bool(id_cita))

# Sección de gestión de citas
st.header("Gestión de Citas")

tab1, tab2 = st.tabs(["Cancelar Cita", "Completar Cita"])

with tab1:
    with st.form("cancelar_cita", clear_on_submit=True):
        id_eliminar = st.text_input("ID de la Cita a Cancelar")
        motivo_cancelacion = st.text_area("Motivo de la Cancelación")
        if st.form_submit_button("Confirmar Cancelación"):
            if id_eliminar and motivo_cancelacion:
                try:
                    respuesta = requests.delete(f"{url_api}/{id_eliminar}")
                    if respuesta.status_code == 204:
                        st.success("Cita cancelada exitosamente")
                        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
                    else:
                        st.error(f"Error en la cancelación: {respuesta.text}")
                except:
                    st.error("Error en la conexión con el servidor")
            else:
                st.error("El ID de la cita y el motivo de cancelación son obligatorios")

with tab2:
    id_completar = st.text_input("ID de la Cita a Completar")
    
    if id_completar:
        cita = next((c for c in citas if str(c['id']) == id_completar), None)
        if not cita:
            st.error("Cita no encontrada o ya completada")
        else:
            precios_tratamientos = obtener_precios_tratamientos()
            
            with st.form("completar_cita", clear_on_submit=True):
                tratamientos_adicionales = st.multiselect(
                    "Tratamientos Realizados",
                    options=tratamientos,
                    help="Seleccione todos los tratamientos realizados durante la consulta"
                )

                col1, col2 = st.columns(2)
                with col1:
                    metodo_pago = st.selectbox(
                        "Método de Pago",
                        options=["Efectivo", "Tarjeta", "Transferencia"]
                    )
                
                with col2:
                    precio_total = sum(precios_tratamientos.get(t, 0) for t in tratamientos_adicionales)
                    st.metric("Total a Cobrar", f"{precio_total:.2f} EUR")

                if st.form_submit_button("Finalizar Consulta"):
                    if not tratamientos_adicionales:
                        st.error("Debe registrar al menos un tratamiento")
                    else:
                        try:
                            datos_completados = {
                                "treatments": tratamientos_adicionales,
                                "payment_method": metodo_pago
                            }
                            respuesta = requests.put(
                                f"{url_api}/{id_completar}/complete",
                                json=datos_completados
                            )
                            if respuesta.status_code == 201:
                                st.success("Consulta finalizada exitosamente. Factura generada.")
                                st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
                            else:
                                st.error(f"Error al finalizar la consulta: {respuesta.text}")
                        except:
                            st.error("Error en la conexión con el servidor")