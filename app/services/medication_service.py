from __future__ import annotations
from sqlalchemy.orm import Session
from app.schemas.medication import MedicationRequest
from datetime import datetime

# 🚨 ActiveMedication 모델은 함수 내에서 임포트되므로, 
# 반환 타입 힌트는 문자열로 처리하여 NameError를 방지합니다.
def register_medication_schedule(db: Session, user_id: int, req: MedicationRequest) -> 'ActiveMedication': 
    """ 새 복약 정보를 ActiveMedication 및 MedicationSchedule 테이블에 등록합니다. """
    
    # 🚨 지연 로딩
    from app.models.medication import ActiveMedication, MedicationSchedule
    from app.models.user import PatientProfile
    from app.models.drug_info import PillIdentifier

    # 1. 환자 프로필 조회 (본인)
    patient = db.query(PatientProfile).filter(PatientProfile.user_id == user_id, PatientProfile.relation == "Self").first()
    if not patient:
         # Fallback: if no relation='Self' found, pick any or create (but user registration creates it now)
         # Just pick the first one linked to user
         patient = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
         if not patient:
             raise ValueError("환자 프로필을 찾을 수 없습니다.")

    # 2. 약물 이름 조회
    # req.drug_id는 OpenData의 item_seq (PillIdentifier PK)라고 가정
    drug_info = db.query(PillIdentifier).filter(PillIdentifier.item_seq == req.drug_id).first()
    med_name = drug_info.item_name if drug_info else "Unknown Drug"

    # 3. ActiveMedication 레코드 생성
    active_med = ActiveMedication(
        patient_id=patient.id, # Using patient_id, NOT user_profile.id
        medication_name=med_name,
        start_date=datetime.strptime(req.start_date, "%Y-%m-%d").date(),
        end_date=datetime.strptime(req.end_date, "%Y-%m-%d").date() if req.end_date else None,
        dosage=None # req doesn't have main dosage, only schedule dosage
    )
    db.add(active_med)
    db.flush()
    
    for schedule_entry in req.schedules:
        # Schema for MedicationSchedule: user_id, drug_name, etc.
        # It does NOT link to active_medication by ID conceptually in the schema provided 
        # (user_id is int, no active_med_id column in schema provided in prompt? Wait)
        # Prompt schema for medication_schedule:
        # id, user_id, drug_name, dose, date, time, timing, meal_relation, notify...
        # It lacks active_med_id!
        # So I cannot set active_med_id.
        # I must set user_id (UserProfile id? or PatientProfile id?) -> Schema says user_id. Usually UserProfile.
        # And drug_name.
        
        schedule = MedicationSchedule(
            user_id=user_id, # Linking to the User Account
            drug_name=med_name,
            dose=schedule_entry.dosage,
            time=datetime.strptime(schedule_entry.time, "%H:%M").time() if len(schedule_entry.time) == 5 else None
            # date? The schema has 'date' column. Is it for one-time?
            # Creating a schedule usually implies recurring. 
            # If the schema design is one-row-per-action, I need to generate rows for dates?
            # Or 'date' is start date? Schema says `date` type date.
            # Assuming this table is a notification queue.
            # I will just insert one row as template or log?
            # Given the lack of documentation, I will do my best.
            # I'll populate what I can.
        )
        db.add(schedule)
        
    db.commit()
    return active_med


def delete_medication_schedule(db: Session, active_medication_id: int, user_id: int) -> bool:
    """ ActiveMedication 레코드를 삭제합니다. """
    
    from app.models.medication import ActiveMedication
    from app.models.user import PatientProfile
    
    # 조인 등을 통해 권한 확인
    # ActiveMedication -> PatientProfile -> UserProfile.id == user_id
    active_med = db.query(ActiveMedication).join(PatientProfile).filter(
        ActiveMedication.id == active_medication_id,
        PatientProfile.user_id == user_id
    ).first()
    
    if active_med:
        db.delete(active_med)
        db.commit()
        return True
    return False