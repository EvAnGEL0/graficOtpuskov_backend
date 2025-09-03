# api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Абсолютные импорты (без точек)
import crud
import schemas
from database import SessionLocal

router = APIRouter()

# Зависимость для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Маршруты ---

@router.get("/schedule", response_model=List[schemas.Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_events(db, skip=skip, limit=limit)

@router.post("/schedule", response_model=schemas.Event, status_code=201)
def create_event_route(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event)

@router.delete("/schedule/{event_id}")
def delete_event_route(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    crud.delete_event(db, event_id)
    return {"status": "ok"}