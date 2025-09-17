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
@router.get("/",response_model=list[department_schema.Department])
async def read_departments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Department_s).offset(skip).limit(limit))
    departments = result.scalars().all()
    return departments


 # Получение должности по ID
@router.get("/{departments_id}",response_model=department_schema.Department)
async def read_rdepartments(departments_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Department_s).where(models.Department_s.id == departments_id))
    departments = result.scalar_one_or_none()
    
    if departments is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return departments   
    
    
# Создание должности
@router.post("/", response_model=department_schema.Department)
async def create_deportament(deportament:department_schema.DepartmentCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существование
    result = await db.execute(select(models.Department_s).where(models.Department_s.name == deportament.name))
    db_depotrament = result.scalar_one_or_none()
    
    if db_depotrament:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    new_deportament= models.Department_s(name=deportament.name)
    db.add(new_deportament)
    await db.commit()
    await db.refresh(new_deportament)
    return new_deportament

# Обновление должности
@router.put("/{departments_id}", response_model=department_schema.Department)
async def update_role(
    departments_id: int, 
    departments: department_schema.DepartmentUpdate, 
    db: AsyncSession = Depends(get_db)
):
    # Находим роль
    result = await db.execute(select(models.Department_s).where(models.Department_s.id == departments_id))
    db_departments = result.scalar_one_or_none()
    
    if db_departments is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Проверяем уникальность имени
    if departments.name != db_departments.name:
        existing_result = await db.execute(select(models.Department_s).where(models.Department_s.name == departments.name))
        existing_departments = existing_result.scalar_one_or_none()
        if existing_departments:
            raise HTTPException(status_code=400, detail="Role name already exists")
    
    # Обновляем данные
    db_departments.name = departments.name
    await db.commit()
    await db.refresh(db_departments)
    return db_departments


# Удаление должности
@router.delete("/{departments_id}")
async def delete_departments(departments_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Department_s).where(models.Department_s.id == departments_id))
    departments = result.scalar_one_or_none()
    
    if departments is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    await db.delete(departments)
    await db.commit()
    return {"message": "Role deleted successfully"}