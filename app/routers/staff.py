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
@router.post("/", response_model=staff_schema.StaffCreate)
async def create_staff(staff: staff_schema.StaffCreate, db: AsyncSession = Depends(get_db)):
    new_staff = models.Staff(**staff.dict())
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff

# Получение сотрудника по ID
@router.get("/{staff_id}", response_model=staff_schema.StaffResponse)
async def read_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .where(models.Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

# Получение всех сотрудников
@router.get("/", response_model=list[staff_schema.StaffResponse])
async def read_staff_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .offset(skip)
        .limit(limit)
    )
    staff_list = result.scalars().all()
    return staff_list

# # Обновление сотрудника
# @router.put("/{staff_id}", response_model=staff_schema.StaffResponse)
# async def update_staff(
#     staff_id: int, 
#     staff_update: staff_schema.StaffUpdate, 
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(models.Staff).where(models.Staff.id == staff_id)
#     )
#     db_staff = result.scalar_one_or_none()
    
#     if db_staff is None:
#         raise HTTPException(status_code=404, detail="Staff not found")
    
#     # Обновляем поля
#     for field, value in staff_update.dict(exclude_unset=True).items():
#         setattr(db_staff, field, value)
    
#     await db.commit()
#     await db.refresh(db_staff)
#     return db_staff

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