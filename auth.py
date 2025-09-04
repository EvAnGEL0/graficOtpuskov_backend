# auth.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from . import schemas, crud, database, models

# ==================== НАСТРОЙКИ АВТОРИЗАЦИИ ====================
# Секретный ключ для подписи токенов (НИКОГДА не храните в коде в продакшене!)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"  # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена

# Создаем схему аутентификации
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",  # URL для получения токена
    scheme_name="JWT"    # Имя схемы (отобразится в Swagger)
)

# ==================== ОСНОВНЫЕ ФУНКЦИИ ====================

def verify_password(plain_password, hashed_password):
    """
    Проверяет, совпадает ли открытый пароль с хешем
    
    Args:
        plain_password: Пароль в открытом виде (который ввел пользователь)
        hashed_password: Хешированный пароль из БД
    
    Returns:
        bool: True если пароли совпадают, иначе False
    """
    return models.pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Хеширует пароль с помощью bcrypt
    
    Args:
        password: Пароль в открытом виде
    
    Returns:
        str: Хешированный пароль
    """
    return models.pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    """
    Аутентифицирует пользователя по логину и паролю
    
    Args:
        db: Сессия базы данных
        username: Логин пользователя
        password: Пароль в открытом виде
    
    Returns:
        User: Объект пользователя если аутентификация успешна
        False: Если пользователь не найден или пароль неверен
    """
    # Ищем пользователя по логину
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return False
    # Проверяем пароль
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token( dict, expires_delta: Optional[timedelta] = None):
    """
    Создает JWT-токен
    
    Args:
        data: Данные для кодирования в токен (обычно содержит sub - идентификатор пользователя)
        expires_delta: Срок действия токена (если не указан, используется значение по умолчанию)
    
    Returns:
        str: JWT-токен
    """
    to_encode = data.copy()
    # Определяем срок действия токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # Добавляем время истечения в данные
    to_encode.update({"exp": expire})
    # Кодируем данные в JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Получает текущего пользователя из JWT-токена
    
    Args:
        db: Сессия базы данных
        token: JWT-токен из заголовка Authorization
    
    Returns:
        User: Объект текущего пользователя
    
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Извлекаем идентификатор пользователя (sub)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Ищем пользователя в базе
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    # Проверяем, активен ли пользователь
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    
    return user


async def get_current_active_user(
    current_user: models.User = Security(get_current_user)
):
    """
    Получает активного пользователя (проверяет, что учетная запись активна)
    
    Args:
        current_user: Текущий пользователь (полученный через get_current_user)
    
    Returns:
        User: Объект активного пользователя
    
    Raises:
        HTTPException: Если учетная запись деактивирована
    """
    # Эта проверка уже делается в get_current_user, но дублируем для явности
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user


def check_role(required_role: str):
    """
    Декоратор для проверки роли пользователя
    
    Args:
        required_role: Требуемая роль (например, "admin", "manager")
    
    Returns:
        функция-зависимость, которая проверяет роль пользователя
    
    Пример использования:
        @router.get("/admin")
        async def admin_route(user: User = Depends(check_role("admin"))):
            ...
    """
    def role_checker(
        current_user: models.User = Depends(get_current_active_user)
    ):
        # Проверяем, совпадает ли роль пользователя с требуемой
        if current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль {required_role}"
            )
        return current_user
    return role_checker