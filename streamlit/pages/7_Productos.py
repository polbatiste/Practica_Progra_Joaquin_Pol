import streamlit as st
import requests

API_URL = "http://app:8000/api/v1/productos"

st.title("Gestión de Productos - Clínica Veterinaria")

# Función para obtener todos los productos
def get_productos():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al cargar los productos")
        return []

# Función para crear un nuevo producto
def create_producto(categoria, marca, nombre, descripcion, precio, stock):
    data = {"categoria": categoria, "marca": marca, "nombre": nombre, "descripcion": descripcion, "precio": precio, "stock": stock}
    response = requests.post(API_URL, json=data)
    if response.status_code == 201:
        st.success("Producto añadido exitosamente")
    else:
        st.error("Error al añadir el producto")

# Función para actualizar el precio de un producto
def update_precio_producto(nombre, precio):
    response = requests.put(f"{API_URL}/{nombre}", json={"precio": precio})
    if response.status_code == 200:
        st.success("Precio actualizado exitosamente")
    else:
        st.error("Error al actualizar el precio")

# Función para eliminar un producto
def delete_producto(nombre):
    response = requests.delete(f"{API_URL}/{nombre}")
    if response.status_code == 200:
        st.success("Producto eliminado exitosamente")
    else:
        st.error("Error al eliminar el producto")

# Función para actualizar el stock de un producto
def update_stock_producto(nombre, cantidad):
    response = requests.post(f"{API_URL}/stock/{nombre}", json={"cantidad": cantidad})
    if response.status_code == 200:
        st.success("Stock actualizado exitosamente")
    else:
        st.error("Error al actualizar el stock")

# Función para buscar productos
def buscar_productos(nombre=None, categoria=None):
    params = {}
    if nombre:
        params["nombre"] = nombre
    if categoria:
        params["categoria"] = categoria
    response = requests.get(f"{API_URL}/busqueda", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al buscar productos")
        return []

# Función para vender un producto
def vender_producto(nombre, cantidad):
    response = requests.post(f"{API_URL}/venta/{nombre}", json={"cantidad": cantidad})
    if response.status_code == 200:
        factura = response.json()
        st.success(f"Venta realizada exitosamente. Factura: {factura}")
    else:
        st.error("Error al realizar la venta")

# Sección de búsqueda de productos
st.subheader("Buscar Productos")
nombre_busqueda = st.text_input("Buscar por Nombre")
categoria_busqueda = st.text_input("Buscar por Categoría")
if st.button("Buscar"):
    resultados_busqueda = buscar_productos(nombre=nombre_busqueda, categoria=categoria_busqueda)
    if resultados_busqueda:
        st.write("Resultados de la búsqueda:")
        st.table(resultados_busqueda)
    else:
        st.info("No se encontraron productos que coincidan con los criterios de búsqueda.")

# Sección para vender un producto
st.subheader("Vender Producto")
nombre_venta = st.selectbox("Seleccione un producto para vender", [p["nombre"] for p in get_productos()])
cantidad_venta = st.number_input("Cantidad a vender", min_value=1, step=1)
if st.button("Realizar Venta"):
    vender_producto(nombre_venta, cantidad_venta)