from app.config.database import Base
from .role_s import Role_s
from .department_s import Department_s
from .rank_s import Rank_s

# Экспортируем все модели для создания таблиц
__all__ = ["Role_s", "Department_s", "Rank_s"]