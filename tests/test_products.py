import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from app.main import app
from utils import register_and_login

client = TestClient(app)

def test_create_product_requires_auth():
    payload = {
        "name": "Mango",
        "price": 100.0,
        "in_stock": True,
    }
    
    response = client.post("/products/", json=payload)
    
    assert response.status_code == 401
    
def test_create_product_with_token():
    email = "productuser@example.com"
    password = "secret123"
    
    token = register_and_login(client, email, password)
    
    headers = {"Authorization": f"Bearer {token}"}    
    
    payload = {
        "name": "Banana",
        "price": 40.0,
        "in_stock": True,
    }

    response = client.post("/products/", json=payload, headers=headers)
    
    assert response.status_code in (200, 201)
    
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["in_stock"] is True
    assert "id" in data
    
def test_list_products_pagination_and_wrapper():
    email = "listuser@example.com"
    password = "secret123"
    token = register_and_login(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(5):
        client.post(
            "/products/",
            json={"name": f"Prod{i}", "price": 10.0 * (i + 1), "in_stock": True},
            headers=headers,
        )
        
    response = client.get("/products/?skip=0&limit=3", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    # We expect wrapper format: { items, total, skip, limit }
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data

    assert isinstance(data["items"], list)
    assert data["skip"] == 0
    assert data["limit"] == 3
    # total should be >= 5 now, but we won't assert exact number
    assert data["total"] >= 5
    assert len(data["items"]) <= 3
            