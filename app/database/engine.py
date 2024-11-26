# database/engine.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database.data.models import Owner, Animal  # Asegúrate de importar los modelos adecuados

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:example@postgres:5432/clinica_veterinaria"

engine = create_engine(
    os.getenv("DATABASE_URL", SQLALCHEMY_DATABASE_URL),  # Usa la variable de entorno si está disponible
    echo=True  # Opcional, para ver las consultas SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crea las tablas en la base de datos."""
    Base.metadata.create_all(bind=engine)

def seed_initial_data():
    """Inicializa datos con dueños y mascotas predeterminados."""
    db = SessionLocal()
    try:
        # Comprobar si ya hay datos iniciales
        if not db.query(Owner).first():
            # Crear los dueños y sus mascotas
            owner1 = Owner(
                nombre="Jaime Oriol",
                dni="12345678A",
                direccion="Calle Falsa 123",
                telefono="555-1234",
                correo_electronico="jaime.oriol@example.com",
                animals=[
                    Animal(name="Jorge Grube", species="Perro", breed="Golden Retriever", age=5),
                    Animal(name="Mbappe", species="Gato", breed="Siamés", age=3)
                ]
            )
            owner2 = Owner(
                nombre="Quino de Mier",
                dni="87654321B",
                direccion="Avenida Verdadera 456",
                telefono="555-5678",
                correo_electronico="quino.mier@example.com",
                animals=[
                    Animal(name="Alfredo Perez", species="Perro", breed="Bulldog", age=4),
                    Animal(name="Mateo Madrigal", species="Gato", breed="Maine Coon", age=2)
                ]
            )

            # Agregar datos a la sesión
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