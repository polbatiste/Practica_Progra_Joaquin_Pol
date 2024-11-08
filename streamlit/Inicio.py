import streamlit as st
import time

st.set_page_config(page_title='Veterinaria Mentema', layout='wide',     page_icon="🩺")
st.image('logo.jpg') 

placeholder = st.empty()
with placeholder:
    for seconds in range(10):
        placeholder.write(f"⏳ {seconds} Cargando sistema de gestión veterinaria")
        time.sleep(1)
placeholder.empty()

st.write("# Bienvenido al Sistema de Gestión de la Clínica Veterinaria 🐶🐱")

st.sidebar.success("Selecciona una página para gestionar las funciones del sistema.")

st.markdown(
    """
    Este sistema de gestión veterinaria está diseñado para facilitar las operaciones diarias de la clínica, basado en una arquitectura modular con microservicios. 
    Las funcionalidades principales se dividen en varias páginas:

    1. **Dashboard**: Visualización de estadísticas clave y datos importantes de la clínica veterinaria, como el número de citas, tratamientos realizados y productos en inventario.

    2. **Citas**: Gestiona las citas de los clientes, incluyendo programación, actualización y cancelación de citas. Permite asignar consultas y visualizar el calendario.

    3. **Calendario**: Muestra un calendario interactivo para visualizar y gestionar las citas. Puedes agregar, modificar y eliminar citas directamente desde esta vista.

    4. **Dueños**: Lleva un registro completo de los dueños, con opciones para agregar, actualizar y buscar información sobre los propietarios de las mascotas.

    5. **Animales**: Administra la información de las mascotas, con detalles como especie, raza, edad y dueño. Permite registrar y actualizar datos de cada mascota.

    6. **Tratamientos**: Gestiona los tratamientos disponibles en la clínica, con opciones para agregar, actualizar y eliminar tratamientos. Conecta con una base de datos no relacional para su administración.

    7. **Productos**: Control de inventario de productos veterinarios, con funcionalidades para añadir, actualizar, vender productos y gestionar el stock de la clínica.

    ¡Explora el sistema y asegúrate de que cada módulo funcione a la perfección! 🐾🩺🐱
    """
)
