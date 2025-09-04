# models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------------------------СПРАВОЧНИКИ---------------------------------------------------------- #

class Department(Base):
    """
    Справочник отделов компании
    """
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="Название отдела (уникальное)")
    
    # Обратная связь: один отдел → много сотрудников
    employees = relationship("Employee", back_populates="department")

class Position(Base):
    """
    Справочник должностей
    """
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="Название должности")
    
    # Обратная связь: должность → сотрудники
    employees = relationship("Employee", back_populates="position")

class Role(Base):
    """
    Справочник ролей пользователей
    
    Примеры данных:
    - user (обычный пользователь)
    - manager (менеджер)
    - admin (администратор)
    
    Зачем нужен:
    - Определяет права доступа
    - Позволяет ограничивать функционал
    """
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="Название роли")
    description = Column(String(255), comment="Описание прав доступа")
    
    # Обратная связь: роль → пользователи
    users = relationship("User", back_populates="role")
class RequestStatus(Base):
    """
    Справочник статусов заявок на отпуск
    
   
    """
    __tablename__ = "request_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="Название статуса")
    description = Column(String(255), comment="Подробное описание статуса")
    
    # Обратная связь: статус → заявки на отпуск
    vacations = relationship("Vacation", back_populates="status")


# ----------------------------------------------------------ОСНОВНЫЕ ТАБЛИЦЫ------------------------------------------------------------ #

class Employee(Base):
    """
    Таблица сотрудников компании
    
    Содержит основную информацию о сотруднике.
    
    Особенности:
    - Полное ФИО (отчество необязательно)
    - Привязка к отделу и должности
    - Может иметь только одного пользователя
    - Цвет для отображения в календаре
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False, comment="Имя сотрудника")
    last_name = Column(String(50), nullable=False, comment="Фамилия сотрудника")
    middle_name = Column(String(50), comment="Отчество сотрудника (опционально)")
    start_working = Column(Date, comment="Дата приема на работу")
    color = Column(String(7), default="#3498db", comment="Цвет для отображения в календаре")
    
    # Связь с отделом (многие к одному)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False,
                          comment="ID отдела из справочника departments")
    department = relationship("Department", back_populates="employees",
                            comment="Отдел, в котором работает сотрудник")
    
    # Связь с должностью (многие к одному)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False,
                        comment="ID должности из справочника positions")
    position = relationship("Position", back_populates="employees",
                          comment="Должность сотрудника")
    
    # Обратная связь с пользователем (один к одному)
    user = relationship("User", back_populates="employee", uselist=False)

class User(Base):
    """
    Таблица пользователей для авторизации
    
    Содержит данные для входа в систему.
    Привязана к сотруднику (1:1).
    
    Особенности:
    - Пароли хранятся в хэшированном виде (никогда в открытом!)
    - role_id — ссылка на роль из справочника
    - is_active — активен ли аккаунт (можно деактивировать без удаления)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, comment="Логин для входа")
    hashed_password = Column(String(128), nullable=False, comment="Хэш пароля (bcrypt)")
    is_active = Column(Boolean, default=True, comment="Активен ли аккаунт")
    
    # Связь с ролью (многие к одному)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False,
                    comment="ID роли из справочника roles")
    role = relationship("Role", back_populates="users",
                      comment="Роль пользователя (определяет права доступа)")
    
    # Связь с сотрудником (один к одному)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False,
                        comment="ID сотрудника из таблицы employees")
    employee = relationship("Employee", back_populates="user",
                          comment="Сотрудник, связанный с этим аккаунтом")
    
    # Метод для верификации пароля
    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)
    
    # Метод для установки пароля
    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)

class Vacation(Base):
    """
    Таблица графика отпусков
    
    Содержит заявки на отпуск сотрудников.
    
    Особенности:
    - Связана со справочником статусов
    - Привязана к сотруднику
    - Содержит период отпуска
    - Поддерживает комментарии для отклоненных заявок
    """
    __tablename__ = "vacations"
    
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False, comment="Дата начала отпуска")
    end_date = Column(Date, nullable=False, comment="Дата окончания отпуска")
    comment = Column(String(255), comment="Комментарий (например, причина отклонения)")
    
    # Связь со сотрудником (многие к одному)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False,
                        comment="ID сотрудника из таблицы employees")
    employee = relationship("Employee", back_populates="vacations",
                          comment="Сотрудник, подавший заявку")
    
    # =============== СВЯЗЬ СО СТАТУСОМ =============== #
    status_id = Column(Integer, ForeignKey("request_statuses.id"), nullable=False,
                      comment="ID статуса из справочника request_statuses")
    status = relationship("RequestStatus", back_populates="vacations",
                        comment="Текущий статус заявки")
    
    # =============== ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА =============== #
    @property
    def duration(self):
        """Возвращает продолжительность отпуска в днях"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_approved(self):
        """Проверяет, одобрен ли отпуск"""
        return self.status.name == "Одобрен"
    
    @property
    def display_color(self):
        """Возвращает цвет для отображения в календаре"""
        return self.status.color