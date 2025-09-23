from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app import models
from app.schemas import user as user_schema
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Создание пользователя
@router.post("/", response_model=user_schema.UserResponse)
async def create_user(user: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким логином
    result = await db.execute(
        select(models.User).where(models.User.login == user.login)
    )
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="User with this login already exists")
    
    # Проверяем, существует ли сотрудник
    staff_result = await db.execute(
        select(models.Staff).where(models.Staff.id == user.id_staff)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=400, detail="Staff not found")
    
    # Проверяем, существует ли роль
    role_result = await db.execute(
        select(models.Role_s).where(models.Role_s.id == user.id_role_s)
    )
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")
    
    # Создаем нового пользователя
    # ВАЖНО: В реальном приложении нужно хэшировать пароль!
    new_user = models.User(
        login=user.login,
        password=user.password,  # TODO: хэшировать пароль
        id_role_s=user.id_role_s,
        id_staff=user.id_staff,
        is_active=user.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# Получение пользователя по ID
@router.get("/{user_id}", response_model=user_schema.UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Получение всех пользователей
@router.get("/", response_model=List[user_schema.UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users

# Аутентификация пользователя
@router.post("/login")
async def login_user(user_credentials: user_schema.UserLogin, db: AsyncSession = Depends(get_db)):
    # Находим пользователя по логину
    result = await db.execute(
        select(models.User).where(models.User.login == user_credentials.login)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.password != user_credentials.password:  # TODO: сравнение хэшей
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is deactivated")
    
    # В реальном приложении здесь должен быть JWT токен
    return {
        "user_id": user.id,
        "login": user.login,
        "staff_id": user.id_staff,
        "role_id": user.id_role_s,
        "message": "Login successful"
    }

# Обновление пользователя
@router.put("/{user_id}", response_model=user_schema.UserResponse)
async def update_user(
    user_id: int,
    user_update: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    db_user = result.scalar_one_or_none()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем существование сотрудника, если указан
    if user_update.id_staff is not None:
        staff_result = await db.execute(
            select(models.Staff).where(models.Staff.id == user_update.id_staff)
        )
        staff = staff_result.scalar_one_or_none()
        if not staff:
            raise HTTPException(status_code=400, detail="Staff not found")
    
    # Проверяем существование роли, если указана
    if user_update.id_role_s is not None:
        role_result = await db.execute(
            select(models.Role_s).where(models.Role_s.id == user_update.id_role_s)
        )
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")
    
    # Обновляем поля
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Удаление пользователя
@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}