from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import select
from app.config.database import get_db
from app import models
from app.schemas import vacation_schedule as vacation_schema

router = APIRouter(
    prefix="/vacation-schedules",
    tags=["vacation_schedules"]
)

# Создание графика отпуска
@router.post("/", response_model=vacation_schema.VacationSchedule)
async def create_vacation_schedule(
    vacation: vacation_schema.VacationScheduleCreate, 
    db: AsyncSession = Depends(get_db)
):
    new_vacation = models.VacationSchedule(**vacation.dict())
    db.add(new_vacation)
    await db.commit()
    await db.refresh(new_vacation)
    return new_vacation



@router.get("/boss/{boss_id}", response_model=list[vacation_schema.VacationScheduleResponse])
async def read_vacation_schedules_by_boss(boss_id: int, db: AsyncSession = Depends(get_db)):
    # Найти всех сотрудников, у которых supervisor_id == boss_id
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.vacation_schedules),
            selectinload(models.Staff.department)
        )
        .where(models.Staff.supervisor_id == boss_id)
    )
    staff_list = result.scalars().all()

    # Собираем все отпуска
    vacations = []
    for staff in staff_list:
        for vac in staff.vacation_schedules:
            vacations.append(
                vacation_schema.VacationScheduleResponse(
                    id=vac.id,
                    staff_id=vac.staff_id,
                    start_date=vac.start_date,
                    end_date=vac.end_date,
                    main_vacation_days=vac.main_vacation_days,
                    staff_last_name=staff.last_name,
                    staff_first_name=staff.first_name,
                    staff_middle_name=staff.middle_name,
                    department_name=staff.department.name if staff.department else None,
                    display_color=staff.display_color or "#ffffff"  # по умолчанию белый

                )
            )

    return vacations

@router.get("/department/{dept_id}", response_model=list[vacation_schema.VacationScheduleKadryResponse])
async def read_vacation_schedules_by_dept(dept_id: int, db: AsyncSession = Depends(get_db)):
    # Найти всех сотрудников, у которых supervisor_id == boss_id
    result = await db.execute(
        select(models.Staff)
        .options(
            selectinload(models.Staff.vacation_schedules),
            selectinload(models.Staff.department),
            selectinload(models.Staff.position),
            selectinload(models.Staff.rank)
        )
        .where(models.Staff.department_id == dept_id)
    )
    staff_list = result.scalars().all()

    # Собираем все отпуска
    vacations = []
    for staff in staff_list:
        for vac in staff.vacation_schedules:
            vacations.append(
                vacation_schema.VacationScheduleKadryResponse(
                    id=vac.id,
                    staff_id=vac.staff_id,
                    start_date=vac.start_date,
                    end_date=vac.end_date,
                    main_vacation_days=vac.main_vacation_days,
                    staff_last_name=staff.last_name,
                    staff_first_name=staff.first_name,
                    staff_middle_name=staff.middle_name,
                    department_name=staff.department.name if staff.department else None,
                    rank_name=staff.rank.name,   # ✅ Добавлено условие
                    position_name=staff.position.name
                )
            )

    return vacations



# Получение графика отпуска по ID
@router.get("/{vacation_id}", response_model=vacation_schema.VacationSchedule)
async def read_vacation_schedule(vacation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.VacationSchedule)
        .where(models.VacationSchedule.id == vacation_id)
    )
    vacation = result.scalar_one_or_none()
    
    if vacation is None:
        raise HTTPException(status_code=404, detail="Vacation schedule not found")
    return vacation

# Получение всех графиков отпусков
@router.get("/", response_model=list[vacation_schema.VacationSchedule])
async def read_vacation_schedules(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.VacationSchedule)
        .offset(skip)
        .limit(limit)
    )
    vacations = result.scalars().all()
    return vacations

# Получение графиков отпусков для конкретного сотрудника
@router.get("/staff/{staff_id}", response_model=list[vacation_schema.VacationSchedule])
async def read_vacation_schedules_by_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.VacationSchedule)
        .where(models.VacationSchedule.staff_id == staff_id)
    )
    vacations = result.scalars().all()
    return vacations

# Обновление графика отпуска
@router.put("/{vacation_id}", response_model=vacation_schema.VacationSchedule)
async def update_vacation_schedule(
    vacation_id: int,
    vacation_update: vacation_schema.VacationScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.VacationSchedule)
        .where(models.VacationSchedule.id == vacation_id)
    )
    db_vacation = result.scalar_one_or_none()
    
    if db_vacation is None:
        raise HTTPException(status_code=404, detail="Vacation schedule not found")
    
    # Обновляем поля
    for field, value in vacation_update.dict().items():
        setattr(db_vacation, field, value)
    
    await db.commit()
    await db.refresh(db_vacation)
    return db_vacation

# Удаление графика отпуска
@router.delete("/{vacation_id}")
async def delete_vacation_schedule(vacation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.VacationSchedule)
        .where(models.VacationSchedule.id == vacation_id)
    )
    vacation = result.scalar_one_or_none()
    
    if vacation is None:
        raise HTTPException(status_code=404, detail="Vacation schedule not found")
    
    await db.delete(vacation)
    await db.commit()
    return {"message": "Vacation schedule deleted successfully"}