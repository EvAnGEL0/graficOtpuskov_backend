# main.py
from fastapi import FastAPI
from api.routes import router  # Абсолютный импорт
from database import engine
from models import Base

# Создаём таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Календарь отпусков",
    description="API для управления графиком отпусков",
    version="1.0.0"
)

# Подключаем маршруты
app.include_router(router)

# Проверка работоспособности
@app.get("/")
def health_check():
    return {"status": "ok", "message": "FastAPI работает!"}