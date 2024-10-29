from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Dueno(Base):
    __tablename__ = 'duenos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    dni = Column(String(15), unique=True, nullable=False)
    direccion = Column(String(200))
    telefono = Column(String(20), nullable=False)
    correo_electronico = Column(String(100), unique=True, nullable=False)