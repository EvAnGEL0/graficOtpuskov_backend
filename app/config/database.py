from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Асинхронный URL для SQLite
ASYNC_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# Для PostgreSQL: "postgresql+asyncpg://user:password@localhost/dbname"

# Создаем асинхронный движок
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, echo=True)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()

# Асинхронная зависимость для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session