from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app import models
from app.schemas import department_s as department_schema

# Создаем роутер для должностей
router = APIRouter(
    prefix="/departments",
    tags=["department"]  # Для документации
)

# Получение всех должностей
@router.get("/",response_model=department_schema.Department)
async def read_departments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Department_s).offset(skip).limit(limit))
    departments = result.scalars().all()
    return departments


# Получение должности по ID
@router.get("/{departments_id}",response_model=department_schema.Department)
async def read_roles(departments_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Department_s).where(models.Department_s.id == departments_id))
    departments = result.scalar_one_or_none()