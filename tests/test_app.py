from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "Bem-vindo" in response.text or "API" in response.text
