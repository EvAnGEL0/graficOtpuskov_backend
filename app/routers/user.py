from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.config.database import get_db
from app import models
from app.schemas import user as user_schema
from app.config.security import verify_password, get_password_hash, create_access_token, decode_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import selectinload  # <-- Добавьте этот импорт

# Создаем OAuth2PasswordBearer здесь, а не внутри функции
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

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

    # Создаем нового пользователя с хэшированным паролем
    new_user = models.User(
        login=user.login,
        password=get_password_hash(user.password),
        id_role_s=user.id_role_s,
        id_staff=user.id_staff,
        is_active=user.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # ✅ Возвращаем в формате UserResponse
    return user_schema.UserResponse(
        id=new_user.id,
        login=new_user.login,
        role_name=role.name,  # Используем объект роли, который мы уже получили
        id_staff=new_user.id_staff,
        is_active=new_user.is_active
    )
# Аутентификация пользователя и выдача JWT токена
@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(user_credentials: user_schema.UserLogin, db: AsyncSession = Depends(get_db)):
    # Находим пользователя по логину
    result = await db.execute(
        select(models.User).where(models.User.login == user_credentials.login)
    )
    user = result.scalar_one_or_none()
    
    # Проверяем существование пользователя и правильность пароля
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Создаем JWT токен
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.login, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# Получение текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    login: str = payload.get("sub")
    if login is None:
        raise credentials_exception

    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.role))  # Загружаем связь с ролью
        .where(models.User.login == login)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user

# Получение информации о текущем пользователе
@router.get("/me", response_model=user_schema.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    # Возвращаем схему с role_name
    return user_schema.UserResponse(
        id=current_user.id,
        login=current_user.login,
        role_name=current_user.role.name,  # Используем имя роли
        id_staff=current_user.id_staff,
        is_active=current_user.is_active
    )

# Получение пользователя по ID
@router.get("/{user_id}", response_model=user_schema.UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.role))
        .where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user_schema.UserResponse(
        id=user.id,
        login=user.login,
        role_name=user.role.name,
        id_staff=user.id_staff,
        is_active=user.is_active
    )


# Получение всех пользователей
@router.get("/", response_model=List[user_schema.UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.role))
        .offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return [
        user_schema.UserResponse(
            id=user.id,
            login=user.login,
            role_name=user.role.name,
            id_staff=user.id_staff,
            is_active=user.is_active
        )
        for user in users
    ]
# Обновление пользователя
@router.put("/{user_id}", response_model=user_schema.UserResponse)
async def update_user(
    user_id: int,
    user_update: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.role))  # Загружаем связь с ролью
        .where(models.User.id == user_id)
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
        if field == "password" and value is not None:
            setattr(db_user, field, get_password_hash(value))
        else:
            setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)

    # ✅ Возвращаем объект в формате UserResponse
    return user_schema.UserResponse(
        id=db_user.id,
        login=db_user.login,
        role_name=db_user.role.name,
        id_staff=db_user.id_staff,
        is_active=db_user.is_active
    )
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