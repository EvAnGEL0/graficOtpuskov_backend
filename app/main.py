from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.cros import add_cors_middleware
from app.config.database import async_engine, Base, get_db
from app import models
from app.schemas import role_s as role_schema
from app.routers import role as role_router
from app.routers import department as department_router
from app.routers import rank as rank_router

app = FastAPI()

# Добавляем CORS middleware
add_cors_middleware(app)

# Создаем таблицы асинхронно
@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# Подключаем роутеры
app.include_router(role_router.router)
app.include_router(department_router.router)
app.include_router(rank_router.router)


@app.get("/")
def read_root():
    return {"test": "v1.0"}

