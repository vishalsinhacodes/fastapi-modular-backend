import sys
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_new_user():
    unique_email = f"testuser_{uuid.uuid4().hex}@example.com"
    payload = {
        "email": unique_email,
        "password": "test123",
    }
    
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code in (200, 201)
    
    data = response.json()
    assert data["email"] == unique_email
    assert "id" in data
    assert "is_active" in data
    
def test_register_duplicate_user():
    payload = {
        "email": "dupuser@example.com",
        "password": "test123",
    }
    client.post("/auth/register", json=payload)
    
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    
    data = response.json()
    assert data["detail"] == "User already registered"
    assert data["code"] == "USER_EXISTS"
    
            