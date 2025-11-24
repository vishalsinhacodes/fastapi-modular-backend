from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)
