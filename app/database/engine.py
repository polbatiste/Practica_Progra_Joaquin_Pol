import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "postgresql://postgres@localhost:5432/clinica_veterinaria"
#la bbdd es nueva con toda la estructura e informacion necesaria para registrar tanto
#animales como dueños

engine = create_engine(
    os.getenv("DATABASE_URL", SQLALCHEMY_DATABASE_URL),  # Usa la variable de entorno si está disponible
    echo=True  # Opcional, para ver las consultas SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Devuelve una sesión de la base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crea todas las tablas en la base de datos a partir de los modelos."""
    from app.database.data.models import Base  # Importación local para evitar circularidad
    Base.metadata.create_all(bind=engine)
    print("Estructura de tabla creada")

def seed_initial_data():
    """Inicializa datos con dueños, mascotas y tratamientos predeterminados."""
    from app.database.data.models import Owner, Animal  # Importación local
    db = SessionLocal()
    try:
        # Comprobar si ya hay datos iniciales
        if not db.query(Owner).first():
            owner1 = Owner(
                nombre="Pol Batiste",
                dni="54023033N",
                direccion="Calle Falsa 123",
                telefono="555-1234",
                correo_electronico="polbati1910@gmail.com",
                animals=[
                    Animal(name="Durko", species="Perro", breed="Golden Retriever", age=5, status="vivo"),
                    Animal(name="Mbappe", species="Gato", breed="Siamés", age=3, status="fallecido")  # Animal fallecido
                ]
            )
            owner2 = Owner(
                nombre="Quino de Mier",
                dni="87654321B",
                direccion="Avenida Verdadera 456",
                telefono="555-5678",
                correo_electronico="quinodemier3@gmail.com",
                animals=[
                    Animal(name="Bob", species="Perro", breed="Bulldog", age=4, status="vivo"),
                    Animal(name="Max", species="Gato", breed="Maine Coon", age=2, status="vivo")
                ]
            )

            db.add_all([owner1, owner2])
            db.commit()
            print("Datos iniciales creados con éxito.")
        else:
            print("Los datos iniciales ya existen.")
    except Exception as e:
        db.rollback()
        print(f"Error al insertar datos iniciales: {e}")
    finally:
        db.close()

#Correr para inicializar en local la bbdd
if __name__ == "__main__":
    create_tables()
    seed_initial_data()