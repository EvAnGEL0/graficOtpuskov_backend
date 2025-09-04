# crud.py
from sqlalchemy.orm import Session
from . import models, schemas

# ==================== СПРАВОЧНИКИ ====================

def get_departments(db: Session, skip: int = 0, limit: int = 100):
    """Получает список отделов"""
    return db.query(models.Department).offset(skip).limit(limit).all()

def get_positions(db: Session, skip: int = 0, limit: int = 100):
    """Получает список должностей"""
    return db.query(models.Position).offset(skip).limit(limit).all()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    """Получает список ролей"""
    return db.query(models.Role).offset(skip).limit(limit).all()

def get_request_statuses(db: Session, skip: int = 0, limit: int = 100):
    """Получает список статусов заявок"""
    return db.query(models.RequestStatus).offset(skip).limit(limit).all()


# ==================== ПОЛЬЗОВАТЕЛИ И СОТРУДНИКИ ====================

def get_user_by_username(db: Session, username: str):
    """Получает пользователя по логину"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int):
    """Получает пользователя по ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Получает список пользователей"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Создает нового пользователя"""
    # Хешируем пароль перед сохранением
    hashed_password = models.pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        is_active=user.is_active,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_employee(db: Session, employee_id: int):
    """Получает сотрудника по ID"""
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    """Получает список сотрудников"""
    return db.query(models.Employee).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    """Создает нового сотрудника"""
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


# ==================== ОТПУСКИ ====================

def get_vacations(db: Session, skip: int = 0, limit: int = 100):
    """Получает список всех отпусков"""
    return db.query(models.Vacation).offset(skip).limit(limit).all()

def get_vacations_by_employee(db: Session, employee_id: int):
    """Получает отпуска конкретного сотрудника"""
    return db.query(models.Vacation).filter(models.Vacation.employee_id == employee_id).all()

def create_vacation(db: Session, vacation: schemas.VacationCreate):
    """Создает новую заявку на отпуск"""
    db_vacation = models.Vacation(**vacation.dict())
    db.add(db_vacation)
    db.commit()
    db.refresh(db_vacation)
    return db_vacation