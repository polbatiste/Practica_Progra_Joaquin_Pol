import streamlit as st
import requests
import pandas as pd

# Configuración del endpoint de la API para tratamientos
API_URL = "http://app:8000/api/v1/tratamientos"

# Título de la página
st.title("Gestión de Tratamientos - Clínica Veterinaria")

# Función para obtener todos los tratamientos
def get_tratamientos():
    response = requests.get(API_URL)
    if response.status_code == 200:
        tratamientos = response.json()
        # Normalizar y estructurar los datos para mostrar en la tabla
        return [
            {
                "Nombre": tratamiento.get("nombre", ""),
                "Tipo": tratamiento.get("tipo", ""),
                "Descripción": tratamiento.get("descripcion", ""),
                "Precio": f"{tratamiento.get('precio', 0.0):.2f} €"
            }
            for tratamiento in tratamientos
        ]
    else:
        st.error("Error al cargar los tratamientos")
        return []

# Función para crear un nuevo tratamiento
def create_tratamiento(tipo, nombre, descripcion, precio):
    data = {
        "tipo": tipo,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio
    }
    response = requests.post(API_URL, json=data)
    if response.status_code == 201:
        st.success("Tratamiento añadido exitosamente")
        # Recargar la página usando HTML
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    else:
        st.error("Error al añadir el tratamiento")

# Función para actualizar un tratamiento
def update_tratamiento(nombre, tipo, descripcion, precio):
    data = {
        "tipo": tipo,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio
    }
    response = requests.put(f"{API_URL}/{nombre}", json=data)
    if response.status_code == 200:
        st.success("Tratamiento actualizado exitosamente")
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    else:
        st.error("Error al actualizar el tratamiento")

# Función para eliminar un tratamiento
def delete_tratamiento(nombre):
    response = requests.delete(f"{API_URL}/{nombre}")
    if response.status_code == 200:
        st.success("Tratamiento eliminado exitosamente")
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    else:
        st.error("Error al eliminar el tratamiento")

# Mostrar todos los tratamientos en una tabla
st.subheader("Tratamientos Registrados")
tratamientos = get_tratamientos()
if tratamientos:
    # Convertir los datos a un DataFrame y mostrarlo en la tabla
    df = pd.DataFrame(tratamientos)
    st.table(df)

# Sección para añadir o modificar tratamientos
st.subheader("Añadir o Modificar Tratamiento")
with st.form("tratamiento_form"):
    tipo = st.text_input("Tipo de Tratamiento")
    nombre = st.text_input("Nombre del Tratamiento")
    descripcion = st.text_area("Descripción")
    precio = st.number_input("Precio", min_value=0.0, step=0.1, format="%.2f")

    if st.form_submit_button("Guardar Tratamiento"):
        # Decidir entre crear o actualizar según si el tratamiento ya existe
        if any(tratamiento['Nombre'] == nombre for tratamiento in tratamientos):
            update_tratamiento(nombre, tipo, descripcion, precio)
        else:
            create_tratamiento(tipo, nombre, descripcion, precio)

# Sección para eliminar un tratamiento
st.subheader("Eliminar Tratamiento")
if tratamientos:
    nombre_eliminar = st.selectbox("Seleccione un tratamiento para eliminar", [t['Nombre'] for t in tratamientos])
    if st.button("Eliminar"):
        delete_tratamiento(nombre_eliminar)
else:
    st.info("No hay tratamientos registrados para eliminar.")