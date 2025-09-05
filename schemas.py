#Pydantic-модели
# schemas.py
from pydantic import BaseModel

# Для задач
class TodoBase(BaseModel):
    title: str
    description: str = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoResponse(TodoBase):
    id: int

    class Config:
        orm_mode = True

# Для пользователей
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None