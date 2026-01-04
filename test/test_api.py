import pytest
import requests
import uuid

#Configuración de la URL de tu API local
BASE_URL = "http://localhost:8000/api/v1"


# --- FIXTURES (Datos compartidos para los tests) ---
@pytest.fixture(scope="module")
def shared_data():
    """Genera IDs únicos para evitar colisiones en la base de datos de test"""
    suffix = str(uuid.uuid4())[:8]
    return {
        "owner_dni": f"TEST-{suffix}",
        "owner_email": f"test-{suffix}@vet.com",
        "animal_name": f"Mascota-{suffix}"
    }


# --- TESTS DE USUARIOS (DUEÑOS) ---

def test_create_owner(shared_data):
    """TDD: Validar creación de dueño y persistencia"""
    payload = {
        "nombre": "Test User",
        "dni": shared_data["owner_dni"],
        "email": shared_data["owner_email"]
    }
    response = requests.post(f"{BASE_URL}/owners", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["dni"] == shared_data["owner_dni"]
    shared_data["owner_id"] = data["id"]  # Guardamos el ID de Mongo para los siguientes tests


def test_get_owner_by_id(shared_data):
    """Validar que el dueño existe en la BD"""
    response = requests.get(f"{BASE_URL}/owners/{shared_data['owner_id']}")
    assert response.status_code == 200
    assert response.json()["dni"] == shared_data["owner_dni"]


# --- TESTS DE PACIENTES (MASCOTAS) ---

def test_create_animal(shared_data):
    """Validar relación Mascota -> Dueño"""
    payload = {
        "name": shared_data["animal_name"],
        "species": "Canino",
        "owner_id": shared_data["owner_id"]
    }
    response = requests.post(f"{BASE_URL}/animals", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["owner_id"] == shared_data["owner_id"]
    shared_data["animal_id"] = data["id"]


# --- TESTS DE CITAS (AGENDA) ---

def test_create_appointment(shared_data):
    """Validar flujo de agenda"""
    payload = {
        "date": "2024-12-31",
        "time": "12:00:00",
        "treatment": "Consulta General",
        "reason": "Revision TDD",
        "owner_id": shared_data["owner_id"],
        "animal_id": shared_data["animal_id"],
        "consultation": "1"
    }
    response = requests.post(f"{BASE_URL}/appointments", json=payload)
    assert response.status_code in [200, 201]
    shared_data["appointment_id"] = response.json()["id"]


# --- TESTS DE FACTURACIÓN Y VENTAS ---

def test_create_invoice_and_calc(shared_data):
    """Validar que la factura se genera con los tratamientos correctos"""
    payload = {
        "owner_id": shared_data["owner_id"],
        "appointment_id": shared_data["appointment_id"],
        "treatments": "Vacuna Rabia, Desparasitación",
        "payment_method": "Tarjeta",
        "paid": False
    }
    response = requests.post(f"{BASE_URL}/invoices", json=payload)
    assert response.status_code in [200, 201]

    invoice = response.json()
    assert invoice["paid"] is False
    assert "Vacuna Rabia" in invoice["treatments"]
    shared_data["invoice_id"] = invoice["id"]


def test_mark_invoice_as_paid(shared_data):
    """Validar cambio de estado de pago (Lógica de negocio)"""
    inv_id = shared_data["invoice_id"]
    response = requests.put(f"{BASE_URL}/invoices/{inv_id}/pay")
    assert response.status_code == 200

    # Verificación secundaria
    check = requests.get(f"{BASE_URL}/invoices")
    factura_pagada = next(f for f in check.json() if f["id"] == inv_id)
    assert factura_pagada["paid"] is True


# --- TEST DE ROBUSTEZ (ESCENARIOS DE FALLO) ---

def test_error_missing_fields():
    """TDD: La API debe fallar si enviamos basura"""
    payload = {"nombre": "Incompleto"}  # Falta DNI y Email
    response = requests.post(f"{BASE_URL}/owners", json=payload)
    assert response.status_code in [400, 422]  # Error de validación