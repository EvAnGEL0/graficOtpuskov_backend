from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base


class Role_s (Base):
    __tablename__ = "role_s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="role")