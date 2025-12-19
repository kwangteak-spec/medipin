# app/schemas/medication.py

from pydantic import BaseModel
from typing import List, Optional

class ScheduleEntry(BaseModel):
    """ 등록/수정할 복용 시간과 용량 """
    time: str 
    dosage: Optional[str] = None 

class MedicationRequest(BaseModel):
    """ 복약 일정 등록 요청 스키마 (register_medication_schedule 함수에서 사용) """
    drug_id: int 
    start_date: str # 날짜 문자열 (예: "2025-12-01")
    end_date: Optional[str] = None
    schedules: List[ScheduleEntry] 

class MedicationDeleteRequest(BaseModel):
    """ 복약 일정 삭제 요청 스키마 (delete_medication_schedule 함수에서 사용) """
    active_medication_id: int