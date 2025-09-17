from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app import models
from app.schemas import position_s as position_schema

# Создаем роутер для звания
router = APIRouter(
    prefix="/position",
    tags=["position"]  # Для документации
)


@router.get("/", response_model=list[position_schema.Position])
async def read_positions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Position_s).offset(skip).limit(limit))
    positions = result.scalars().all()
    return positions


# Получение должности по ID
@router.get("/{position_id}", response_model=position_schema.Position)
async def read_position(position_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Position_s).where(models.Position_s.id == position_id))
    position = result.scalar_one_or_none()
    
    if position is None:
        raise HTTPException(status_code=404, detail="position not found")
    return position

# Создание должности
@router.post("/", response_model=position_schema.Position)
async def create_position(position: position_schema.PositionCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существование
    result = await db.execute(select(models.Position_s).where(models.Position_s.name == position.name))
    db_position = result.scalar_one_or_none()
    
    if db_position:
        raise HTTPException(status_code=400, detail="position already exists")
    
    # Создаем новую звание
    new_position = models.Position_s(name=position.name)
    db.add(new_position)
    await db.commit()
    await db.refresh(new_position)
    return new_position


# Обновление звания
@router.put("/{position_id}", response_model=position_schema.Position)
async def update_position(
    position_id: int, 
    position: position_schema.PositionUpdate, 
    db: AsyncSession = Depends(get_db)
):
    # Находим звание
    result = await db.execute(select(models.Position_s).where(models.Position_s.id == position_id))
    db_position = result.scalar_one_or_none()
    
    if db_position is None:
        raise HTTPException(status_code=404, detail="position not found")
    
    # Проверяем уникальность имени
    if position.name != db_position.name:
        existing_result = await db.execute(select(models.Position_s).where(models.Position_s.name == position.name))
        existing_position = existing_result.scalar_one_or_none()
        if existing_position:
            raise HTTPException(status_code=400, detail="position name already exists")
    
    # Обновляем данные
    db_position.name = position.name
    await db.commit()
    await db.refresh(db_position)
    return db_position


# Удаление звания
@router.delete("/{position_id}")
async def delete_position(position_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Position_s).where(models.Position_s.id == position_id))
    position = result.scalar_one_or_none()
    
    if position is None:
        raise HTTPException(status_code=404, detail="position not found")
    
    await db.delete(position)
    await db.commit()
    return {"message": "position deleted successfully"}