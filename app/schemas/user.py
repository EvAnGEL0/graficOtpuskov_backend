# app/schemas/user.py
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    login: str
    id_role_s: int
    id_staff: int
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    login: str
    password: str