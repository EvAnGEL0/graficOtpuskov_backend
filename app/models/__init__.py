from app.config.database import Base
from .role_s import Role_s
from .department_s import Department_s
from .rank_s import Rank_s
from .position_s import Position_s
from .staff import Staff
from .vacation_schedule import VacationSchedule

# Экспортируем все модели для создания таблиц
__all__ = ["Role_s", "Department_s", "Rank_s","Position_s", "Staff", "Base", "VacationSchedule"]