
'''
import random
import unittest
import requests
import uuid
from datetime import datetime


class TestClinicaVeterinaria(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://localhost:8000/api/v1"
        cls.unique_id = str(uuid.uuid4())[:6]
        cls.data = {
            "owner_id": None,
            "animal_id": None,
            "appointment_id": None,
            "invoice_id": None
        }

    # --- 1. TEST DUEÑOS (Campos: nombre, dni, direccion, telefono, correo_electronico) ---
    def test_01_crear_dueno(self):
        payload = {
            "nombre": f"Test User {self.unique_id}",
            "dni": f"DNI-{self.unique_id}",
            "direccion": "Calle Falsa 123",
            "telefono": "600000000",
            "correo_electronico": f"test-{self.unique_id}@vet.com"
        }
        response = requests.post(f"{self.base_url}/owners", json=payload)

        self.assertIn(response.status_code, [200, 201], f"Error 422: Revisa nombres de campos -> {response.text}")
        self.__class__.data["owner_id"] = response.json()["id"]

    # --- 2. TEST ANIMALES (Campos: name, species, breed, age, owner_id) ---
    def test_02_crear_mascota(self):
        self.assertIsNotNone(self.data["owner_id"])
        payload = {
            "name": f"Toby-{self.unique_id}",
            "species": "Perro",
            "breed": "Labrador",
            "age": 3,
            "owner_id": self.data["owner_id"]
        }
        response = requests.post(f"{self.base_url}/animals", json=payload)
        self.assertIn(response.status_code, [200, 201], f"Fallo en Animal: {response.text}")
        self.__class__.data["animal_id"] = response.json()["id"]

    # --- 3. TEST CITAS (Campos: date, time, treatment, consultation, owner_id, animal_id) ---
    def test_03_agendar_cita(self):
        """Genera una cita única para evitar el error 400 de conflicto"""
        # Usamos random para asegurar que la combinación fecha/hora/consulta sea única
        hora_random = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
        consulta_random = f"Consulta-{uuid.uuid4().hex[:4]}"

        payload = {
            "date": "2026-06-15",
            "time": hora_random,
            "treatment": "Revision TDD",
            "reason": "Test de integracion",
            "consultation": consulta_random,
            "owner_id": self.data["owner_id"],
            "animal_id": self.data["animal_id"]
        }
        response = requests.post(f"{self.base_url}/appointments", json=payload)

        self.assertIn(response.status_code, [200, 201], f"Fallo en Cita: {response.text}")
        # Guardamos el ID para que la factura lo reciba
        self.__class__.data["appointment_id"] = response.json()["id"]

    def test_04_generar_factura(self):
        """Valida la creación de factura asegurando que el ID de cita existe"""
        # Verificación de seguridad: si el test anterior falló, este no puede ejecutarse
        if self.data["appointment_id"] is None:
            self.skipTest("Saltando test de factura porque no se pudo crear la cita previa.")

        payload = {
            "appointment_id": self.data["appointment_id"],
            "owner_id": self.data["owner_id"],
            "treatments": "Vacuna, Desparasitación",
            "total_price": 65.0,
            "payment_method": "Tarjeta",
            "paid": False
        }

        # Intentamos con la ruta raíz (plural)
        response = requests.post(f"{self.base_url}/invoices", json=payload)

        self.assertIn(response.status_code, [200, 201], f"Fallo en Factura: {response.text}")


if __name__ == '__main__':
    unittest.main()

'''