from pydantic import BaseModel
from typing import Optional
from datetime import date

# Базовая схема
class StaffBase(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    hire_date: date
    dismissal_date: Optional[date] = None
    display_color: Optional[str] = None
    department_id: int
    position_id: int
    rank_id: int
    role_id: int
    supervisor_id: Optional[int] = None

# Для создания сотрудника
class StaffCreate(StaffBase):
    pass

# Для обновления сотрудника
class StaffUpdate(StaffBase):
    pass

# Для ответа (без связей)
class StaffShort(StaffBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# Для ответа (с вложенными объектами)
class Staff(StaffShort):
    department: 'Department'
    position: 'Position'
    rank: 'Rank'
    role: 'Role_s'
    supervisor: Optional['StaffShort'] = None

    class Config:
        from_attributes = True

# Импорты для вложенных схем
from .department import Department
from .position import Position
from .rank import Rank

# Обнови аннотации типов
Staff.model_rebuild()