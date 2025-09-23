from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    id_role_s = Column(Integer, ForeignKey("role_s.id"), nullable=False)
    id_staff = Column(Integer, ForeignKey("staff.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Связи
    role = relationship("Role_s", back_populates="users")
    staff = relationship("Staff", back_populates="user_account")