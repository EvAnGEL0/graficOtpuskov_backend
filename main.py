# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi.middleware.cors import CORSMiddleware

import database
import models
import schemas
from auth import get_password_hash, create_access_token, get_current_user, verify_password

app = FastAPI()

# Разрешаем React (http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём таблицы
@app.on_event("startup")
async def init_db():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Зависимость для сессии
async def get_db():
    async with database.AsyncSessionLocal() as session:
        yield session

# 🔐 Регистрация нового пользователя
@app.post("/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверим, существует ли пользователь
    result = await db.execute(models.User.__table__.select().where(models.User.username == user.username))
    if result.fetchone():
        raise HTTPException(status_code=400, detail="Имя пользователя занято")

    hashed_pw = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Выдаем токен
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 🔐 Вход (логин)
@app.post("/login", response_model=schemas.Token)
async def login(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(models.User.__table__.select().where(models.User.username == user.username))
    db_user = result.fetchone()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверное имя или пароль")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 🛡️ Пример защищённого маршрута
@app.get("/me")
async def read_users_me(current_user = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}

# 📝 Все маршруты для Todo — защищаем от неавторизованных
@app.get("/todos/", response_model=List[schemas.TodoResponse])
async def get_todos(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(models.Todo.__table__.select())
    todos = result.fetchall()
    return [
        schemas.TodoResponse(
            id=row.id,
            title=row.title,
            description=row.description,
            completed=row.completed
        )
        for row in todos
    ]

@app.post("/todos/", response_model=schemas.TodoResponse)
async def create_todo(
    todo: schemas.TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_todo = models.Todo(**todo.dict())
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return new_todo