from pydantic import BaseModel
from typing import Optional

# Базовая схема
class UserBase(BaseModel):
    login: str
    id_role_s: int
    id_staff: int
    is_active: bool = True

# Для создания
class UserCreate(UserBase):
    password: str

# Для обновления
class UserUpdate(UserBase):
    password: Optional[str] = None

# Для ответа (без пароля)
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Для входа в систему
class UserLogin(BaseModel):
    login: str
    password: str