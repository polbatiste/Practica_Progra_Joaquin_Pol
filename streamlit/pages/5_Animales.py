# streamli/pages/5_Animales.py

import streamlit as st
import requests
import pandas as pd

# URLs de la API
API_URL_ANIMALS = "http://app:8000/api/v1/animals"
API_URL_OWNERS = "http://app:8000/api/v1/owners"

# Título de la página
st.title("Alta de Animales - Clínica Veterinaria")

# Función para obtener dueños
def get_owners():
    response = requests.get(API_URL_OWNERS)
    if response.status_code == 200:
        return response.json()
    return []

def create_animal(name, species, breed, age, owner_id):
    data = {
        "name": name,
        "species": species,
        "breed": breed,
        "age": age,
        "owner_id": owner_id
    }
    response = requests.post(API_URL_ANIMALS, json=data)
    if response.status_code == 201:
        st.success("Animal registrado exitosamente")
        st.experimental_rerun()
    else:
        st.error("Error al registrar el animal")

def get_animals():
    response = requests.get(API_URL_ANIMALS)
    if response.status_code == 200:
        return response.json()
    return []

# Obtener lista de dueños
owners = get_owners()
owners_dict = {f"{owner['nombre']} (DNI: {owner['dni']})": owner['id'] for owner in owners}

# Formulario para registrar un nuevo animal
st.subheader("Registrar un Nuevo Animal")

# Opción para ir a registrar un nuevo dueño
if st.button("Registrar Nuevo Dueño"):
    st.switch_page("pages/4_Dueños.py")

with st.form("animal_form"):
    name = st.text_input("Nombre del Animal")
    species = st.text_input("Especie")
    breed = st.text_input("Raza")
    age = st.number_input("Edad", min_value=0, step=1)
    
    if owners:
        owner_selection = st.selectbox(
            "Seleccionar Dueño",
            options=list(owners_dict.keys()),
            index=None,
            placeholder="Seleccione un dueño..."
        )
        owner_id = owners_dict[owner_selection] if owner_selection else None
    else:
        st.warning("No hay dueños registrados. Por favor, registre un dueño primero.")
        owner_id = None

    submit_disabled = not owners
    if st.form_submit_button("Registrar", disabled=submit_disabled):
        if owner_id is not None:
            create_animal(name, species, breed, age, owner_id)

# Mostrar todos los animales registrados
st.subheader("Animales Registrados")
animals = get_animals()
if animals:
    # Enriquecer datos con información del dueño
    enriched_animals = []
    for animal in animals:
        owner = next((o for o in owners if o['id'] == animal['owner_id']), None)
        enriched_animals.append({
            'ID': animal['id'],
            'Nombre': animal['name'],
            'Especie': animal['species'],
            'Raza': animal['breed'],
            'Edad': animal['age'],
            'Dueño': owner['nombre'] if owner else 'Desconocido'
        })
    
    df_animals = pd.DataFrame(enriched_animals)
    st.table(df_animals)
else:
    st.info("No hay animales registrados.")