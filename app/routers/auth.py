from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.schemas import user as user_schema
from app.core.security import verify_password, create_access_token
from app import models
from sqlalchemy import select
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

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

# Обновим функцию получения текущего пользователя
from fastapi.security import OAuth2PasswordBearer
from app.config.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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
        select(models.User).where(models.User.login == login)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user