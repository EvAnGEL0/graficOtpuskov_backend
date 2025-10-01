from pydantic import BaseModel
from datetime import date
from typing import Optional

# Базовая схема
class VacationScheduleBase(BaseModel):
    staff_id: int
    start_date: date
    end_date: date
    main_vacation_days: int

# Для создания
class VacationScheduleCreate(VacationScheduleBase):
    pass

# Для обновления
class VacationScheduleUpdate(VacationScheduleBase):
    pass

# Для ответа
class VacationSchedule(VacationScheduleBase):
    id: int

    class Config:
        from_attributes = True
        
class VacationScheduleResponse(BaseModel):
    id: int
    staff_id: int
    start_date: date
    end_date: date
    main_vacation_days: int
    # Добавим информацию о сотруднике
    staff_last_name: str
    staff_first_name: str
    staff_middle_name: str
    department_name: str
    display_color: str

      
class VacationScheduleKadryResponse(BaseModel):
    id: int
    staff_id: int
    start_date: date
    end_date: date
    main_vacation_days: int
    # Добавим информацию о сотруднике
    staff_last_name: str
    staff_first_name: str
    staff_middle_name: str
    department_name: str
    rank_name: Optional[str] = None  # ✅ Сделано опциональным
    display_color: Optional[str] = "#ffffff"  # ✅ Сделано опциональным
    position_name: Optional[str] = None

    class Config:
        from_attributes = True