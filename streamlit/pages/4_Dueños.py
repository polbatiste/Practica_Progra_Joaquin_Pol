import streamlit as st
import requests

# Configuración del endpoint de la API
API_URL = "http://app:8000/api/v1/owners"

# Título de la página
st.title("Alta de Dueños - Clínica Veterinaria")

# Función para registrar un nuevo dueño
def create_owner(nombre, dni, direccion, telefono, correo_electronico):
    data = {
        "nombre": nombre,
        "dni": dni,
        "direccion": direccion,
        "telefono": telefono,
        "correo_electronico": correo_electronico
    }
    response = requests.post(API_URL, json=data)
    if response.status_code == 201:
        st.success("Dueño registrado exitosamente")
    else:
        st.error("Error al registrar dueño")

# Función para obtener todos los dueños
def get_owners():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al cargar los dueños")
        return []

# Sección de formulario para registrar un nuevo dueño
st.subheader("Registrar un Nuevo Dueño")
with st.form("owner_form"):
    nombre = st.text_input("Nombre")
    dni = st.text_input("DNI")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    correo_electronico = st.text_input("Correo Electrónico")

    submitted = st.form_submit_button("Registrar")
    if submitted:
        create_owner(nombre, dni, direccion, telefono, correo_electronico)

# Mostrar todos los dueños registrados
st.subheader("Dueños Registrados")
owners = get_owners()
if owners:
    st.write(owners)

# Sección de búsqueda de dueños
st.subheader("Buscar Dueños")
search_name = st.text_input("Buscar por Nombre")
search_dni = st.text_input("Buscar por DNI")

# Filtrar dueños según el criterio de búsqueda
if search_name or search_dni:
    filtered_owners = [
        owner for owner in owners
        if (search_name.lower() in owner["nombre"].lower() if search_name else True) and
           (search_dni in owner["dni"] if search_dni else True)
    ]
    if filtered_owners:
        st.write("Resultados de la búsqueda:")
        st.write(filtered_owners)
    else:
        st.info("No se encontraron dueños que coincidan con los criterios de búsqueda.")
else:
    if owners:
        st.write(owners)
    else:
        st.info("No hay dueños registrados.")
