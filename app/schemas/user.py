# app/schemas/user.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Существующие схемы
class UserBase(BaseModel):
    login: str
    id_role_s: int  # Пока оставим для создания/обновления
    id_staff: int
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    login: str
    role_name: str  # Новое поле: имя роли
    id_staff: int
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    login: str
    password: str

# Новые схемы для JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    login: Optional[str] = None