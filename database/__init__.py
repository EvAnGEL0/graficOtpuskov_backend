# database/__init__.py
from core.config import engine, AsyncSessionLocal, Base

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session