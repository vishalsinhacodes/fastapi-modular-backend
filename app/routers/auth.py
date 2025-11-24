from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, User

router = APIRouter(prefix="/auth", tags=["Auth"])
user_service = UserService()

@router.post("/register", response_model=User)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, payload)


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return user_service.create_token(user)
