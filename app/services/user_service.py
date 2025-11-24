import logging

from sqlalchemy.orm import Session
from app.core.errors import ConflictError
from app.models.user import UserModel
from app.schemas.user import UserCreate, User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.token import Token

logger = logging.getLogger("app")

class UserService:
    def create_user(self, db: Session, payload: UserCreate) -> User:
        existing = db.query(UserModel).filter(UserModel.email == payload.email).first()
        if existing:
            logger.info(f"Registration attempt with existing email: {payload.email}")
            raise ConflictError("User already registered", code="USER_EXISTS")
        
        user_count = db.query(UserModel).count()
        is_admin = user_count == 0

        hashed = hash_password(payload.password)
        user = UserModel(email=payload.email, hashed_password=hashed, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"New user registered: id={user.id}, email={user.email}, is_admin={user.is_admin}")
        return User.model_validate(user)

    def authenticate(self, db: Session, email: str, password: str):
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    def create_token(self, user: UserModel):
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
