import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Tratamientos",
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
    .stNumberInput > div > div > input,
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
    .table-container {
        margin: 2rem 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .price-column {
        text-align: right;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# Configuración del endpoint de la API
API_URL = "http://app:8000/api/v1/tratamientos"

st.title("Sistema de Gestión de Tratamientos")

def get_tratamientos():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            tratamientos = response.json()
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
            st.error("Error de conexión: No se pudieron cargar los tratamientos")
            return []
    except:
        st.error("Error de conexión con el servidor")
        return []

def create_tratamiento(tipo, nombre, descripcion, precio):
    data = {
        "tipo": tipo,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio
    }
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 201:
            st.success("Tratamiento registrado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error("Error en el registro del tratamiento")
    except:
        st.error("Error de conexión con el servidor")

def update_tratamiento(nombre, tipo, descripcion, precio):
    data = {
        "tipo": tipo,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio
    }
    try:
        response = requests.put(f"{API_URL}/{nombre}", json=data)
        if response.status_code == 200:
            st.success("Tratamiento actualizado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error("Error en la actualización del tratamiento")
    except:
        st.error("Error de conexión con el servidor")

def delete_tratamiento(nombre):
    try:
        response = requests.delete(f"{API_URL}/{nombre}")
        if response.status_code == 200:
            st.success("Tratamiento eliminado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error("Error al eliminar el tratamiento")
    except:
        st.error("Error de conexión con el servidor")

# Crear tabs para mejor organización
tab1, tab2, tab3 = st.tabs(["Lista de Tratamientos", "Gestión de Tratamientos", "Eliminar Tratamientos"])

with tab1:
    st.header("Catálogo de Tratamientos")
    tratamientos = get_tratamientos()
    if tratamientos:
        df = pd.DataFrame(tratamientos)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Precio": st.column_config.Column(
                    width="medium",
                    help="Precio del tratamiento en euros"
                )
            }
        )
    else:
        st.info("No hay tratamientos registrados en el sistema")

with tab2:
    st.header("Registro y Modificación de Tratamientos")
    with st.form("tratamiento_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.text_input("Tipo de Tratamiento")
            nombre = st.text_input("Nombre del Tratamiento")
        
        with col2:
            precio = st.number_input(
                "Precio (€)", 
                min_value=0.0, 
                step=0.1, 
                format="%.2f",
                help="Introduce el precio en euros"
            )
        
        descripcion = st.text_area(
            "Descripción del Tratamiento",
            height=100,
            help="Describe detalladamente el tratamiento"
        )

        if st.form_submit_button("Guardar Tratamiento"):
            if all([tipo, nombre, descripcion]):
                if any(tratamiento['Nombre'] == nombre for tratamiento in tratamientos):
                    update_tratamiento(nombre, tipo, descripcion, precio)
                else:
                    create_tratamiento(tipo, nombre, descripcion, precio)
            else:
                st.error("Todos los campos son obligatorios")

with tab3:
    st.header("Eliminar Tratamientos")
    if tratamientos:
        nombre_eliminar = st.selectbox(
            "Seleccionar tratamiento a eliminar",
            options=[t['Nombre'] for t in tratamientos]
        )
        razon = st.text_area("Motivo de la eliminación", height=100)
        
        if st.button("Eliminar Tratamiento", type="primary"):
            if razon:
                delete_tratamiento(nombre_eliminar)
            else:
                st.error("Por favor, indique el motivo de la eliminación")
    else:
        st.info("No hay tratamientos registrados en el sistema")