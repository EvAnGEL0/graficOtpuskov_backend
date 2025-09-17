from pydantic import BaseModel
from typing import Optional

# Базовая схема
class PositionBase(BaseModel):
    name: str

# Для создания роли
class PositionCreate(PositionBase):
    pass

# Для обновления роли
class PositionUpdate(PositionBase):
    pass

# Для ответа
class Position(PositionBase):
    id: int

    class Config:
        from_attributes = True