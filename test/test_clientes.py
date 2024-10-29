from fastapi.testclient import TestClient
from server import app
import pytest

client = TestClient(app)

@pytest.fixture
def nuevo_dueno():
    return {
        "nombre": "Carlos",
        "dni": "12345678Z",
        "direccion": "Calle Falsa 123",
        "telefono": "123456789",
        "correo": "carlos@mail.com"
    }

def test_crear_dueno(nuevo_dueno):
    response = client.post("/api/duenos/", json=nuevo_dueno)
    assert response.status_code == 200
    assert response.json()["nombre"] == nuevo_dueno["nombre"]

def test_crear_dueno_duplicado(nuevo_dueno):
    client.post("/api/duenos/", json=nuevo_dueno)
    response = client.post("/api/duenos/", json=nuevo_dueno)
    assert response.status_code == 400
    assert "Error al registrar el dueño" in response.json()["detail"]