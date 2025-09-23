from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    last_name = Column(String, index=True)
    first_name = Column(String, index=True)
    middle_name = Column(String, nullable=True)
    hire_date = Column(Date)
    dismissal_date = Column(Date, nullable=True)
    display_color = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Внешние ключи (сделаны nullable=True)
    department_id = Column(Integer, ForeignKey("department_s.id"), nullable=True)
    position_id = Column(Integer, ForeignKey("position_s.id"), nullable=True)
    rank_id = Column(Integer, ForeignKey("rank_s.id"), nullable=True)
    supervisor_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    
    # Связи
    department = relationship("Department_s", back_populates="staff")
    position = relationship("Position_s", back_populates="staff")
    rank = relationship("Rank_s", back_populates="staff")
    supervisor = relationship("Staff", remote_side=[id], back_populates="subordinates")
    subordinates = relationship("Staff", back_populates="supervisor")
    vacation_schedules = relationship("VacationSchedule", back_populates="staff")
    user_account = relationship("User", back_populates="staff", uselist=False)