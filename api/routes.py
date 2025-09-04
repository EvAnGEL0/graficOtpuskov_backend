# api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm  # ✅ Исправленный импорт

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta  # ⚠️ ОШИБКА 1: Не было импорта timedelta

# Абсолютные импорты (без точек)
import crud
import schemas
import auth
import database
router = APIRouter()

# ==================== ЗАВИСИМОСТИ ====================

def get_db():
    """Зависимость для получения сессии БД"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ЭНДПОИНТЫ АВТОРИЗАЦИИ ====================

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),  # ⚠️ ОШИБКА 2: Неправильный синтаксис объявления параметра
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя и получение JWT-токена
    
    Args:
        form_data: Данные формы (username и password)
        db: Сессия базы данных
    
    Returns:
        Token: Объект с access_token и token_type
    
    Raises:
        HTTPException: Если логин или пароль неверны
    """
    # Аутентифицируем пользователя
    user = auth.authenticate_user(db, form_data.username, form_data.password)  # ⚠️ ОШИБКА 3: Использовалась несуществующая переменная
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем данные для токена (sub - обязательное поле в JWT)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},  # sub (subject) - идентификатор пользователя
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=schemas.User)
def read_users_me(
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Получение информации о текущем пользователе
    
    Защищенный маршрут - требует валидный JWT-токен
    
    Returns:
        User: Информация о текущем пользователе
    """
    return current_user


# ==================== ЭНДПОИНТЫ ДЛЯ АДМИНИСТРАТОРОВ ====================

@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.check_role("admin"))
):
    """
    Создание нового пользователя (только для администраторов)
    
    Args:
        user: Данные нового пользователя
        current_user: Текущий пользователь (автоматически проверяется на роль admin)
    
    Returns:
        User: Созданный пользователь
    
    Raises:
        HTTPException: Если текущий пользователь не администратор
    """
    # Проверяем, существует ли уже пользователь с таким логином
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )
    
    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.check_role("admin"))
):
    """
    Получение списка всех пользователей (только для администраторов)
    
    Args:
        skip: Сколько записей пропустить
        limit: Максимальное количество записей
        current_user: Текущий пользователь (автоматически проверяется на роль admin)
    
    Returns:
        List[User]: Список пользователей
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# ==================== ЭНДПОИНТЫ ДЛЯ СОТРУДНИКОВ ====================

@router.get("/employees/", response_model=List[schemas.Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Получение списка сотрудников
    
    Доступно всем авторизованным пользователям
    
    Args:
        skip: Сколько записей пропустить
        limit: Максимальное количество записей
    
    Returns:
        List[Employee]: Список сотрудников
    """
    return crud.get_employees(db, skip=skip, limit=limit)


@router.post("/employees/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.check_role("admin"))
):
    """
    Создание нового сотрудника (только для администраторов)
    
    Args:
        employee: Данные нового сотрудника
        current_user: Текущий пользователь (автоматически проверяется на роль admin)
    
    Returns:
        Employee: Созданный сотрудник
    """
    return crud.create_employee(db=db, employee=employee)


# ==================== ЭНДПОИНТЫ ДЛЯ ОТПУСКОВ ====================

@router.get("/vacations/", response_model=List[schemas.Vacation])
def read_vacations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Получение списка всех отпусков
    
    Доступно всем авторизованным пользователям
    
    Args:
        skip: Сколько записей пропустить
        limit: Максимальное количество записей
    
    Returns:
        List[Vacation]: Список отпусков
    """
    return crud.get_vacations(db, skip=skip, limit=limit)


@router.post("/vacations/", response_model=schemas.Vacation, status_code=status.HTTP_201_CREATED)
def create_vacation(
    vacation: schemas.VacationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Создание новой заявки на отпуск
    
    Доступно всем авторизованным пользователям
    
    Args:
        vacation: Данные новой заявки
    
    Returns:
        Vacation: Созданная заявка
    """
    return crud.create_vacation(db=db, vacation=vacation)


@router.get("/my-vacations/", response_model=List[schemas.Vacation])
def read_my_vacations(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Получение списка своих отпусков
    
    Доступно всем авторизованным пользователям
    
    Returns:
        List[Vacation]: Список отпусков текущего пользователя
    """
    return crud.get_vacations_by_employee(db, employee_id=current_user.employee.id)