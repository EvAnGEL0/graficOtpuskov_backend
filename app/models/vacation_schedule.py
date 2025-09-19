from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class VacationSchedule(Base):
    __tablename__ = "vacation_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    main_vacation_days = Column(Integer, nullable=False)  # Количество суток из основного отпуска
    
    # Связь с сотрудником
    staff = relationship("Staff", back_populates="vacation_schedules")