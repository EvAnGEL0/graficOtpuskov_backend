from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base


class Rank_s (Base):
    __tablename__ = "rank_s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    staff = relationship("Staff", back_populates="rank")