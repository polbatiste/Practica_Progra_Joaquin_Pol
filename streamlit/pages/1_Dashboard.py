import pandas as pd
import streamlit as st
import plotly.express as px
import requests
import seaborn as sns

@st.cache_data
def load_data(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    # Adaptación para convertir la lista de citas a un DataFrame
    df = pd.DataFrame(data)
    return df

def info_box(text, color=None):
    st.markdown(f'<div style="background-color:#4EBAE1;opacity:70%"><p style="text-align:center;color:white;font-size:30px;">{text}</p></div>', unsafe_allow_html=True)

# Cargar los datos desde la ruta de tu servidor FastAPI para citas y animales
df_appointments = load_data('http://app:8000/api/v1/appointments')  # Ruta para citas
df_animals = load_data('http://app:8000/api/v1/animals')  # Ruta para animales

if df_appointments is not None and not df_appointments.empty:
    # Verificar si las columnas existen antes de usarlas
    if 'client_name' in df_appointments.columns and 'pet_name' in df_appointments.columns:
        # Información general para la clínica veterinaria
        total_citas = str(df_appointments.shape[0])
        total_clientes = str(len(df_appointments['client_name'].unique()))
    else:
        st.error("El DataFrame de citas no contiene las columnas esperadas. Verifique la respuesta de la API.")
        total_citas = total_clientes = '0'
else:
    st.error("No se pudieron cargar los datos de citas o el DataFrame está vacío.")
    total_citas = total_clientes = '0'

# Calcular total de animales
if df_animals is not None and not df_animals.empty:
    total_animales = str(df_animals.shape[0])
else:
    st.error("No se pudieron cargar los datos de animales o el DataFrame está vacío.")
    total_animales = '0'

sns.set_palette("pastel")

st.title("Dashboard de la Clínica Veterinaria")

st.header("Información general")

col1, col2, col3 = st.columns(3)

with col1:
    col1.subheader('Total citas')
    info_box(total_citas)
with col2:
    col2.subheader('Total clientes')
    info_box(total_clientes)
with col3:
    col3.subheader('Total animales')
    info_box(total_animales)

tab1, tab2 = st.tabs(["Distribución de citas", "Análisis de citas"])

# Personalizar los gráficos según tus necesidades
if df_appointments is not None and not df_appointments.empty:
    fig1 = px.scatter(df_appointments, x='pet_name', y='date', color='treatment', title="Citas por tratamiento")
    fig2 = px.histogram(df_appointments, x='date', title="Distribución de citas por fecha")

    with tab1:
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
    with tab2:
        st.plotly_chart(fig2, theme=None, use_container_width=True)
else:
    st.info("No hay datos suficientes para mostrar los gráficos.")
