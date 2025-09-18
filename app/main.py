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
from app.routers import position as position_router
from app.schemas import staff as staff_schema



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
app.include_router(position_router.router)


@app.get("/")
def read_root():
    return {"test": "v1.0"}



# Создание сотрудника
@app.post("/staff/", response_model=staff_schema.Staff)
async def create_staff(staff: staff_schema.StaffCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существование связанных записей
    # (добавь проверки для department_id, position_id, etc.)
    
    new_staff = models.Staff(**staff.model_dump())
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff

# Получение сотрудника по ID
@app.get("/staff/{staff_id}", response_model=staff_schema.Staff)
async def read_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Staff).where(models.Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

# Получение всех сотрудников
@app.get("/staff/", response_model=list[staff_schema.StaffShort])
async def read_staff_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Staff).offset(skip).limit(limit))
    staff_list = result.scalars().all()
    return staff_list