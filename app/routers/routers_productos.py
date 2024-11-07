from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from datetime import datetime

# Conexión con MongoDB
MONGO_URI = "mongodb://root:example@mongodb:27017/?authSource=admin"
client = MongoClient(MONGO_URI)
db = client.clinica_veterinaria
coleccion_productos = db.productos
coleccion_facturas = db.facturas  # Nueva colección para almacenar las facturas

router = APIRouter()

# Modelos de producto y factura
class Producto(BaseModel):
    categoria: str
    marca: str
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int

class Factura(BaseModel):
    nombre_producto: str
    cantidad: int
    precio_total: float
    fecha: datetime

# Modelos para actualizar precio, stock y realizar venta
class ActualizarPrecio(BaseModel):
    precio: float

class ActualizarStock(BaseModel):
    stock: int

class VenderProducto(BaseModel):
    cantidad: int

# Función para poblar la colección con productos iniciales
def poblar_productos_iniciales():
    productos_iniciales = [
        {"categoria": "Vitaminas", "marca": "PetVita", "nombre": "Vitamina A+", "descripcion": "Suplemento de vitamina A para animales", "precio": 10.0, "stock": 100},
        {"categoria": "Cremas analgésicas", "marca": "PetCare", "nombre": "Crema Analgésica", "descripcion": "Crema para aliviar el dolor en animales", "precio": 20.0, "stock": 50},
        {"categoria": "Desparasitador", "marca": "SafePet", "nombre": "Desparasitador Plus", "descripcion": "Desparasitador de amplio espectro para perros", "precio": 15.0, "stock": 200},
        {"categoria": "Productos de belleza", "marca": "AnimalLook", "nombre": "Champú para perros", "descripcion": "Champú suave para el cuidado del pelaje", "precio": 12.0, "stock": 80}
    ]

    if coleccion_productos.count_documents({}) == 0:
        coleccion_productos.insert_many(productos_iniciales)

# Llamar a la función de población inicial
poblar_productos_iniciales()

@router.post("/productos", response_model=Producto)
def crear_producto(producto: Producto):
    if coleccion_productos.find_one({"nombre": producto.nombre}):
        raise HTTPException(status_code=400, detail="El producto ya existe")
    coleccion_productos.insert_one(producto.dict())
    return producto

@router.get("/productos", response_model=List[Producto])
def listar_productos():
    productos = list(coleccion_productos.find({}, {"_id": 0}))
    return productos

# Endpoint para actualizar el precio de un producto
@router.put("/productos/precio/{nombre}", response_model=Producto)
def actualizar_precio_producto(nombre: str, actualizar: ActualizarPrecio):
    resultado = coleccion_productos.update_one({"nombre": nombre}, {"$set": {"precio": actualizar.precio}})
    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado o sin cambios")
    producto_actualizado = coleccion_productos.find_one({"nombre": nombre}, {"_id": 0})
    return producto_actualizado

# Endpoint para actualizar el stock de un producto
@router.put("/productos/stock/{nombre}")
def actualizar_stock_producto(nombre: str, actualizar: ActualizarStock):
    producto = coleccion_productos.find_one({"nombre": nombre})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    nuevo_stock = producto["stock"] + actualizar.stock
    resultado = coleccion_productos.update_one({"nombre": nombre}, {"$set": {"stock": nuevo_stock}})
    
    if resultado.modified_count == 0:
        raise HTTPException(status_code=500, detail="Error al actualizar el stock")

    return {"nombre": nombre, "stock": nuevo_stock}

@router.delete("/productos/{nombre}")
def eliminar_producto(nombre: str):
    resultado = coleccion_productos.delete_one({"nombre": nombre})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado exitosamente"}

# Endpoint para buscar productos por nombre o categoría
@router.get("/productos/busqueda", response_model=List[Producto])
def buscar_productos(nombre: Optional[str] = None, categoria: Optional[str] = None):
    filtro = {}
    if nombre:
        filtro["nombre"] = {"$regex": nombre, "$options": "i"}
    if categoria:
        filtro["categoria"] = {"$regex": categoria, "$options": "i"}
    productos = list(coleccion_productos.find(filtro, {"_id": 0}))
    return productos

# Endpoint para vender un producto
@router.post("/productos/venta/{nombre}", response_model=Factura)
def vender_producto(nombre: str, venta: VenderProducto):
    producto = coleccion_productos.find_one({"nombre": nombre})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto["stock"] < venta.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    nuevo_stock = producto["stock"] - venta.cantidad
    coleccion_productos.update_one({"nombre": nombre}, {"$set": {"stock": nuevo_stock}})

    precio_total = producto["precio"] * venta.cantidad
    factura = {
        "nombre_producto": producto["nombre"],
        "cantidad": venta.cantidad,
        "precio_total": precio_total,
        "fecha": datetime.now()
    }
    coleccion_facturas.insert_one(factura)  # Guardar la factura en la base de datos

    return factura