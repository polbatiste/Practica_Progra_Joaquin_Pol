from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_crear_dueno():
    response = client.post(
        "/api/v1/duenos/",
        json={
            "nombre": "Juan Pérez",
            "dni": "12345678A",
            "direccion": "Calle Falsa 123",
            "telefono": "123456789",
            "correo_electronico": "juan@example.com"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Dueño creado con éxito"}