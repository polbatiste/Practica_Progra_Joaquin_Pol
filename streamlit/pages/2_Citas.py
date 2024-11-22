# streanlit/pages/2_Citas.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, time

# URLs de la API
url_api = "http://app:8000/api/v1/appointments"
url_tratamientos = "http://app:8000/api/v1/tratamientos"
url_owners = "http://app:8000/api/v1/owners"
url_animals = "http://app:8000/api/v1/animals"

def obtener_dueños():
    try:
        respuesta = requests.get(url_owners)
        respuesta.raise_for_status()
        dueños = respuesta.json()
        st.write(f"Debug - Total dueños cargados: {len(dueños)}")
        return dueños
    except:
        st.error("No se pudo obtener la lista de dueños")
        return []

def obtener_animales():
    try:
        respuesta = requests.get(url_animals)
        respuesta.raise_for_status()
        animales = respuesta.json()
        st.write(f"Debug - Total animales cargados: {len(animales)}")
        return animales
    except:
        st.error("No se pudo obtener la lista de animales")
        return []

def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        respuesta.raise_for_status()
        return respuesta.json()
    except:
        st.error("No se pudo conectar con el servidor")
        return []

def obtener_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        respuesta.raise_for_status()
        return [tratamiento["nombre"] for tratamiento in respuesta.json()]
    except:
        st.error("No se pudo obtener la lista de tratamientos")
        return []

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
    st.error("No hay consultas disponibles para la fecha y hora seleccionadas")
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
            st.success(f"Cita gestionada exitosamente en la consulta {consulta}")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error al gestionar la cita: {respuesta.text}")
    except:
        st.error("No se pudo conectar con el servidor")

st.title("Agenda tu Cita en la Clínica Veterinaria")

# Obtener datos
citas = obtener_citas()
dueños = obtener_dueños()
animales = obtener_animales()
tratamientos = obtener_tratamientos()
opciones_de_horas = generar_horas_inicio()

# Mostrar citas programadas
st.subheader("Citas Programadas")
if citas:
    # Enriquecer datos de citas con nombres de dueño y mascota
    citas_enriquecidas = []
    for cita in citas:
        dueño = next((d for d in dueños if d['id'] == cita['owner_id']), None)
        animal = next((a for a in animales if a['id'] == cita['animal_id']), None)
        citas_enriquecidas.append({
            "ID de Cita": cita['id'],
            "Dueño": dueño['nombre'] if dueño else "Desconocido",
            "Mascota": animal['name'] if animal else "Desconocido",
            "Fecha": cita['date'],
            "Hora": cita['time'],
            "Tratamiento": cita['treatment'],
            "Motivo": cita['reason'],
            "Consulta": cita['consultation']
        })
    st.table(pd.DataFrame(citas_enriquecidas))
else:
    st.info("No hay citas programadas")

# Formulario de citas
st.subheader("Programar o Modificar Cita")
with st.form("formulario_cita"):
    id_cita = st.text_input("ID de la Cita (solo para modificar)")
    
    # Selector de dueño
    dueño_options = {f"{d['nombre']} (DNI: {d['dni']})": d['id'] for d in dueños}
    selected_dueño = st.selectbox("Seleccionar Dueño", options=list(dueño_options.keys()))
    owner_id = dueño_options[selected_dueño] if selected_dueño else None
    
    # Selector de animal filtrado por dueño
    animal_id = None
    if owner_id:
        st.write("Debug - Owner ID:", owner_id)
        animales_dueño = [a for a in animales if a['owner_id'] == owner_id]
        st.write("Debug - Animales encontrados:", len(animales_dueño))
        st.write("Debug - IDs de animales encontrados:", [a['id'] for a in animales_dueño])
        
        if animales_dueño:
            animal_options = {a['name']: a['id'] for a in animales_dueño}
            selected_animal = st.selectbox(
                "Seleccionar Mascota", 
                options=list(animal_options.keys()),
                key=f"animal_select_{owner_id}"
            )
            animal_id = animal_options[selected_animal] if selected_animal else None
            st.write("Debug - Animal ID seleccionado:", animal_id)
        else:
            st.warning("Este dueño no tiene mascotas registradas")
    else:
        st.warning("Seleccione un dueño primero")

    fecha = st.date_input("Fecha")
    hora = st.selectbox("Hora", opciones_de_horas)
    tratamiento = st.selectbox("Tratamiento", tratamientos)
    motivo = st.text_area("Motivo")

    enviado = st.form_submit_button("Enviar")
    if enviado:
        if fecha.weekday() == 6:
            st.error("No se pueden programar citas los domingos")
        elif not all([owner_id, animal_id, fecha, hora, tratamiento, motivo]):
            st.error("Complete todos los campos del formulario")
        else:
            crear_actualizar_cita(id_cita, owner_id, animal_id, fecha, hora, tratamiento, motivo, citas, bool(id_cita))

# Eliminar citas
st.subheader("Eliminar Cita")
id_eliminar = st.text_input("ID de la Cita a Eliminar", "")
if id_eliminar and st.button("Confirmar Eliminación"):
    try:
        respuesta = requests.delete(f"{url_api}/{id_eliminar}")
        if respuesta.status_code == 204:
            st.success("Cita eliminada exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error al eliminar la cita: {respuesta.text}")
    except:
        st.error("No se pudo conectar con el servidor")