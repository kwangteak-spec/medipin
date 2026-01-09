# app/schemas/chatbot.py (신규 파일)

from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    """ 챗봇에게 질문할 내용을 담는 요청 스키마 """
    question: str
    conversation_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    """ 챗봇의 답변을 담는 응답 스키마 """
    response: str
    conversation_id: Optional[str] = None

class ScheduleEntry(BaseModel):
    """ 등록/수정할 복용 시간과 용량 """
    time: str # 예: "14:00"
    dosage: Optional[str] = None # 예: "1정"

class MedicationRequest(BaseModel):
    """ 복약 일정 등록 요청 스키마 """
    drug_id: int 
    start_date: str # 날짜 문자열 (예: "2025-12-01")
    end_date: Optional[str] = None
    schedules: List[ScheduleEntry] 

class MedicationDeleteRequest(BaseModel):
    """ 복약 일정 삭제 요청 스키마 """
    active_medication_id: int
    
