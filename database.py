# настройка БД
# database.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Путь к базе данных SQLite
DATABASE_URL = "sqlite+aiosqlite:///./todo.db"

# Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()