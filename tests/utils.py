from fastapi.testclient import TestClient

def register_and_login(client: TestClient, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    
    data = response.json()
    return data["access_token"]

def create_product(client: TestClient, token: str, name: str, price: float = 50.0) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": name,
        "price": price,
        "in_stock": True,
    }
    response = client.post("/products/", json=payload, headers=headers)
    assert response.status_code in (200, 201)
    data = response.json()
    return data["id"]