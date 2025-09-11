# database/models/todo.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(300))
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))