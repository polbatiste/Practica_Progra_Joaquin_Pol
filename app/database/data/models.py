from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, Date, Time
from sqlalchemy.orm import relationship
from database.engine import Base

class Owner(Base):
    __tablename__ = 'owners'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=False)
    correo_electronico = Column(String(100), nullable=False)
    
    animals = relationship("Animal", back_populates="owner", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="owner", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="owner", cascade="all, delete-orphan")

class Animal(Base):
    __tablename__ = 'animals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=False)
    
    owner = relationship("Owner", back_populates="animals")
    appointments = relationship("Appointment", back_populates="animal", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    treatment = Column(String(200), nullable=False)
    reason = Column(String(500))
    consultation = Column(String(50), nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=False)
    animal_id = Column(Integer, ForeignKey('animals.id'), nullable=False)
    completed = Column(Boolean, default=False)  # Nuevo campo para indicar si la cita fue completada

    owner = relationship("Owner", back_populates="appointments")
    animal = relationship("Animal", back_populates="appointments")
    invoice = relationship("Invoice", back_populates="appointment", uselist=False, cascade="all, delete-orphan")

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'), nullable=False)
    treatments = Column(String(500), nullable=False)  # Lista de tratamientos realizados
    total_price = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # Transferencia, efectivo o tarjeta
    paid = Column(Boolean, default=False)  # Indica si la factura está pagada

    appointment = relationship("Appointment", back_populates="invoice")
    owner = relationship("Owner", back_populates="invoices")