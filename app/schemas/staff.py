from pydantic import BaseModel
from typing import Optional
from datetime import date

class StaffBase(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    hire_date: date
    dismissal_date: Optional[date] = None
    display_color: Optional[str] = None
    department_id: Optional[int] = None  # Сделано опциональным
    position_id: Optional[int] = None    # Сделано опциональным
    rank_id: Optional[int] = None        # Сделано опциональным
    supervisor_id: Optional[int] = None
    is_active: bool = True

class StaffCreate(StaffBase):
    pass

class StaffUpdate(StaffBase):
    pass

class StaffResponse(StaffBase):
    id: int

    class Config:
        from_attributes = True