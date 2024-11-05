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

# Cargar los datos desde la ruta de tu servidor FastAPI
df_merged = load_data('http://app:8000/api/v1/appointments')  # Ruta ajustada para el router de citas

if df_merged is not None and not df_merged.empty:
    # Verificar si las columnas existen antes de usarlas
    if 'client_name' in df_merged.columns and 'pet_name' in df_merged.columns:
        # Información general para la clínica veterinaria
        total_citas = str(df_merged.shape[0])
        total_clientes = str(len(df_merged['client_name'].unique()))
        total_animales = str(len(df_merged['pet_name'].unique()))
    else:
        st.error("El DataFrame no contiene las columnas esperadas. Verifique la respuesta de la API.")
        total_citas = total_clientes = total_animales = '0'
else:
    st.error("No se pudieron cargar los datos o el DataFrame está vacío.")
    total_citas = total_clientes = total_animales = '0'

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
if df_merged is not None and not df_merged.empty:
    fig1 = px.scatter(df_merged, x='pet_name', y='date', color='treatment', title="Citas por tratamiento")
    fig2 = px.histogram(df_merged, x='date', title="Distribución de citas por fecha")

    with tab1:
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
    with tab2:
        st.plotly_chart(fig2, theme=None, use_container_width=True)
else:
    st.info("No hay datos suficientes para mostrar los gráficos.")