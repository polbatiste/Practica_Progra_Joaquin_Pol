import streamlit as st
import time

# Configuración de la página de Streamlit
st.set_page_config(page_title='Veterinaria Mentema', layout='wide', page_icon="🩺")
st.image('logo.jpg')  # Mostrar el logo de la clínica

# Mensaje de carga con un temporizador
placeholder = st.empty()
with placeholder:
    for seconds in range(10):
        placeholder.write(f"⏳ {seconds} Cargando sistema de gestión veterinaria")
        time.sleep(1)
placeholder.empty()

# Bienvenida al sistema de gestión veterinaria
st.write("# Bienvenido al Sistema de Gestión de la Clínica Veterinaria 🐶🐱")
st.sidebar.success("Selecciona una página para gestionar las funciones del sistema.")

# Descripción de las funcionalidades del sistema
st.markdown(
    """
    Este sistema de gestión veterinaria facilita las operaciones diarias de la clínica y se organiza en varias secciones:

    1. **Dashboard**: Visualización de estadísticas clave y datos de la clínica, como el número de citas y productos en inventario.
    2. **Citas**: Gestión de citas de clientes, incluyendo programación, actualización y cancelación.
    3. **Calendario**: Vista interactiva del calendario para gestionar citas.
    4. **Dueños**: Registro y búsqueda de información sobre los dueños de las mascotas.
    5. **Animales**: Información de mascotas, incluyendo especie, raza, edad y dueño.
    6. **Tratamientos**: Administración de tratamientos disponibles, conectados a una base de datos no relacional.
    7. **Productos**: Control de inventario de productos veterinarios, incluyendo la gestión de stock y ventas.

    ¡Explora el sistema y asegura el buen funcionamiento de cada módulo! 🐾🩺
    """
)