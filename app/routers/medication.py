from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date as date_type, datetime
from app.db import get_db
from app.models.medication import MedicationSchedule

router = APIRouter(prefix="/medication", tags=["Medication"])

# Request Schema
class ScheduleCreate(BaseModel):
    user_id: int
    pill_name: str
    dose: str
    date: date_type
    start_date: Optional[date_type] = None
    end_date: Optional[date_type] = None
    timing: Optional[str] = None
    meal_relation: Optional[str] = None
    memo: Optional[str] = None
    notify: bool = True

class ScheduleResponse(BaseModel):
    id: int
    user_id: int
    pill_name: Optional[str]
    dose: Optional[str]
    date: Optional[date_type]
    start_date: Optional[date_type]
    end_date: Optional[date_type]
    timing: Optional[str]
    meal_relation: Optional[str]
    memo: Optional[str]
    notify: Optional[bool]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

@router.post("/schedule", response_model=ScheduleResponse)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = MedicationSchedule(
        user_id=schedule.user_id,
        pill_name=schedule.pill_name,
        dose=schedule.dose,
        date=schedule.date,
        start_date=schedule.start_date,
        end_date=schedule.end_date,
        timing=schedule.timing,
        meal_relation=schedule.meal_relation,
        memo=schedule.memo,
        notify=schedule.notify
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/schedule", response_model=List[ScheduleResponse])
def get_schedules(
    user_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MedicationSchedule)
    
    if user_id:
        query = query.filter(MedicationSchedule.user_id == user_id)
    
    if year and month:
        # Simple Filter: Extract month/year from 'date' column
        # Note: This checks the specific `date` column. 
        # If the user wants to check events overlapping date ranges (start_date ~ end_date), 
        # logic would be different.
        # Given the schema has `date` AND `start/end_date`, `date` likely means "The specific target date" 
        # OR "Create Date"? 
        # The prompt image says `date` has a value.
        # Use simple date extraction filter compatible with common DBs
        from sqlalchemy import extract
        query = query.filter(extract('year', MedicationSchedule.date) == year)
        query = query.filter(extract('month', MedicationSchedule.date) == month)

    return query.all()
