# schemas.py
from pydantic import BaseModel
from datetime import date

class EventCreate(BaseModel):
    name: str
    startDate: date
    endDate: date
    color: str = "#3498db"

class Event(EventCreate):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2