from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app import models
from app.schemas import role_s as role_schema

# Создаем роутер для ролей
router = APIRouter(
    prefix="/roles",
    tags=["roles"]  # Для документации
)

# Получение всех ролей
@router.get("/", response_model=list[role_schema.Role])
async def read_roles(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Role_s).offset(skip).limit(limit))
    roles = result.scalars().all()
    return roles

# Получение роли по ID
@router.get("/{role_id}", response_model=role_schema.Role)
async def read_role(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Role_s).where(models.Role_s.id == role_id))
    role = result.scalar_one_or_none()
    
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

# Создание роли
@router.post("/", response_model=role_schema.Role)
async def create_role(role: role_schema.RoleCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существование
    result = await db.execute(select(models.Role_s).where(models.Role_s.name == role.name))
    db_role = result.scalar_one_or_none()
    
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    # Создаем новую роль
    new_role = models.Role_s(name=role.name)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role

# Обновление роли
@router.put("/{role_id}", response_model=role_schema.Role)
async def update_role(
    role_id: int, 
    role: role_schema.RoleUpdate, 
    db: AsyncSession = Depends(get_db)
):
    # Находим роль
    result = await db.execute(select(models.Role_s).where(models.Role_s.id == role_id))
    db_role = result.scalar_one_or_none()
    
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Проверяем уникальность имени
    if role.name != db_role.name:
        existing_result = await db.execute(select(models.Role_s).where(models.Role_s.name == role.name))
        existing_role = existing_result.scalar_one_or_none()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role name already exists")
    
    # Обновляем данные
    db_role.name = role.name
    await db.commit()
    await db.refresh(db_role)
    return db_role

# Удаление роли
@router.delete("/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Role_s).where(models.Role_s.id == role_id))
    role = result.scalar_one_or_none()
    
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    await db.delete(role)
    await db.commit()
    return {"message": "Role deleted successfully"}