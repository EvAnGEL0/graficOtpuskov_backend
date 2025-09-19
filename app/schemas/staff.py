# app/schemas/staff.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

# Базовая схема без связей
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
    supervisor_id: Optional[int] = None
    is_active: bool = True

# Для создания
class StaffCreate(StaffBase):
    pass

# Для ответа без связей
class StaffResponse(StaffBase):
    id: int

    class Config:
        from_attributes = True

# Для ответа с связями (если используешь selectinload)
class StaffWithRelations(StaffBase):
    id: int
    department: Optional['DepartmentResponse'] = None
    position: Optional['PositionResponse'] = None
    rank: Optional['RankResponse'] = None

    class Config:
        from_attributes = True