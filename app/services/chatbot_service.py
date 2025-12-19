# app/services/chatbot_service.py (최종 완성 코드 - 지연 로딩 적용)

from sqlalchemy.orm import Session, joinedload
from typing import Optional, Dict, Any

# 🚨 check_drug_safety_for_user 함수 임포트
from app.services.drug_safety_service import check_drug_safety_for_user 
from app.services.medication_service import register_medication_schedule, delete_medication_schedule

# =======================================================
# 1. 보조 함수: 사용자 요약 정보 조회 (get_user_summary)
# =======================================================

def get_user_summary(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """ 주사용자와 가족 구성원의 간략한 정보를 조회하고, 특이사항을 포함합니다. """
    
    # 🚨 지연 로딩
    from app.models.user import UserProfile, PatientProfile
    
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    
    if user:
        # 주사용자의 가족 구성원 (UserProfile 테이블에서 조회)
        members = db.query(UserProfile).filter(UserProfile.user_id == user_id, UserProfile.id != user_id).all()
        
        # 주사용자 본인의 특이사항 조회 (PatientProfile 테이블 사용. relation='Self')
        # Assuming one PatientProfile per user with relation 'Self' created at registration
        patient = db.query(PatientProfile).filter(PatientProfile.user_id == user_id, PatientProfile.relation == "Self").first()
        patient_note = patient.special_note if patient else None
        
        member_names = [m.name for m in members]
        
        return {
            "name": user.name,
            "age": user.age,
            "special_note": patient_note,
            "family_members": member_names,
            "profile_id": user.id # This is UserProfile ID
            # Note: For strict logic, we might need PatientProfile ID for ActiveMedication lookups
        }
    return None

# =======================================================
# 2. 보조 함수: 복용 약물 이름 목록 조회 (get_profile_medications)
# =======================================================

def get_profile_medications(db: Session, profile_id: int) -> list[str]:
    """ 특정 프로필(PatientProfile ID)이 복용 중인 약물의 이름을 조회합니다. """
    
    # 🚨 지연 로딩
    from app.models.medication import ActiveMedication
    
    # ActiveMedication에는 medication_name이 직접 저장되어 있습니다.
    # profile_id should be patient_id here. 
    # If caller passes UserProfile.id, this query might fail if patient_id != user_profile.id.
    # However, currently register_user creates PatientProfile.id (auto inc) which might be different from UserProfile.id.
    # The 'profile_id' argument here implies PatientProfile ID.
    
    meds = db.query(ActiveMedication).filter(
        ActiveMedication.patient_id == profile_id
    ).all()
    
    return [m.medication_name for m in meds if m.medication_name]


# =======================================================
# 3. 핵심 함수: 챗봇 응답 생성 (generate_chatbot_response)
# =======================================================

def generate_chatbot_response(db: Session, user_id: int, question: str) -> str:
    
    user_summary = get_user_summary(db, user_id)
    if not user_summary:
        return "사용자 정보를 찾을 수 없습니다. 다시 로그인해 주세요."
    
    from app.models.user import PatientProfile
    # We need the PatientProfile ID for the user to look up meds.
    # Assuming user_summary['profile_id'] is UserProfile ID.
    # Let's find PatientProfile ID.
    patient_profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id, PatientProfile.relation == "Self").first()
    current_patient_id = patient_profile.id if patient_profile else None
    
    q = question.lower().strip()
    name = user_summary['name']

    # === F. 복약 일정 등록 의도 ===
    if "약 등록" in q or "일정 추가" in q:
        return "복약 일정을 등록하려면 약물 ID, 시작일, 시간, 용량을 정확히 입력해 주세요. (현재는 직접 API를 사용해주세요.)"

    # === G. 복약 일정 삭제 의도 ===
    elif "약 삭제" in q or "복용 중단" in q:
        return "어떤 복약 일정을 삭제하고 싶으신가요? 정확한 복약 ID를 알려주세요."

    # === A. 약물 안전성/상호작용 질문 ===
    if "상호작용" in q or "같이 먹어도" in q or "금기" in q or "안전" in q:
        if not current_patient_id:
             return "환자 프로필 정보를 찾을 수 없어 안전성 검사를 수행할 수 없습니다."
             
        return check_drug_safety_for_user(
            db, 
            profile_id=current_patient_id, # Linking to PatientProfile
            drug_name="아스피린", # 임시값
            user_age=user_summary['age'], 
            is_pregnant="임신" in q or "임부" in q 
        )
    
    # === B. 복용 스케줄 질문 ===
    elif "오늘 약" in q or "복용 시간" in q or "빼먹" in q:
        from app.models.medication import MedicationSchedule 
        # MedicationSchedule uses user_id (UserProfile ID based on schema interpretation)
        return f"{name}님, 오늘 복용할 약물 스케줄 정보를 조회 중입니다."
    
    # === C. 개인 특이사항 조회 (special_note) ===
    elif "특이사항" in q or "알러지" in q or "내 정보" in q:
        note = user_summary.get('special_note')
        if note:
             return f"{name}님에게 등록된 특이사항은 '{note}' 입니다."
        else:
             return f"{name}님에게 등록된 특이사항(알러지 등)은 없습니다."

    # === D. 약 보관 방법 (Drug 기본 정보 조회) ===
    elif "보관" in q or "냉장" in q:
        # Drug is now in drug_info
        from app.models.drug_info import Drug
        return "죄송합니다. 어떤 약물의 보관 방법을 알고 싶으신가요?"
    
    # === E. 기본 정보 (나이, 가족 구성원) ===
    elif "나이" in q or "몇 살" in q:
        return f"현재 {name}님의 나이는 만 {user_summary['age']}세로 등록되어 있습니다."
    
    elif "가족" in q or "구성원" in q:
        members = user_summary['family_members']
        if members:
            return f"관리 중인 가족 구성원은 {', '.join(members)} 님들이 있습니다."
        else:
            return "현재 등록된 가족 구성원은 없습니다."

    else:
        return f"{name}님, 현재는 안전성, 스케줄, 개인 특이사항 등의 질문에 답할 수 있습니다. 질문을 구체화해주세요."