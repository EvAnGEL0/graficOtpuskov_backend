from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class Department_s (Base):
    __tablename__ = "department_s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    # Обратная связь
    staff = relationship("Staff", back_populates="departments")