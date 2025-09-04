# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.routes import router
from database import engine
from models import Base
from auth import get_current_user

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Календарь отпусков",
    description="API для управления графиком отпусков сотрудников",
    version="2.0.0"
)

# Подключаем маршруты
app.include_router(router)

# ==================== ТЕСТОВЫЙ МАРШРУТ ====================

@app.get("/")
def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "message": "FastAPI работает!"}

# ==================== ЗАЩИЩЕННЫЙ МАРШРУТ ====================

@app.get("/protected")
def protected_route(
    current_user: dict = Depends(get_current_user)
):
    """
    Пример защищенного маршрута
    
    Требует валидный JWT-токен для доступа
    
    Returns:
        dict: Приветствие с именем пользователя
    """
    return {"message": f"Привет, {current_user.username}! Это защищенный маршрут."}

# ==================== ОБРАБОТЧИК ОШИБОК ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Обработчик HTTP-исключений
    
    Добавляет заголовок WWW-Authenticate для ошибок аутентификации
    """
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return {
            "status": "error",
            "detail": exc.detail,
            "headers": {"WWW-Authenticate": "Bearer"}
        }
    return {
        "status": "error",
        "detail": exc.detail
    }

# main.py (продолжение)

def create_test_data(db: Session):
    """Создает тестовые данные для демонстрации"""
    
    # Создаем роли, если их нет
    roles = [
        models.Role(name="user", description="Обычный пользователь"),
        models.Role(name="manager", description="Менеджер (может утверждать отпуска)"),
        models.Role(name="admin", description="Администратор (полный доступ)")
    ]
    for role in roles:
        if not db.query(models.Role).filter(models.Role.name == role.name).first():
            db.add(role)
    db.commit()
    
    # Создаем отделы
    departments = [
        models.Department(name="IT-отдел"),
        models.Department(name="Бухгалтерия"),
        models.Department(name="HR")
    ]
    for dept in departments:
        if not db.query(models.Department).filter(models.Department.name == dept.name).first():
            db.add(dept)
    db.commit()
    
    # Создаем должности
    positions = [
        models.Position(name="Разработчик"),
        models.Position(name="Менеджер"),
        models.Position(name="Аналитик")
    ]
    for pos in positions:
        if not db.query(models.Position).filter(models.Position.name == pos.name).first():
            db.add(pos)
    db.commit()
    
    # Создаем статусы заявок
    statuses = [
        models.RequestStatus(name="На рассмотрении", description="Заявка отправлена, ожидает проверки"),
        models.RequestStatus(name="Одобрен", description="Заявка утверждена руководителем"),
        models.RequestStatus(name="Отклонен", description="Заявка отклонена с комментарием")
    ]
    for status in statuses:
        if not db.query(models.RequestStatus).filter(models.RequestStatus.name == status.name).first():
            db.add(status)
    db.commit()
    
    # Создаем сотрудников
    employees = [
        models.Employee(
            first_name="Сергей",
            last_name="Рыбаков",
            middle_name="Васильевич",
            start_working=date(2020, 1, 15),
            color="#3498db",
            department_id=1,
            position_id=1
        ),
        models.Employee(
            first_name="Алексей",
            last_name="Бычков",
            middle_name="Сергеевич",
            start_working=date(2021, 3, 10),
            color="#e74c3c",
            department_id=1,
            position_id=2
        )
    ]
    for emp in employees:
        if not db.query(models.Employee).filter(
            models.Employee.first_name == emp.first_name,
            models.Employee.last_name == emp.last_name
        ).first():
            db.add(emp)
    db.commit()
    
    # Создаем пользователей
    users = [
        {
            "username": "rybakov",
            "password": "password123",
            "role_id": 3,  # admin
            "employee_id": 1
        },
        {
            "username": "bychkov",
            "password": "password123",
            "role_id": 1,  # user
            "employee_id": 2
        }
    ]
    for user_data in users:
        if not db.query(models.User).filter(models.User.username == user_data["username"]).first():
            user = models.User(
                username=user_data["username"],
                role_id=user_data["role_id"],
                employee_id=user_data["employee_id"]
            )
            user.set_password(user_data["password"])
            db.add(user)
    db.commit()

# Запускаем при старте
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    create_test_data(db)
    db.close()