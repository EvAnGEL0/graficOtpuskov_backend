from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, index=True)      # Фамилия
    first_name = Column(String, index=True)     # Имя
    middle_name = Column(String, nullable=True) # Отчество
    hire_date = Column(Date)                    # Дата трудоустройства
    dismissal_date = Column(Date, nullable=True) # Дата увольнения
    display_color = Column(String, nullable=True) # Цвет отображения
    is_active = Column(Boolean, default=True)   # Активен ли сотрудник
    
    # Внешние ключи
    department_id = Column(Integer, ForeignKey("department_s.id"))
    position_id = Column(Integer, ForeignKey("position_s.id"))
    rank_id = Column(Integer, ForeignKey("rank_s.id"))
    supervisor_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    
    # Связи
    department = relationship("Department", back_populates="staff")
    position = relationship("Position", back_populates="staff")
    rank = relationship("Rank", back_populates="staff")
    supervisor = relationship("Staff", remote_side=[id], back_populates="subordinates")
    subordinates = relationship("Staff", back_populates="supervisor")