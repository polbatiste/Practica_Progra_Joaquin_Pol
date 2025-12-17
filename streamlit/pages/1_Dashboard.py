import pandas as pd
import streamlit as st
import plotly.express as px
import requests

@st.cache_data
def load_data(url: str):

    try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()

            return pd.DataFrame(r.json())
    except Exception as e:
            st.error(f"Error conectando a la API: {e}")

    return pd.DataFrame()  # Devuelve un DataFrame vacío en lugar de None

# Configurar el dashboard para que use el ancho completo de la pantalla
st.set_page_config(page_title="VetControl Dashboard", page_icon="🐾", layout="wide")
# Cambiamos 'app' por 'localhost' para ejecución local fuera de Docker
df_appointments = load_data('http://localhost:8000/api/v1/appointments')
df_animals = load_data('http://localhost:8000/api/v1/animals')

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

# Visualización de totales mejorada con st.metric
st.divider()
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="📅 Total Citas", value=total_citas)
kpi2.metric(label="👥 Total Clientes", value=total_clientes)
kpi3.metric(label="🐾 Total Animales", value=total_animales)
st.divider()

# Tabs de gráficos
tab1, tab2, tab3, tab4 = st.tabs(["Distribución de citas", "Análisis de citas", "Análisis de animales", "Animales por Tratamiento"])

# Lógica de gráficos dentro de sus pestañas correspondientes
if df_appointments is not None and not df_appointments.empty:
     with tab1:
         fig2 = px.histogram(df_appointments, x='date', title="Frecuencia de Citas por Fecha", color_discrete_sequence=['#4EBAE1'])
         st.plotly_chart(fig2, use_container_width=True)

     with tab2:
         treatment_counts = df_appointments['treatment'].value_counts()
         fig_treatment = px.bar(treatment_counts, x=treatment_counts.index, y=treatment_counts.values,
                               color=treatment_counts.values, color_continuous_scale='Blues',
                               title="Demanda por Tipo de Tratamiento")
         st.plotly_chart(fig_treatment, use_container_width=True)

     with tab4:
         animal_treatment_counts = df_appointments.groupby('treatment')['animal_id'].nunique().reset_index()
         fig_animal_treatment = px.bar(animal_treatment_counts, x='treatment', y='animal_id',
                                      title="Diversidad de Animales Únicos por Tratamiento",
                                      color_discrete_sequence=['#FF8C00'])
         st.plotly_chart(fig_animal_treatment, use_container_width=True)

else:
    st.info("No hay datos suficientes para mostrar los gráficos.")

#Grafico de pastel actualizado:
if df_animals is not None and not df_animals.empty:
     with tab3:
         species_counts = df_animals['species'].value_counts()
         # Se cambia a formato "Donut" para mayor elegancia
         fig_species = px.pie(species_counts, names=species_counts.index, values=species_counts.values,
                             hole=0.5, title="Composición de la Población por Especie",
                             color_discrete_sequence=px.colors.qualitative.Safe)
         st.plotly_chart(fig_species, use_container_width=True)
else:
    st.info("No hay datos suficientes para mostrar los gráficos de animales.")