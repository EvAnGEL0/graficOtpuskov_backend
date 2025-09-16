from pydantic import BaseModel
from typing import Optional

# Базовая схема
class DepartmentBase(BaseModel):
    name: str

# Для создания роли
class DepartmentCreate(DepartmentBase):
    pass

# Для обновления роли
class DepartmentUpdate(DepartmentBase):
    pass

# Для ответа
class Department(DepartmentBase):
    id: int

    class Config:
        from_attributes = True