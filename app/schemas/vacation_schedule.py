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