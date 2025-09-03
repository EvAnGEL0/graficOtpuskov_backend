# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Подключаемся к SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./schedule.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)