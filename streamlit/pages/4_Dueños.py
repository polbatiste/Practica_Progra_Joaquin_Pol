# streamlit/pages/4_Dueños.py

import streamlit as st
import requests
import pandas as pd
import time

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
        st.success("✅ Dueño registrado exitosamente")
        if st.session_state.get('from_animals'):
            st.session_state['from_animals'] = False
            st.switch_page("pages/5_Animales.py")
        else:
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    else:
        st.error(f"❌ Error al registrar dueño: {response.json().get('detail', 'Error desconocido')}")

def get_owners():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    st.error("❌ Error al cargar los dueños")
    return []

def request_owner_deletion(dni, email, reason):
    data = {
        "dni": dni,
        "email": email,
        "reason": reason
    }
    response = requests.post(f"{API_URL}/delete-request", json=data)
    return response

def check_deletion_confirmation(dni: str):
    try:
        response = requests.get(f"{API_URL}/confirm-deletion/{dni}")
        if response.status_code == 200:
            st.success("✅ Sus datos han sido eliminados exitosamente")
            st.balloons()
            time.sleep(2)
            # Recargar la página principal
            st.write('<meta http-equiv="refresh" content="2;url=/">', unsafe_allow_html=True)
            return True
        else:
            error_msg = response.json().get('detail', 'Error desconocido')
            st.error(f"❌ Error al procesar la eliminación: {error_msg}")
            return False
    except Exception as e:
        st.error(f"❌ Error en la solicitud: {str(e)}")
        return False

if 'from_animals' not in st.session_state:
    st.session_state['from_animals'] = False

# Sección de Registro
st.subheader("📝 Registrar un Nuevo Dueño")
with st.form("owner_form"):
    nombre = st.text_input("Nombre")
    dni = st.text_input("DNI")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    correo_electronico = st.text_input("Correo Electrónico")
    
    col1, col2 = st.columns(2)
    with col1:
        submit = st.form_submit_button("✅ Registrar")
    if submit:
        create_owner(nombre, dni, direccion, telefono, correo_electronico)

if st.session_state.get('from_animals'):
    if st.button("↩️ Volver a Registro de Animales"):
        st.switch_page("pages/5_Animales.py")

# Sección de Eliminación
st.subheader("🗑️ Solicitar Eliminación de Datos")
with st.form("delete_form"):
    delete_dni = st.text_input("DNI del dueño a eliminar")
    delete_email = st.text_input("Correo electrónico de confirmación")
    delete_reason = st.text_area("Razón de la eliminación (opcional)")
    
    delete_submit = st.form_submit_button("🗑️ Solicitar Eliminación")
    
    if delete_submit:
        if not delete_dni or not delete_email:
            st.error("❌ Por favor, complete los campos obligatorios (DNI y correo electrónico)")
        else:
            response = request_owner_deletion(delete_dni, delete_email, delete_reason)
            if response.status_code == 200:
                st.success("""
                    ✅ Solicitud de eliminación enviada correctamente.
                    📧 Por favor, revise su correo electrónico para confirmar la eliminación.
                """)
            else:
                st.error(f"❌ Error al procesar la solicitud: {response.json().get('detail', 'Error desconocido')}")

# Sección de Confirmación de Eliminación
# En la sección de confirmación de eliminación:

params = st.query_params
if 'delete' in params:
    dni = params['delete']
    
    st.warning("⚠️ ¿Está seguro que desea eliminar permanentemente sus datos y los de sus mascotas asociadas?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✔️ Confirmar eliminación"):
            try:
                response = requests.delete(f"{API_URL}/{dni}")
                if response.status_code in [200, 204]:
                    st.success("✅ Sus datos han sido eliminados exitosamente")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Error al eliminar los datos")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("❌ Cancelar"):
            st.write('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)

# Mostrar estado de la eliminación si está en progreso
if st.session_state.get('deletion_confirmed'):
    st.info("🔄 Procesando la eliminación...")
    time.sleep(1)
    st.experimental_rerun()

# Sección de Listado
st.subheader("📋 Dueños Registrados")
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
            "correo_electronico": st.column_config.Column("Email", width="large")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("ℹ️ No hay dueños registrados")

# Sección de Búsqueda
st.subheader("🔍 Buscar Dueños")
search_name = st.text_input("Buscar por Nombre")
search_dni = st.text_input("Buscar por DNI")

if search_name or search_dni:
    filtered_owners = [
        owner for owner in owners
        if (search_name.lower() in owner["nombre"].lower() if search_name else True) and
           (search_dni in owner["dni"] if search_dni else True)
    ]
    if filtered_owners:
        st.write("📊 Resultados de la búsqueda:")
        st.dataframe(
            pd.DataFrame(filtered_owners),
            column_config={
                "id": st.column_config.Column("ID", width="small"),
                "nombre": st.column_config.Column("Nombre", width="medium"),
                "dni": st.column_config.Column("DNI", width="medium"),
                "direccion": st.column_config.Column("Dirección", width="large"),
                "telefono": st.column_config.Column("Teléfono", width="medium"),
                "correo_electronico": st.column_config.Column("Email", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("ℹ️ No se encontraron dueños que coincidan con los criterios de búsqueda.")