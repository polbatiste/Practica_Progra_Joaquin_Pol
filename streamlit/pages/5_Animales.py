import streamlit as st
import requests
import pandas as pd

# URLs de la API
API_URL_ANIMALS = "http://app:8000/api/v1/animals"
API_URL_OWNERS = "http://app:8000/api/v1/owners"

st.title("Gestión de Animales - Clínica Veterinaria")

def get_owners():
    try:
        response = requests.get(API_URL_OWNERS)
        response.raise_for_status()
        owners = response.json()
        return owners
    except:
        st.error("No se pudo obtener la lista de dueños")
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
            st.success("Animal registrado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error al registrar el animal: {response.text}")
    except:
        st.error("No se pudo conectar con el servidor")

def get_animals():
    try:
        response = requests.get(API_URL_ANIMALS)
        response.raise_for_status()
        animals = response.json()
        return animals
    except:
        st.error("No se pudo obtener la lista de animales")
        return []

def mark_animal_as_deceased(animal_id):
    try:
        response = requests.put(f"{API_URL_ANIMALS}/{animal_id}/mark-deceased")
        if response.status_code == 200:
            st.success(f"El animal con ID {animal_id} ha sido marcado como fallecido.")
            st.experimental_rerun()
        else:
            st.error(f"Error al marcar como fallecido: {response.text}")
    except:
        st.error("No se pudo conectar con el servidor.")

def delete_animal(animal_id):
    try:
        response = requests.delete(f"{API_URL_ANIMALS}/{animal_id}")
        if response.status_code == 204:
            st.success(f"El animal con ID {animal_id} ha sido eliminado.")
            st.experimental_rerun()
        else:
            st.error(f"Error al eliminar el animal: {response.text}")
    except:
        st.error("No se pudo conectar con el servidor.")

# Obtener datos
owners = get_owners()
owners_dict = {f"{owner['nombre']} (DNI: {owner['dni']})": owner['id'] for owner in owners}

# Formulario para registrar un nuevo animal
st.subheader("Registrar un Nuevo Animal")

# Opción para ir a registrar un nuevo dueño
if st.button("Registrar Nuevo Dueño"):
    st.write('<meta http-equiv="refresh" content="0;url=/pages/4_Dueños.py">', unsafe_allow_html=True)

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
        if all([name, species, breed, age, owner_id]):
            create_animal(name, species, breed, age, owner_id)
        else:
            st.error("Por favor complete todos los campos")

# Mostrar todos los animales registrados
st.subheader("Animales Registrados")
animals = get_animals()
if animals:
    enriched_animals = []
    for animal in animals:
        owner = next((o for o in owners if o['id'] == animal['owner_id']), None)
        enriched_animals.append({
            'ID': animal['id'],
            'Nombre': animal['name'],
            'Especie': animal['species'],
            'Raza': animal['breed'],
            'Edad': animal['age'],
            'Estado': animal['status'],  # Mostrar estado
            'Dueño': owner['nombre'] if owner else 'Desconocido'
        })
    
    df_animals = pd.DataFrame(enriched_animals)
    st.table(df_animals)
else:
    st.info("No hay animales registrados.")

# Sección para marcar un animal como fallecido
st.subheader("Marcar Animal como Fallecido")
with st.form("mark_deceased_form"):
    animal_id = st.number_input("ID del Animal", min_value=1, step=1, key="deceased_id")
    submit_mark_deceased = st.form_submit_button("Marcar como Fallecido")
    
    if submit_mark_deceased:
        if animal_id:
            mark_animal_as_deceased(animal_id)
        else:
            st.error("Por favor, ingrese un ID válido.")

# Sección para eliminar un animal
st.subheader("Eliminar Animal")
with st.form("delete_animal_form"):
    animal_id = st.number_input("ID del Animal", min_value=1, step=1, key="delete_id")
    submit_delete_animal = st.form_submit_button("Eliminar Animal")
    
    if submit_delete_animal:
        if animal_id:
            delete_animal(animal_id)
        else:
            st.error("Por favor, ingrese un ID válido.")