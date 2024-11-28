import pandas as pd
import streamlit as st
import plotly.express as px
import requests

@st.cache_data
def load_data(url: str):
    # Función para cargar datos desde una API y convertirlos en DataFrame
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return pd.DataFrame(r.json())

def info_box(text):
    # Caja de información con estilo
    st.markdown(
        f'<div style="background-color:#4EBAE1;opacity:70%"><p style="text-align:center;color:white;font-size:30px;">{text}</p></div>',
        unsafe_allow_html=True
    )

# Cargar datos desde las rutas de la API
df_appointments = load_data('http://app:8000/api/v1/appointments')  # Citas
df_animals = load_data('http://app:8000/api/v1/animals')  # Animales

# Verificación de carga de datos y conteo
total_citas, total_clientes, total_animales = '0', '0', '0'

if df_appointments is not None and not df_appointments.empty:
    if {'owner_id', 'animal_id'}.issubset(df_appointments.columns):
        total_citas = str(df_appointments.shape[0])
        total_clientes = str(df_appointments['owner_id'].nunique())
    else:
        st.error("El DataFrame de citas no contiene las columnas esperadas. Verifique la respuesta de la API.")
else:
    st.error("No se pudieron cargar los datos de citas o el DataFrame está vacío.")

if df_animals is not None and not df_animals.empty:
    total_animales = str(df_animals.shape[0])
else:
    st.error("No se pudieron cargar los datos de animales o el DataFrame está vacío.")

# Título y cabecera del dashboard
st.title("Dashboard de la Clínica Veterinaria")
st.header("Información general")

# Visualización de totales
col1, col2, col3 = st.columns(3)
col1.subheader('Total citas')
info_box(total_citas)
col2.subheader('Total clientes')
info_box(total_clientes)
col3.subheader('Total animales')
info_box(total_animales)

# Tabs de gráficos
tab1, tab2, tab3 = st.tabs(["Distribución de citas", "Análisis de citas", "Análisis de animales"])

# Gráficos
if df_appointments is not None and not df_appointments.empty:
    fig1 = px.scatter(df_appointments, x='id', y='date', color='treatment', title="Citas por tratamiento")
    fig2 = px.histogram(df_appointments, x='date', title="Distribución de citas por fecha")
    
    with tab1:
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
    with tab2:
        st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico de barras para citas por tratamiento
    st.subheader("Citas por Tratamiento")
    treatment_counts = df_appointments['treatment'].value_counts()
    fig_treatment = px.bar(treatment_counts, x=treatment_counts.index, y=treatment_counts.values, labels={'x': 'Tratamiento', 'y': 'Número de Citas'}, title="Número de Citas por Tratamiento")
    st.plotly_chart(fig_treatment, use_container_width=True)

else:
    st.info("No hay datos suficientes para mostrar los gráficos.")

# Gráfico de pastel para distribución de especies de animales
if df_animals is not None and not df_animals.empty:
    with tab3:
        st.subheader("Distribución de Especies de Animales")
        species_counts = df_animals['species'].value_counts()
        fig_species = px.pie(species_counts, names=species_counts.index, values=species_counts.values, title="Distribución de Especies de Animales")
        st.plotly_chart(fig_species, use_container_width=True)
else:
    st.info("No hay datos suficientes para mostrar los gráficos de animales.")