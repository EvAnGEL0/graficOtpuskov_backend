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


# Получение всех сотрудников (с загрузкой связей)
@router.get("/", response_model=list[staff_schema.StaffResponse])
async def read_staff_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.department),
            selectinload(models.Staff.position),
            selectinload(models.Staff.rank),
            selectinload(models.Staff.supervisor)
        )
        .offset(skip)
        .limit(limit)
    )
    staff_list = result.scalars().all()

    return [
        staff_schema.StaffResponse(
            id=staff.id,
            last_name=staff.last_name,
            first_name=staff.first_name,
            middle_name=staff.middle_name,
            hire_date=staff.hire_date,
            dismissal_date=staff.dismissal_date,
            display_color=staff.display_color,
            department_id=staff.department_id,
            position_id=staff.position_id,
            rank_id=staff.rank_id,
            supervisor_id=staff.supervisor_id,
            is_active=staff.is_active,
            # Добавляем названия
            department_name=staff.department.name if staff.department else None,
            position_name=staff.position.name if staff.position else None,
            rank_name=staff.rank.name if staff.rank else None,
            supervisor_name=f"{staff.supervisor.first_name} {staff.supervisor.last_name}" if staff.supervisor else None
        )
        for staff in staff_list
    ]

# Получение всех сотрудников (с загрузкой связей)
@router.get("/boss/{boss_id}", response_model=list[staff_schema.StaffResponse])
async def read_staff_list(boss_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.department),
            selectinload(models.Staff.position),
            selectinload(models.Staff.rank),
            selectinload(models.Staff.supervisor)
        )
        .where(models.Staff.supervisor_id == boss_id)    )
    staff_list = result.scalars().all()

    return [
        staff_schema.StaffResponse(
            id=staff.id,
            last_name=staff.last_name,
            first_name=staff.first_name,
            middle_name=staff.middle_name,
            hire_date=staff.hire_date,
            dismissal_date=staff.dismissal_date,
            display_color=staff.display_color,
            department_id=staff.department_id,
            position_id=staff.position_id,
            rank_id=staff.rank_id,
            supervisor_id=staff.supervisor_id,
            is_active=staff.is_active,
            # Добавляем названия
            department_name=staff.department.name if staff.department else None,
            position_name=staff.position.name if staff.position else None,
            rank_name=staff.rank.name if staff.rank else None,
            supervisor_name=f"{staff.supervisor.first_name} {staff.supervisor.last_name}" if staff.supervisor else None
        )
        for staff in staff_list
    ]


# Получение сотрудника по ID
@router.get("/{staff_id}", response_model=staff_schema.StaffResponse)
async def read_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.department),
            selectinload(models.Staff.position),
            selectinload(models.Staff.rank),
            selectinload(models.Staff.supervisor)
        )
        .where(models.Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()

    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")

    return staff_schema.StaffResponse(
        id=staff.id,
        last_name=staff.last_name,
        first_name=staff.first_name,
        middle_name=staff.middle_name,
        hire_date=staff.hire_date,
        dismissal_date=staff.dismissal_date,
        display_color=staff.display_color,
        department_id=staff.department_id,
        position_id=staff.position_id,
        rank_id=staff.rank_id,
        supervisor_id=staff.supervisor_id,
        is_active=staff.is_active,
        # Добавляем названия
        department_name=staff.department.name if staff.department else None,
        position_name=staff.position.name if staff.position else None,
        rank_name=staff.rank.name if staff.rank else None,
        supervisor_name=f"{staff.supervisor.first_name} {staff.supervisor.last_name}" if staff.supervisor else None
    )

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
    # Проверяем, есть ли у сотрудника связанный пользователь
    user_result = await db.execute(
        select(models.User).where(models.User.id_staff == staff_id)
    )
    user = user_result.scalar_one_or_none()

    if user:
        # Если есть связанный пользователь — удаляем его
        await db.delete(user)

    # Теперь удаляем сотрудника
    result = await db.execute(
        select(models.Staff).where(models.Staff.id == staff_id)
    )
    staff = result.scalar_one_or_none()

    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")

    await db.delete(staff)
    await db.commit()
    return {"message": "Staff deleted successfully"}