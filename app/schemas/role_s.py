from pydantic import BaseModel
from typing import Optional

# Базовая схема
class RoleBase(BaseModel):
    name: str

# Для создания роли
class RoleCreate(RoleBase):
    pass

# Для обновления роли
class RoleUpdate(RoleBase):
    pass

# Для ответа
class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True