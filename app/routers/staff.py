from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config.database import get_db
from app import models
from app.schemas import staff as staff_schema

router = APIRouter(
    prefix="/staff",
    tags=["staff"]
)

# Создание сотрудника
@router.post("/", response_model=staff_schema.StaffResponse)
async def create_staff(staff: staff_schema.StaffCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существование связанных записей
    # Проверка department
    if staff.department_id:
        dept_result = await db.execute(
            select(models.Department_s).where(models.Department_s.id == staff.department_id)
        )
        if not dept_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Department not found")
    
    # Проверка position
    if staff.position_id:
        pos_result = await db.execute(
            select(models.Position_s).where(models.Position_s.id == staff.position_id)
        )
        if not pos_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Position not found")
    
    # Проверка rank
    if staff.rank_id:
        rank_result = await db.execute(
            select(models.Rank_s).where(models.Rank_s.id == staff.rank_id)
        )
        if not rank_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Rank not found")
    
    # Проверка supervisor
    if staff.supervisor_id:
        sup_result = await db.execute(
            select(models.Staff).where(models.Staff.id == staff.supervisor_id)
        )
        if not sup_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Supervisor not found")
    
    new_staff = models.Staff(**staff.dict())
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff

# Получение сотрудника по ID (без связей)
@router.get("/{staff_id}", response_model=staff_schema.StaffResponse)
async def read_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff).where(models.Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

# Получение сотрудника по ID (с загрузкой связей)
@router.get("/{staff_id}/full", response_model=staff_schema.StaffResponse)
async def read_staff_full(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.department),
            selectinload(models.Staff.position),
            selectinload(models.Staff.rank),
            selectinload(models.Staff.supervisor),
            selectinload(models.Staff.subordinates)
        )
        .where(models.Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

# Получение всех сотрудников (без связей)
@router.get("/", response_model=list[staff_schema.StaffResponse])
async def read_staff_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .offset(skip)
        .limit(limit)
    )
    staff_list = result.scalars().all()
    return staff_list

# Получение всех сотрудников (с загрузкой связей)
@router.get("/full/", response_model=list[staff_schema.StaffResponse])
async def read_staff_list_full(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.department),
            selectinload(models.Staff.position),
            selectinload(models.Staff.rank)
        )
        .offset(skip)
        .limit(limit)
    )
    staff_list = result.scalars().all()
    return staff_list

# Обновление сотрудника
@router.put("/{staff_id}", response_model=staff_schema.StaffResponse)
async def update_staff(
    staff_id: int, 
    staff_update: staff_schema.StaffCreate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Staff).where(models.Staff.id == staff_id)
    )
    db_staff = result.scalar_one_or_none()
    
    if db_staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # Обновляем поля
    for field, value in staff_update.dict().items():
        setattr(db_staff, field, value)
    
    await db.commit()
    await db.refresh(db_staff)
    return db_staff

# Удаление сотрудника
@router.delete("/{staff_id}")
async def delete_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff).where(models.Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    await db.delete(staff)
    await db.commit()
    return {"message": "Staff deleted successfully"}