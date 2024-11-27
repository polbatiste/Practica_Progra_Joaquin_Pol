import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria - Gestión de Inventario",
    page_icon="🏥",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        background-color: #2c3e50;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > input {
        border-radius: 4px;
    }
    h1 {
        color: #2c3e50;
        padding-bottom: 1rem;
        border-bottom: 2px solid #eee;
    }
    h2 {
        color: #34495e;
        margin-top: 2rem;
    }
    .success {
        padding: 1rem;
        border-radius: 4px;
        background-color: #d4edda;
        color: #155724;
    }
    .error {
        padding: 1rem;
        border-radius: 4px;
        background-color: #f8d7da;
        color: #721c24;
    }
    .warning {
        padding: 1rem;
        border-radius: 4px;
        background-color: #fff3cd;
        color: #856404;
    }
    .table-container {
        margin: 2rem 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .price-column {
        text-align: right !important;
        font-family: monospace;
    }
    .stock-warning {
        color: #dc3545;
        font-weight: bold;
    }
    .stock-ok {
        color: #28a745;
    }
    </style>
""", unsafe_allow_html=True)

# URLs de la API
API_URL = "http://app:8000/api/v1/productos"
API_FACTURAS_URL = "http://app:8000/api/v1/facturas"

st.title("Sistema de Gestión de Inventario")

# Funciones de utilidad
def get_productos():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            productos = response.json()
            for producto in productos:
                producto["precio"] = f"{producto['precio']:.2f} €"
                producto["stock_status"] = "stock-ok" if producto['stock'] > 10 else "stock-warning"
            return pd.DataFrame(productos).rename(columns=str.capitalize)
        else:
            st.error("Error de conexión: No se pudo cargar el inventario")
            return pd.DataFrame()
    except:
        st.error("Error de conexión con el servidor")
        return pd.DataFrame()

def create_producto(categoria, marca, nombre, descripcion, precio, stock):
    data = {
        "categoria": categoria,
        "marca": marca,
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "stock": stock
    }
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 201:
            st.success("Producto registrado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error("Error en el registro del producto")
    except:
        st.error("Error de conexión con el servidor")

def update_precio_producto(nombre, precio):
    try:
        response = requests.put(f"{API_URL}/precio/{nombre}", json={"precio": precio})
        if response.status_code == 200:
            st.success("Precio actualizado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error en la actualización: {response.json().get('detail')}")
    except:
        st.error("Error de conexión con el servidor")

def update_stock_producto(nombre, stock):
    try:
        response = requests.put(f"{API_URL}/stock/{nombre}", json={"stock": stock})
        if response.status_code == 200:
            st.success("Inventario actualizado exitosamente")
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error en la actualización: {response.json().get('detail')}")
    except:
        st.error("Error de conexión con el servidor")

def vender_producto(nombre, cantidad):
    try:
        response = requests.post(f"{API_URL}/venta/{nombre}", json={"cantidad": cantidad})
        if response.status_code == 200:
            factura = response.json()
            st.success("Venta registrada exitosamente")
            with st.expander("Ver Detalle de Factura"):
                st.json(factura)
            st.write('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
        else:
            st.error(f"Error en la transacción: {response.json().get('detail')}")
    except:
        st.error("Error de conexión con el servidor")

def get_historial_facturas():
    try:
        response = requests.get(API_FACTURAS_URL)
        if response.status_code == 200:
            facturas = response.json()
            df_facturas = pd.DataFrame(facturas)
            if "nombre_producto" in df_facturas.columns and "precio_total" in df_facturas.columns:
                df_facturas["precio_total"] = df_facturas["precio_total"].apply(lambda x: f"{x:.2f} €")
                df_facturas.rename(columns={
                    "nombre_producto": "Producto",
                    "precio_total": "Total",
                    "cantidad": "Cantidad",
                    "fecha": "Fecha"
                }, inplace=True)
                return df_facturas[["Fecha", "Producto", "Cantidad", "Total"]]
            return pd.DataFrame()
    except:
        st.error("Error de conexión con el servidor")
        return pd.DataFrame()

# Crear tabs para mejor organización
tab1, tab2, tab3, tab4 = st.tabs(["Inventario", "Gestión de Productos", "Ventas", "Historial"])

with tab1:
    st.header("Inventario Actual")
    
    # Búsqueda de productos
    col1, col2 = st.columns(2)
    with col1:
        buscar_nombre = st.text_input("Buscar por Nombre")
    with col2:
        buscar_categoria = st.text_input("Buscar por Categoría")
    
    productos_df = get_productos()
    if not productos_df.empty:
        # Filtrar si hay términos de búsqueda
        if buscar_nombre or buscar_categoria:
            mask = pd.Series(True, index=productos_df.index)
            if buscar_nombre:
                mask &= productos_df['Nombre'].str.contains(buscar_nombre, case=False)
            if buscar_categoria:
                mask &= productos_df['Categoria'].str.contains(buscar_categoria, case=False)
            productos_df = productos_df[mask]
        
        st.dataframe(
            productos_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Stock": st.column_config.NumberColumn(
                    "Stock",
                    help="Cantidad disponible en inventario",
                    format="%d"
                ),
                "Precio": st.column_config.Column(
                    "Precio",
                    width="medium"
                )
            }
        )
    else:
        st.info("No hay productos registrados en el sistema")

with tab2:
    st.header("Gestión de Productos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Registro de Productos")
        with st.form("producto_form", clear_on_submit=True):
            categoria = st.text_input("Categoría")
            marca = st.text_input("Marca")
            nombre = st.text_input("Nombre del Producto")
            descripcion = st.text_area("Descripción")
            precio = st.number_input("Precio (€)", min_value=0.0, step=0.01, format="%.2f")
            stock = st.number_input("Stock Inicial", min_value=0, step=1)
            
            if st.form_submit_button("Registrar Producto"):
                if all([categoria, marca, nombre, descripcion, precio >= 0]):
                    create_producto(categoria, marca, nombre, descripcion, precio, stock)
                else:
                    st.error("Todos los campos son obligatorios")
    
    with col2:
        if not productos_df.empty:
            st.subheader("Actualización de Precios")
            with st.form("precio_form", clear_on_submit=True):
                nombre_producto = st.selectbox(
                    "Seleccionar Producto",
                    options=productos_df["Nombre"].tolist()
                )
                nuevo_precio = st.number_input(
                    "Nuevo Precio (€)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f"
                )
                if st.form_submit_button("Actualizar Precio"):
                    if nuevo_precio >= 0:
                        update_precio_producto(nombre_producto, nuevo_precio)
                    else:
                        st.error("El precio debe ser mayor o igual a 0")

            st.subheader("Gestión de Stock")
            with st.form("stock_form", clear_on_submit=True):
                nombre_stock = st.selectbox(
                    "Seleccionar Producto",
                    options=productos_df["Nombre"].tolist(),
                    key="stock_select"
                )
                stock_cantidad = st.number_input(
                    "Cantidad a Añadir",
                    min_value=1,
                    step=1
                )
                if st.form_submit_button("Actualizar Stock"):
                    update_stock_producto(nombre_stock, stock_cantidad)

with tab3:
    st.header("Registro de Ventas")
    if not productos_df.empty:
        with st.form("venta_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_venta = st.selectbox(
                    "Seleccionar Producto",
                    options=productos_df["Nombre"].tolist()
                )
            
            with col2:
                cantidad_venta = st.number_input(
                    "Cantidad",
                    min_value=1,
                    step=1
                )
            
            if st.form_submit_button("Procesar Venta"):
                vender_producto(nombre_venta, cantidad_venta)

with tab4:
    st.header("Historial de Transacciones")
    facturas_df = get_historial_facturas()
    if not facturas_df.empty:
        st.dataframe(
            facturas_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total": st.column_config.Column(
                    "Total",
                    width="medium"
                ),
                "Fecha": st.column_config.DatetimeColumn(
                    "Fecha",
                    format="DD/MM/YYYY HH:mm"
                )
            }
        )
    else:
        st.info("No hay transacciones registradas")