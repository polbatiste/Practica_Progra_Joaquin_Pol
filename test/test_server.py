from fastapi.testclient import TestClient
from fastapi.server import app  # Importar `app` desde el archivo server.py

client = TestClient(app)

def test_retrieve_data():
    response = client.get("/retrieve_data/")
    assert response.status_code == 200
    # Comprobar que el resultado contiene una lista de contratos
    assert "contratos" in response.json()

def test_submit_form():
    # Datos de ejemplo para el formulario
    form_data = {
        "date": "2024-01-01",
        "description": "Descripción de prueba",
        "option": "Opción 1",
        "amount": 100.0
    }
    response = client.post("/envio/", json=form_data)
    assert response.status_code == 200
    # Verificar que el mensaje de éxito esté en la respuesta
    assert response.json() == {"message": "Formulario recibido", "data": form_data}
