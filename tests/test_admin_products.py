import sys
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import UserModel
from utils import register_and_login, create_product

client = TestClient(app)

def make_user_admin(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if user:
            user.is_admin = True
            db.commit()
    finally:
        db.close()
        
def test_non_admin_cannot_delete_product():
    admin_email = f"admin_{uuid.uuid4().hex}@example.com"
    admin_password = "secret123"
    admin_token = register_and_login(client, admin_email, admin_password)
    
    make_user_admin(admin_email)
    
    product_id = create_product(client, admin_token, name="AdminProduct")
    
    # Create a non-admin user
    user_email = f"user_{uuid.uuid4().hex}@example.com"
    user_password = "secret123"
    user_token = register_and_login(client, user_email, user_password)
    
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    response = client.delete(f"/products/{product_id}", headers=user_headers)
    assert response.status_code == 403
    
    data = response.json()
    assert data["detail"] == "Admin access required"
    
def test_admin_can_delete_product():
    admin_email = f"admin2_{uuid.uuid4().hex}@example.com"
    admin_password = "admin123"
    admin_token = register_and_login(client, admin_email, admin_password)
    make_user_admin(admin_email)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    product_id = create_product(client, admin_token, name="ToDelete")
    
    response = client.delete(f"/products/{product_id}", headers=admin_headers)
    assert response.status_code == 204
    
    list_resp = client.get("/products/?skip=0&limit=100", headers=admin_headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    ids = [item["id"] for item in data["items"]]
    assert product_id not in ids    