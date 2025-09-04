# schemas.py
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

# ==================== СХЕМЫ АВТОРИЗАЦИИ ====================

class Token(BaseModel):
    """
    Схема для ответа с токеном
    
    Пример:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Схема для данных в токене
    
    Обычно содержит только username (идентификатор пользователя)
    """
    username: Optional[str] = None


# ==================== СХЕМЫ СПРАВОЧНИКОВ ====================

class DepartmentBase(BaseModel):
    name: str

class Department(DepartmentBase):
    id: int

    class Config:
        from_attributes = True  # Включает поддержку SQLAlchemy моделей


class PositionBase(BaseModel):
    name: str

class Position(PositionBase):
    id: int

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True


class RequestStatusBase(BaseModel):
    name: str
    description: Optional[str] = None

class RequestStatus(RequestStatusBase):
    id: int

    class Config:
        from_attributes = True


# ==================== СХЕМЫ ПОЛЬЗОВАТЕЛЕЙ И СОТРУДНИКОВ ====================

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    start_working: Optional[date] = None
    color: str = "#3498db"

class EmployeeCreate(EmployeeBase):
    department_id: int
    position_id: int

class Employee(EmployeeBase):
    id: int
    department: Department
    position: Position

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    role_id: int

class User(UserBase):
    id: int
    employee: Employee
    role: Role

    class Config:
        from_attributes = True


# ==================== СХЕМЫ ОТПУСКОВ ====================

class VacationBase(BaseModel):
    start_date: date
    end_date: date
    comment: Optional[str] = None

class VacationCreate(VacationBase):
    employee_id: int
    status_id: int

class Vacation(VacationBase):
    id: int
    employee: Employee
    status: RequestStatus

    class Config:
        from_attributes = True