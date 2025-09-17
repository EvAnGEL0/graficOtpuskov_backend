from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app import models
from app.schemas import rank_s as rank_schema

# Создаем роутер для звания
router = APIRouter(
    prefix="/rank",
    tags=["rank"]  # Для документации
)

@router.get("/", response_model=list[rank_schema.Rank])
async def read_ranks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Rank_s).offset(skip).limit(limit))
    rank = result.scalars().all()
    return rank


# Получение звания по ID
@router.get("/{rank_id}", response_model=rank_schema.Rank)
async def read_rank(rank_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Rank_s).where(models.Rank_s.id == rank_id))
    rank = result.scalar_one_or_none()
    
    if rank is None:
        raise HTTPException(status_code=404, detail="rank not found")
    return rank


# Создание звания
@router.post("/", response_model=rank_schema.Rank)
async def create_rank(rank: rank_schema.RankCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существование
    result = await db.execute(select(models.Rank_s).where(models.Rank_s.name == rank.name))
    db_rank = result.scalar_one_or_none()
    
    if db_rank:
        raise HTTPException(status_code=400, detail="rank already exists")
    
    # Создаем новую звание
    new_rank = models.Rank_s(name=rank.name)
    db.add(new_rank)
    await db.commit()
    await db.refresh(new_rank)
    return new_rank


# Обновление звания
@router.put("/{rank_id}", response_model=rank_schema.Rank)
async def update_rank(
    rank_id: int, 
    rank: rank_schema.RankUpdate, 
    db: AsyncSession = Depends(get_db)
):
    # Находим звание
    result = await db.execute(select(models.Rank_s).where(models.Rank_s.id == rank_id))
    db_rank = result.scalar_one_or_none()
    
    if db_rank is None:
        raise HTTPException(status_code=404, detail="rank not found")
    
    # Проверяем уникальность имени
    if rank.name != db_rank.name:
        existing_result = await db.execute(select(models.Rank_s).where(models.Rank_s.name == rank.name))
        existing_rank = existing_result.scalar_one_or_none()
        if existing_rank:
            raise HTTPException(status_code=400, detail="rank name already exists")
    
    # Обновляем данные
    db_rank.name = rank.name
    await db.commit()
    await db.refresh(db_rank)
    return db_rank



# Удаление звания
@router.delete("/{rank_id}")
async def delete_rank(rank_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Rank_s).where(models.Rank_s.id == rank_id))
    rank = result.scalar_one_or_none()
    
    if rank is None:
        raise HTTPException(status_code=404, detail="rank not found")
    
    await db.delete(rank)
    await db.commit()
    return {"message": "rank deleted successfully"}