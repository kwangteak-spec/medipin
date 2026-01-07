from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.db import get_db
from app.models.alarm import Alarm

router = APIRouter(prefix="/alarms", tags=["Alarms"])

class AlarmResponse(BaseModel):
    id: int
    user_id: int
    schedule_id: int
    alarm_time: datetime
    message: str
    is_read: bool
    
    # Joined fields
    pill_name: str = None
    is_taken: bool = None
    
    class Config:
        from_attributes = True

from app.security.jwt_handler import get_current_user
from app.models.user import UserProfile

@router.get("/pending", response_model=List[AlarmResponse])
def get_pending_alarms(user_id: int = None, current_user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    현재 시간 이전에 발생했으나 아직 확인하지 않은 알림 조회
    사용자 ID는 토큰에서 추출하여 보안 강화
    """
    now = datetime.now()
    
    # 요청된 user_id와 토큰의 user_id가 다르면 에러 또는 토큰 기준 강제
    real_user_id = current_user.id
    
    alarms = db.query(Alarm).filter(
        Alarm.user_id == real_user_id,
        Alarm.is_read == False,
        Alarm.alarm_time <= now
    ).order_by(Alarm.alarm_time.asc()).all()
    
    return alarms

@router.get("/history", response_model=List[AlarmResponse])
def get_alarm_history(user_id: int = None, current_user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    전체 알림 내역 조회 (최신순 정렬)
    약 이름, 복용 여부(is_taken) 포함
    """
    from app.models.medication import MedicationSchedule
    
    real_user_id = current_user.id
    
    results = db.query(Alarm, MedicationSchedule.pill_name, MedicationSchedule.is_taken)\
        .join(MedicationSchedule, Alarm.schedule_id == MedicationSchedule.id)\
        .filter(Alarm.user_id == real_user_id)\
        .order_by(Alarm.alarm_time.desc())\
        .all()
    
    response_list = []
    for alarm, pill_name, is_taken in results:
        # Pydantic 모델로 매핑
        resp = AlarmResponse.model_validate(alarm)
        resp.pill_name = pill_name
        resp.is_taken = is_taken
        response_list.append(resp)
        
    return response_list

@router.post("/{alarm_id}/read")
def mark_alarm_read(alarm_id: int, db: Session = Depends(get_db)):
    """
    알림을 읽음(완료) 상태로 변경
    + 연동된 스케줄의 is_taken도 True로 업데이트 (사용자 요구사항 반영: '확인' 시 '복용 완료' 처리)
    """
    from app.models.medication import MedicationSchedule

    alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    alarm.is_read = True
    
    # 2026-01-06: 알림 확인 시 복용 완료(is_taken=True)로 자동 업데이트하는 옵션 로직 추가
    schedule = db.query(MedicationSchedule).filter(MedicationSchedule.id == alarm.schedule_id).first()
    if schedule:
        schedule.is_taken = True
        
    db.commit()
    return {"status": "success", "message": "Alarm marked as read and taken"}
