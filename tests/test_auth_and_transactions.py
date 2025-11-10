from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_and_login_success():
    # --- Teste de registro ---
    response = client.post("/register", json={
        "name": "Teste",
        "email": "teste2@example.com",
        "password": "123456"
    })
    print("\n[DEBUG REGISTER]", response.status_code, response.json())
    assert response.status_code in (200, 201, 400)

    # --- Teste de login ---
    response = client.post("/login", data={
        "username": "teste2@example.com",
        "password": "123456"
    })
    print("\n[DEBUG LOGIN]", response.status_code, response.json())
    assert response.status_code in (200, 201)

    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        token = data["access_token"]
        return token
    else:
        return None


def test_create_transaction_type_and_transaction():
    # Primeiro, pegar o token do login
    login_response = client.post("/login", data={
        "username": "teste2@example.com",
        "password": "123456"
    })
    print("\n[DEBUG LOGIN 2]", login_response.status_code, login_response.json())

    assert login_response.status_code == 200, "Falha no login — token não obtido"
    token = login_response.json()["access_token"]

    # --- Criar tipo de transação ---
    tipo_response = client.post(
        "/transaction-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Alimentação"}
    )
    print("\n[DEBUG TIPO]", tipo_response.status_code, tipo_response.json())
    assert tipo_response.status_code in (200, 201)

    tipo_id = tipo_response.json().get("id") or tipo_response.json().get("type_id")

    # --- Criar transação ---
    trans_response = client.post(
        "/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "type_id": tipo_id,
            "amount": 100.0
        }
    )
    print("\n[DEBUG TRANSACTION]", trans_response.status_code, trans_response.json())
    assert trans_response.status_code in (200, 201)
