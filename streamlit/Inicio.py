import streamlit as st
import time
import os

# Configuración de la página
st.set_page_config(
    page_title='Clínica Veterinaria Mentema',
    page_icon="🏥",
    layout='wide',
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    h1 {
        color: #2c3e50;
        padding-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        text-align: center;
        margin-bottom: 2rem;
    }
    .module-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid;
        transition: transform 0.2s;
    }
    .module-card:hover {
        transform: translateY(-5px);
    }
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: rgba(255,255,255,0.9);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
    }
    .progress-bar {
        width: 300px;
        height: 20px;
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress {
        height: 100%;
        background-color: #3498db;
        transition: width 0.5s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Animación de carga inicial
placeholder = st.empty()
for i in range(8):
    with placeholder.container():
        progress = (i + 1) * 12.5
        st.markdown(f"""
            <div class="loading-container">
                <h2>Iniciando Sistema Veterinario</h2>
                <div class="progress-bar">
                    <div class="progress" style="width: {progress}%"></div>
                </div>
                <p>Cargando módulos... {int(progress)}%</p>
            </div>
        """, unsafe_allow_html=True)
    time.sleep(1)
placeholder.empty()

# Logo y título
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image('logo.jpg', use_column_width=True)

st.title("Sistema Integral de Gestión Veterinaria")

# Descripción de las páginas
modules = [
    {
        "title": "Dashboard",
        "icon": "📊",
        "description": "Panel de control principal que muestra métricas clave de la clínica, incluyendo número de pacientes, citas programadas, ingresos diarios y estado del inventario.",
        "color": "#3498db"
    },
    {
        "title": "Gestión de Citas",
        "icon": "📅",
        "description": "Sistema completo para gestionar citas médicas. Permite programar, modificar y cancelar citas, con vista de disponibilidad por veterinario y consulta.",
        "color": "#2ecc71"
    },
    {
        "title": "Calendario",
        "icon": "📆",
        "description": "Vista general del calendario de la clínica. Muestra todas las citas programadas, disponibilidad de consultas y permite la gestión visual de horarios.",
        "color": "#9b59b6"
    },
    {
        "title": "Gestión de Propietarios",
        "icon": "👥",
        "description": "Gestión completa de datos de propietarios. Incluye información de contacto, historial de visitas y registro de mascotas asociadas.",
        "color": "#34495e"
    },
    {
        "title": "Gestión de Pacientes",
        "icon": "🐾",
        "description": "Control de historias clínicas de pacientes, incluyendo historial médico, vacunaciones, tratamientos y seguimiento de evolución.",
        "color": "#e67e22"
    },
    {
        "title": "Tratamientos",
        "icon": "💊",
        "description": "Catálogo completo de tratamientos disponibles con precios, duraciones y protocolos médicos asociados.",
        "color": "#e74c3c"
    },
    {
        "title": "Inventario",
        "icon": "📦",
        "description": "Control de inventario de medicamentos y productos veterinarios. Gestión de stock, alertas de reposición y registro de ventas.",
        "color": "#f1c40f"
    },
    {
        "title": "Facturación",
        "icon": "📑",
        "description": "Sistema de facturación integrado. Genera facturas automáticas, gestiona pagos y mantiene un registro completo de transacciones.",
        "color": "#16a085"
    }
]

# Mostrar módulos en grid
for i in range(0, len(modules), 2):
    col1, col2 = st.columns(2)
    
    with col1:
        if i < len(modules):
            st.markdown(f"""
                <div class="module-card" style="border-left-color: {modules[i]['color']}">
                    <h3>{modules[i]['icon']} {modules[i]['title']}</h3>
                    <p>{modules[i]['description']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if i + 1 < len(modules):
            st.markdown(f"""
                <div class="module-card" style="border-left-color: {modules[i+1]['color']}">
                    <h3>{modules[i+1]['icon']} {modules[i+1]['title']}</h3>
                    <p>{modules[i+1]['description']}</p>
                </div>
            """, unsafe_allow_html=True)

# Información de contacto
st.markdown("""
    <div class="module-card" style="border-left-color: #7f8c8d">
        <h3>ℹ️ Información de Contacto</h3>
        <ul>
            <li><strong>Horario:</strong> Lunes a Sábado de 9:00 a 20:00</li>
            <li><strong>Urgencias:</strong> Servicio 24/7</li>
            <li><strong>Email:</strong> info@clinicaveterinaria.com</li>
            <li><strong>Teléfono:</strong> +34 900 123 456</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# Pie de página
st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px; color: #7f8c8d;">
        <p>© 2024 Clínica Veterinaria Mentema - Todos los derechos reservados</p>
    </div>
""", unsafe_allow_html=True)