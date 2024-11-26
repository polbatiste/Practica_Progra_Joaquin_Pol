# app/server.py

from fastapi import FastAPI
from routers.routers_owners import router as owners_router
from routers.routers_citas import router as appointments_router
from routers.routers_animales import router as animals_router
from routers.routers_tratamientos import router as tratamientos_router
from routers.routers_productos import router as productos_router
from database.engine import create_tables, seed_initial_data

# Inicializar base de datos y datos iniciales
create_tables()
seed_initial_data()

# Crear instancia de la aplicación FastAPI
app = FastAPI(
    title="Gestión de Clínica Veterinaria",
    description="API para la gestión de datos de la clínica veterinaria y otras funcionalidades.",
    version="0.2.0"
)

# Incluir routers
app.include_router(owners_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")
app.include_router(animals_router, prefix="/api/v1")
app.include_router(tratamientos_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")

# Mensaje de bienvenida
@app.get("/")
def read_root():
    return