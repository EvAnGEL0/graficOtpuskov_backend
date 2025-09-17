from sqlalchemy import Column, Integer, String
from app.config.database import Base


class Position_s (Base):
    __tablename__ = "position_s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
  