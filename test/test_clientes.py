from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_crear_dueno():
    response = client.post("/api/duenos/", json={
        "nombre": "Carlos",
        "dni": "12345678Z",
        "direccion": "Calle Falsa 123",
        "telefono": "123456789",
        "correo": "carlos@mail.com"
    })
    assert response.status_code == 200
    assert response.json()["nombre"] == "Carlos"
