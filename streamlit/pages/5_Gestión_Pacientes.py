import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Pacientes",
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
    </style>
""", unsafe_allow_html=True)

# URLs de la API
API_URL_ANIMALS = "http://app:8000/api/v1/animals"
API_URL_OWNERS = "http://app:8000/api/v1/owners"

st.title("Sistema de Gestión de Pacientes")

def get_owners():
    try:
        response = requests.get(API_URL_OWNERS)
        response.raise_for_status()
        owners = response.json()
        return owners
    except:
        st.error("Error de conexión: No se pudo obtener la lista de propietarios")
        return []

def create_animal(name, species, breed, age, owner_id):
    data = {
        "name": name,
        "species": species,
        "breed": breed,
        "age": age,
        "owner_id": owner_id
    }
    try:
        response = requests.post(API_URL_ANIMALS, json=data)
        if response.status_code == 201:
            st.success("Paciente registrado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error en el registro: {response.text}")
    except:
        st.error("Error de conexión con el servidor")

def get_animals():
    try:
        response = requests.get(API_URL_ANIMALS)
        response.raise_for_status()
        animals = response.json()
        return animals
    except:
        st.error("Error de conexión: No se pudo obtener la lista de pacientes")
        return []

def mark_animal_as_deceased(animal_id):
    try:
        response = requests.patch(f"{API_URL_ANIMALS}/{animal_id}/deceased")
        
        if response.status_code == 200:
            st.success("El paciente ha sido marcado como fallecido")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error en la actualización del estado: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión con el servidor: {str(e)}")

def delete_animal(animal_id):
    try:
        response = requests.delete(f"{API_URL_ANIMALS}/{animal_id}")
        if response.status_code == 204:
            st.success("Registro eliminado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error al eliminar el registro: {response.text}")
    except:
        st.error("Error de conexión con el servidor")

# Obtener datos
owners = get_owners()
owners_dict = {f"{owner['nombre']} (DNI: {owner['dni']})": owner['id'] for owner in owners}

# Sección principal con tabs
tab1, tab2, tab3 = st.tabs(["Registro de Pacientes", "Lista de Pacientes", "Gestión de Estados"])

with tab1:
    st.header("Registro de Nuevo Paciente")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Registrar Nuevo Propietario"):
            st.write('<meta http-equiv="refresh" content="0;url=/pages/4_Gestión_Propietarios.py">', unsafe_allow_html=True)

    with st.form("animal_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre del Paciente")
            species = st.text_input("Especie")
            breed = st.text_input("Raza")
        
        with col2:
            age = st.number_input("Edad", min_value=0, step=1)
            if owners:
                owner_selection = st.selectbox(
                    "Seleccionar Propietario",
                    options=list(owners_dict.keys()),
                    index=None,
                    placeholder="Seleccione un propietario..."
                )
                owner_id = owners_dict[owner_selection] if owner_selection else None
            else:
                st.warning("No hay propietarios registrados en el sistema")
                owner_id = None

        submit_disabled = not owners
        if st.form_submit_button("Registrar Paciente", disabled=submit_disabled):
            if all([name, species, breed, age, owner_id]):
                create_animal(name, species, breed, age, owner_id)
            else:
                st.error("Todos los campos son obligatorios")

with tab2:
    st.header("Registro de Pacientes")
    animals = get_animals()
    if animals:
        enriched_animals = []
        for animal in animals:
            owner = next((o for o in owners if o['id'] == animal['owner_id']), None)
            status_color = "#dc3545" if animal['status'] == "DECEASED" else "#28a745"
            enriched_animals.append({
                'ID': animal['id'],
                'Nombre': animal['name'],
                'Especie': animal['species'],
                'Raza': animal['breed'],
                'Edad': animal['age'],
                'Estado': f"<span style='color: {status_color}'>{animal['status']}</span>",
                'Propietario': owner['nombre'] if owner else 'No registrado'
            })
        
        df_animals = pd.DataFrame(enriched_animals)
        st.write(
            df_animals.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
    else:
        st.info("No hay pacientes registrados en el sistema")

with tab3:
    st.header("Actualización de Estados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Registrar Fallecimiento")
        with st.form("mark_deceased_form", clear_on_submit=True):
            animal_id = st.number_input("ID del Paciente", min_value=1, step=1, key="deceased_id")
            submit_mark_deceased = st.form_submit_button("Actualizar Estado")
            
            if submit_mark_deceased:
                if animal_id:
                    mark_animal_as_deceased(animal_id)
                else:
                    st.error("Por favor, ingrese un ID válido")

    with col2:
        st.subheader("Eliminar Registro")
        with st.form("delete_animal_form", clear_on_submit=True):
            animal_id = st.number_input("ID del Paciente", min_value=1, step=1, key="delete_id")
            reason = st.text_area("Motivo de la eliminación", height=100)
            submit_delete_animal = st.form_submit_button("Eliminar Registro")
            
            if submit_delete_animal:
                if animal_id and reason:
                    delete_animal(animal_id)
                else:
                    st.error("El ID y el motivo son obligatorios")