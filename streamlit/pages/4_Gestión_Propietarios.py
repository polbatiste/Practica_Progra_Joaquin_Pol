import streamlit as st
import requests
import pandas as pd
import time

API_URL = "http://app:8000/api/v1/owners"

st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Propietarios",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for a more professional look
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
    .stTextInput > div > div > input {
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
    </style>
""", unsafe_allow_html=True)

st.title("Sistema de Gestión de Propietarios")

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
        st.success("Propietario registrado exitosamente")
        if st.session_state.get('from_animals'):
            st.session_state['from_animals'] = False
            st.switch_page("pages/5_Animales.py")
        else:
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    else:
        st.error(f"Error al registrar propietario: {response.json().get('detail', 'Error desconocido')}")

def get_owners():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    st.error("Error al cargar los propietarios")
    return []

def request_owner_deletion(dni, email, reason):
    data = {
        "dni": dni,
        "email": email,
        "reason": reason
    }
    response = requests.post(f"{API_URL}/delete", json=data)
    return response

if 'from_animals' not in st.session_state:
    st.session_state['from_animals'] = False

# Sección de Registro
st.subheader("Registro de Nuevo Propietario")
with st.form("owner_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre completo")
        dni = st.text_input("DNI")
        direccion = st.text_input("Dirección")
    with col2:
        telefono = st.text_input("Teléfono")
        correo_electronico = st.text_input("Correo Electrónico")
    
    submit = st.form_submit_button("Registrar Propietario")
    if submit:
        create_owner(nombre, dni, direccion, telefono, correo_electronico)

if st.session_state.get('from_animals'):
    if st.button("Volver a Registro de Pacientes"):

        st.switch_page("pages/5_Gestión_Pacientes.py")

# Sección de Eliminación
st.subheader("Solicitud de Baja de Propietario")
with st.form("delete_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        delete_dni = st.text_input("DNI del propietario")
        delete_email = st.text_input("Confirmación de correo electrónico")
    with col2:
        delete_reason = st.text_area("Motivo de la baja")
    
    delete_submit = st.form_submit_button("Procesar Baja")
    
    if delete_submit:
        if not delete_dni or not delete_email:
            st.error("Por favor, complete los campos obligatorios (DNI y correo electrónico)")
        else:
            response = request_owner_deletion(delete_dni, delete_email, delete_reason)
            if response.status_code == 204:
                st.success("Solicitud procesada correctamente. Se ha enviado un correo de confirmación.")
            else:
                st.error(f"Error en el proceso: {response.json().get('detail', 'Error desconocido')}")

# Sección de Listado
st.subheader("Registro de Propietarios")
owners = get_owners()
if owners:
    df_owners = pd.DataFrame(owners)
    st.dataframe(
        df_owners,
        column_config={
            "id": st.column_config.Column("ID", width="small"),
            "nombre": st.column_config.Column("Nombre", width="medium"),
            "dni": st.column_config.Column("DNI", width="medium"),
            "direccion": st.column_config.Column("Dirección", width="large"),
            "telefono": st.column_config.Column("Teléfono", width="medium"),
            "correo_electronico": st.column_config.Column("Correo Electrónico", width="large")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No hay propietarios registrados en el sistema")

# Sección de Búsqueda
st.subheader("Búsqueda de Propietarios")
col1, col2 = st.columns(2)
with col1:
    search_name = st.text_input("Buscar por nombre")
with col2:
    search_dni = st.text_input("Buscar por DNI")

if search_name or search_dni:
    filtered_owners = [
        owner for owner in owners
        if (search_name.lower() in owner["nombre"].lower() if search_name else True) and
           (search_dni in owner["dni"] if search_dni else True)
    ]
    if filtered_owners:
        st.write("Resultados de la búsqueda:")
        st.dataframe(
            pd.DataFrame(filtered_owners),
            column_config={
                "id": st.column_config.Column("ID", width="small"),
                "nombre": st.column_config.Column("Nombre", width="medium"),
                "dni": st.column_config.Column("DNI", width="medium"),
                "direccion": st.column_config.Column("Dirección", width="large"),
                "telefono": st.column_config.Column("Teléfono", width="medium"),
                "correo_electronico": st.column_config.Column("Correo Electrónico", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No se encontraron registros que coincidan con los criterios de búsqueda.")