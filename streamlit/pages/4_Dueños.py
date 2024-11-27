# streamlit/pages/4_Dueños.py

import streamlit as st
import requests
import pandas as pd

API_URL = "http://app:8000/api/v1/owners"

st.title("Alta de Dueños - Clínica Veterinaria")

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
        if st.session_state.get('from_animals'):
            st.session_state['from_animals'] = False
            st.switch_page("pages/5_Animales.py")
        else:
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    else:
        st.error(f"Error al registrar dueño: {response.json().get('detail', 'Error desconocido')}")

def get_owners():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    st.error("Error al cargar los dueños")
    return []

def request_owner_deletion(dni, email, reason):
    data = {
        "dni": dni,
        "email": email,
        "reason": reason
    }
    response = requests.post(f"{API_URL}/delete-request", json=data)
    return response

if 'from_animals' not in st.session_state:
    st.session_state['from_animals'] = False

# Sección de Registro
st.subheader("Registrar un Nuevo Dueño")
with st.form("owner_form"):
    nombre = st.text_input("Nombre")
    dni = st.text_input("DNI")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    correo_electronico = st.text_input("Correo Electrónico")
    
    col1, col2 = st.columns(2)
    with col1:
        submit = st.form_submit_button("Registrar")
    if submit:
        create_owner(nombre, dni, direccion, telefono, correo_electronico)

if st.session_state.get('from_animals'):
    if st.button("Volver a Registro de Animales"):
        st.switch_page("pages/5_Animales.py")

# Sección de Eliminación
st.subheader("Solicitar Eliminación de Datos")
with st.form("delete_form"):
    delete_dni = st.text_input("DNI del dueño a eliminar")
    delete_email = st.text_input("Correo electrónico de confirmación")
    delete_reason = st.text_area("Razón de la eliminación (opcional)")
    
    delete_submit = st.form_submit_button("Solicitar Eliminación")
    
    if delete_submit:
        if not delete_dni or not delete_email:
            st.error("Por favor, complete los campos obligatorios (DNI y correo electrónico)")
        else:
            response = request_owner_deletion(delete_dni, delete_email, delete_reason)
            if response.status_code == 200:
                st.success("""
                    Solicitud de eliminación enviada correctamente.
                    Por favor, revise su correo electrónico para confirmar la eliminación.
                """)
            else:
                st.error(f"Error al procesar la solicitud: {response.json().get('detail', 'Error desconocido')}")

# Sección de Confirmación de Eliminación
params = st.experimental_get_query_params()
if 'confirm-deletion' in params:
    dni = params['confirm-deletion'][0]
    st.warning(f"¿Está seguro que desea eliminar permanentemente sus datos y los de sus mascotas asociadas?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirmar eliminación"):
            response = requests.get(f"{API_URL}/confirm-deletion/{dni}")
            if response.status_code == 200:
                st.success("Sus datos han sido eliminados exitosamente")
                st.write('<meta http-equiv="refresh" content="3;url=/">', unsafe_allow_html=True)
            else:
                st.error("Error al procesar la eliminación")
    with col2:
        if st.button("Cancelar"):
            st.write('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)

# Sección de Listado
st.subheader("Dueños Registrados")
owners = get_owners()
if owners:
    df_owners = pd.DataFrame(owners)
    st.table(df_owners)

# Sección de Búsqueda
st.subheader("Buscar Dueños")
search_name = st.text_input("Buscar por Nombre")
search_dni = st.text_input("Buscar por DNI")

if search_name or search_dni:
    filtered_owners = [
        owner for owner in owners
        if (search_name.lower() in owner["nombre"].lower() if search_name else True) and
           (search_dni in owner["dni"] if search_dni else True)
    ]
    if filtered_owners:
        st.write("Resultados de la búsqueda:")
        st.table(pd.DataFrame(filtered_owners))
    else:
        st.info("No se encontraron dueños que coincidan con los criterios de búsqueda.")