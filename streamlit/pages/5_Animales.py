import streamlit as st
import requests
import pandas as pd

# Configuración del endpoint de la API
API_URL = "http://app:8000/api/v1/animals"

# Título de la página
st.title("Alta de Animales - Clínica Veterinaria")

# Función para registrar un nuevo animal
def create_animal(name, species, breed, age, owner_id):
    data = {
        "name": name,
        "species": species,
        "breed": breed,
        "age": age,
        "owner_id": owner_id
    }
    response = requests.post(API_URL, json=data)
    if response.status_code == 201:
        st.success("Animal registrado exitosamente")
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
    else:
        st.error("Error al registrar el animal")

# Función para obtener todos los animales
def get_animals():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al cargar los animales")
        return []

# Sección de formulario para registrar un nuevo animal
st.subheader("Registrar un Nuevo Animal")
with st.form("animal_form"):
    name = st.text_input("Nombre del Animal")
    species = st.text_input("Especie")
    breed = st.text_input("Raza")
    age = st.number_input("Edad", min_value=0, step=1)
    owner_id = st.number_input("ID del Dueño", min_value=0, step=1)

    submitted = st.form_submit_button("Registrar")
    if submitted:
        create_animal(name, species, breed, age, owner_id)

# Mostrar todos los animales registrados en una tabla
st.subheader("Animales Registrados")
animals = get_animals()
if animals:
    df_animals = pd.DataFrame(animals)
    st.table(df_animals)
else:
    st.info("No hay animales registrados.")