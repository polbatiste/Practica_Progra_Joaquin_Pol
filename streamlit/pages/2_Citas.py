import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, time

# Definir la URL de la API de citas y tratamientos
url_api = "http://app:8000/api/v1/appointments"
url_tratamientos = "http://app:8000/api/v1/tratamientos"

# Función para obtener todas las citas existentes de la API
def obtener_citas():
    try:
        respuesta = requests.get(url_api)
        respuesta.raise_for_status()
        return respuesta.json()  # Devuelve una lista de citas en formato JSON
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con el servidor. Inténtelo más tarde.")
        return []

# Función para obtener la lista de tratamientos desde la API
def obtener_tratamientos():
    try:
        respuesta = requests.get(url_tratamientos)
        respuesta.raise_for_status()
        tratamientos = respuesta.json()
        return [tratamiento["nombre"] for tratamiento in tratamientos]
    except requests.exceptions.RequestException:
        st.error("No se pudo obtener la lista de tratamientos. Inténtelo más tarde.")
        return []

# Generar una lista de horas de 9:00 AM a 8:00 PM en intervalos de 30 minutos
def generar_horas_inicio():
    horas = []
    hora_actual = time(9, 0)  # 9:00 AM
    fin = time(20, 0)  # 8:00 PM
    while hora_actual <= fin:
        horas.append(hora_actual)
        # Incremento de 30 minutos
        hora_actual = (datetime.combine(datetime.today(), hora_actual) + timedelta(minutes=30)).time()
    return horas

# Crear lista de opciones de horas
opciones_de_horas = generar_horas_inicio()

# Función para asignar automáticamente una consulta a la cita
def asignar_consulta(fecha, hora, citas):
    consultas_disponibles = ["1", "2", "3"]  # Consultas disponibles
    for consulta in consultas_disponibles:
        # Verificar si la consulta está libre para la fecha y hora dadas
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
        return  # Si no hay consulta disponible, salir de la función

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
        # Realizar una llamada PUT si es una actualización, de lo contrario, POST
        if es_actualizacion and id_cita:
            respuesta = requests.put(f"{url_api}/{id_cita}", json=datos_cita)
        else:
            respuesta = requests.post(url_api, json=datos_cita)

        if respuesta.status_code in [200, 201]:
            st.success(f"Cita gestionada exitosamente en la consulta {consulta}")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
        else:
            st.error(f"Error al gestionar la cita: {respuesta.text}")
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con el servidor para gestionar la cita.")

# Título de la aplicación
st.title("Agenda tu Cita en la Clínica Veterinaria")

# Sección para mostrar las citas existentes
st.subheader("Citas Programadas")
citas = obtener_citas()
if citas:
    # Convertir la lista de citas a un DataFrame de pandas para renombrar las columnas
    citas_df = pd.DataFrame(citas)
    if not citas_df.empty:
        # Renombrar las columnas para mostrarlas de forma más clara y profesional
        citas_df.rename(columns={
            "id": "ID de Cita",
            "client_name": "Nombre de Cliente",
            "pet_name": "Nombre de Mascota",
            "date": "Fecha",
            "time": "Hora",
            "treatment": "Tratamiento",
            "reason": "Motivo",
            "consultation": "Consulta"
        }, inplace=True)
        st.table(citas_df)
else:
    st.info("No hay citas programadas en este momento.")

# Sección para el formulario de creación/actualización de citas
st.subheader("Programar o Modificar Cita")
tratamientos = obtener_tratamientos()  # Obtener lista de tratamientos desde la API
with st.form("formulario_cita"):
    id_cita = st.text_input("ID de la Cita (solo para modificar una cita ya existente)")
    nombre_cliente = st.text_input("Nombre de Cliente")
    nombre_mascota = st.text_input("Nombre de Mascota")
    fecha = st.date_input("Fecha")
    hora = st.selectbox("Hora", opciones_de_horas)
    tratamiento = st.selectbox("Tratamiento", tratamientos)  # Menú desplegable de tratamientos
    motivo = st.text_area("Motivo")

    enviado = st.form_submit_button("Enviar")
    if enviado:
        if fecha.weekday() == 6:
            st.error("No se pueden programar citas los domingos. Por favor, elija otra fecha.")
        elif not nombre_cliente or not nombre_mascota or not fecha or not hora or not tratamiento or not motivo:
            st.error("Por favor, complete todos los campos del formulario.")
        else:
            es_actualizacion = bool(id_cita)
            crear_actualizar_cita(id_cita, nombre_cliente, nombre_mascota, fecha, hora, tratamiento, motivo, citas, es_actualizacion)

# Sección para eliminar citas
st.subheader("Eliminar Cita")
id_eliminar = st.text_input("ID de la Cita a Eliminar", "")
if id_eliminar and st.button("Confirmar Eliminación"):
    try:
        respuesta = requests.delete(f"{url_api}/{id_eliminar}")
        if respuesta.status_code == 204:
            st.success("Cita eliminada exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
        else:
            st.error(f"Error al eliminar la cita: {respuesta.text}")
    except requests.exceptions.RequestException:
        st.error("No se pudo conectar con el servidor para eliminar la cita.")