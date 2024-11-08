import streamlit as st
import requests
import pandas as pd

API_URL = "http://app:8000/api/v1/productos"

st.title("Gestión de Productos - Clínica Veterinaria")

# Función para obtener todos los productos y formatear los datos
def get_productos():
    response = requests.get(API_URL)
    if response.status_code == 200:
        productos = response.json()
        for producto in productos:
            producto["precio"] = f"{producto['precio']:.2f} €"
        df_productos = pd.DataFrame(productos)
        df_productos.columns = [col.capitalize() for col in df_productos.columns]
        return df_productos
    else:
        st.error("Error al cargar los productos")
        return pd.DataFrame()

# Función para crear un nuevo producto
def create_producto(categoria, marca, nombre, descripcion, precio, stock):
    data = {"categoria": categoria, "marca": marca, "nombre": nombre, "descripcion": descripcion, "precio": precio, "stock": stock}
    response = requests.post(API_URL, json=data)
    if response.status_code == 201:
        st.success("Producto añadido exitosamente")
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
    else:
        st.error("Error al añadir el producto")

# Función para actualizar el precio de un producto
def update_precio_producto(nombre, precio):
    response = requests.put(f"{API_URL}/precio/{nombre}", json={"precio": precio})  # Endpoint específico para precio
    if response.status_code == 200:
        st.success("Precio actualizado exitosamente")
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
    else:
        st.error(f"Error al actualizar el precio: {response.json().get('detail')}")

# Función para actualizar el stock de un producto
def update_stock_producto(nombre, stock):
    response = requests.put(f"{API_URL}/stock/{nombre}", json={"stock": stock})
    if response.status_code == 200:
        st.success("Stock actualizado exitosamente")
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
    else:
        st.error(f"Error al actualizar el stock: {response.json().get('detail')}")

# Función para vender un producto
def vender_producto(nombre, cantidad):
    response = requests.post(f"{API_URL}/venta/{nombre}", json={"cantidad": cantidad})
    if response.status_code == 200:
        factura = response.json()
        st.success("Venta realizada exitosamente")
        st.write("Factura:")
        st.json(factura)
        st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)  # Recargar la página automáticamente
    else:
        st.error(f"Error al realizar la venta: {response.json().get('detail')}")

# Función para buscar productos por nombre o categoría
def buscar_productos(nombre=None, categoria=None):
    params = {}
    if nombre:
        params["nombre"] = nombre
    if categoria:
        params["categoria"] = categoria

    response = requests.get(f"{API_URL}/busqueda", params=params)
    if response.status_code == 200:
        productos = response.json()
        for producto in productos:
            producto["precio"] = f"{producto['precio']:.2f} €"
        return pd.DataFrame(productos).rename(columns=str.capitalize)
    else:
        st.error("Error al buscar productos")
        return pd.DataFrame()

# Mostrar todos los productos en una tabla
st.subheader("Productos Registrados")
productos_df = get_productos()
if not productos_df.empty:
    st.table(productos_df)

# Formulario para añadir un nuevo producto
st.subheader("Añadir Producto")
with st.form("producto_form"):
    categoria = st.text_input("Categoría")
    marca = st.text_input("Marca")
    nombre = st.text_input("Nombre")
    descripcion = st.text_area("Descripción")
    precio = st.number_input("Precio", min_value=0.0, step=0.01)
    stock = st.number_input("Stock inicial", min_value=0, step=1)
    if st.form_submit_button("Añadir Producto"):
        create_producto(categoria, marca, nombre, descripcion, precio, stock)

# Formulario para actualizar el precio de un producto existente
st.subheader("Modificar Precio de Producto")
if not productos_df.empty:
    nombre_producto = st.selectbox("Seleccione un producto", productos_df["Nombre"])
    nuevo_precio = st.number_input("Nuevo Precio", min_value=0.0, step=0.01)
    if st.button("Actualizar Precio"):
        update_precio_producto(nombre_producto, nuevo_precio)

# Formulario para actualizar el stock de un producto existente
st.subheader("Actualizar Stock de Producto")
if not productos_df.empty:
    nombre_stock = st.selectbox("Seleccione un producto para actualizar stock", productos_df["Nombre"])
    stock_cantidad = st.number_input("Cantidad a añadir al stock", min_value=1, step=1)
    if st.button("Actualizar Stock"):
        update_stock_producto(nombre_stock, stock_cantidad)

# Formulario para vender un producto
st.subheader("Vender Producto")
if not productos_df.empty:
    nombre_venta = st.selectbox("Seleccione un producto para vender", productos_df["Nombre"])
    cantidad_venta = st.number_input("Cantidad a vender", min_value=1, step=1)
    if st.button("Realizar Venta"):
        vender_producto(nombre_venta, cantidad_venta)

# Formulario para buscar productos por nombre o categoría
st.subheader("Buscar Producto")
buscar_nombre = st.text_input("Buscar por Nombre")
buscar_categoria = st.text_input("Buscar por Categoría")
if st.button("Buscar"):
    productos_buscados = buscar_productos(buscar_nombre, buscar_categoria)
    if not productos_buscados.empty:
        st.table(productos_buscados)
    else:
        st.info("No se encontraron productos con los criterios de búsqueda.")