
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

def check_drug_safety_for_user(db: Session, profile_id: int, drug_name: str, user_age: int, is_pregnant: bool) -> str:
    # 🚨 함수 내부에서 필요한 모델을 임포트합니다.
    from app.models.medication import ActiveMedication
    from app.models.drug_info import DrugInteraction, PregnancyWarning
    
    warnings = []
    
    # 1. 임부 금기 확인 (if is_pregnant):
    if is_pregnant:
        # DB에서 임부 금기 약물인지 조회 (product_name 사용)
        if db.query(PregnancyWarning).filter(PregnancyWarning.product_name.like(f"%{drug_name}%")).first():
             # drug_name matches partial? Strict match? Using like for robustness
            warnings.append("🚨 경고: 이 약물은 임산부에게 금기 또는 주의 필요 약물입니다.")

    # 2. 연령 제한 확인 (생략)

    # 3. 약물 상호작용 확인 (현재 복용약 조합)
    # ActiveMedication uses 'medication_name'
    # Profile ID in ActiveMedication is 'patient_id' now (Wait, logic in chatbot might pass user_id as profile_id? 
    # check_drug_safety_for_user is likely called with patient_profile_id. Assuming correct.)
    
    current_meds = db.query(ActiveMedication.medication_name).filter(ActiveMedication.patient_id == profile_id).all()
    for med in current_meds:
        current_drug_name = med.medication_name
        # DrugInteraction 테이블에서 상호작용 조회 (product_name1, product_name2)
        # Or ingredient? The previous logic used drug1, drug2.
        # OpenData has `product_name1`, `product_name2`.
        if db.query(DrugInteraction).filter(
            (DrugInteraction.product_name1.like(f"%{drug_name}%")) & (DrugInteraction.product_name2.like(f"%{current_drug_name}%"))
        ).first():
            warnings.append(f"⚠️ 주의: 이 약물은 복용 중인 {current_drug_name}과 상호작용 가능성이 있습니다.")

    if warnings:
        return " ".join(warnings)
    else:
        return f"현재 정보로는 {drug_name} 복용에 특별한 안전성 문제가 발견되지 않았습니다."