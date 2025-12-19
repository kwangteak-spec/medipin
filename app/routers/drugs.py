from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List 
# ----------------------------------------------------

from app.db import get_db
# 🚨 수정: drugs.py는 현재 사용자를 식별하는 get_current_user만 필요합니다.
#    create_token_pair, verify_refresh_token은 auth.py에서만 사용됩니다.
from app.security.jwt_handler import get_current_user 

# 서비스 임포트
from app.services.drug_service import get_drugs_by_query, get_drug_by_id 
from app.services.medication_service import register_medication_schedule, delete_medication_schedule

# 스키마 임포트 (drug.py가 있으므로 직접 임포트)
from app.schemas.medication import MedicationRequest, MedicationDeleteRequest 
from app.schemas.drug import DrugDetailOut 

# 🚨 라우터 인스턴스 정의
drugs_router = APIRouter(prefix="/drugs", tags=["Drugs"])
# =======================================================
# 1. 약품 검색 (Search) 엔드포인트
# =======================================================
@drugs_router.get("/search", response_model=List[dict]) 
def search_drugs(q: str, db: Session = Depends(get_db)):
    """ 검색 쿼리(q)를 기반으로 약품 목록을 조회합니다. """
    
    drugs_list = get_drugs_by_query(db, q) 
    
    if not drugs_list:
        return [] 
        
    return drugs_list
    
# =======================================================
# 2. 약품 상세 정보 조회 (Detail) 엔드포인트
# =======================================================
@drugs_router.get(
    "/{item_seq}", # URL 경로 매개변수
    response_model=DrugDetailOut, # 상세 정보 출력 스키마 사용
    status_code=status.HTTP_200_OK
)
def get_drug_details(item_seq: int, db: Session = Depends(get_db)):
    """
    특정 약품 ID(item_seq)에 대한 상세 정보를 조회합니다.
    """
    drug = get_drug_by_id(db, item_seq) 
    
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with item_seq {item_seq} not found"
        )
    return drug

# =======================================================
# 3. 복약 일정 등록 엔드포인트 (POST /drugs/schedule)
# =======================================================
@drugs_router.post("/schedule", status_code=status.HTTP_201_CREATED)
def register_schedule(
    req: MedicationRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user) # JWT 인증 필요
):
    """ 새로운 복약 정보를 등록합니다. """
    try:
        active_med = register_medication_schedule(db, user_id, req)
        return {"message": "복약 일정이 성공적으로 등록되었습니다.", "active_medication_id": active_med.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"등록 중 오류 발생: {e}")

# =======================================================
# 4. 복약 일정 삭제 엔드포인트 (DELETE /drugs/schedule/{id})
# =======================================================
@drugs_router.delete("/schedule/{active_medication_id}")
def delete_schedule(
    active_medication_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user) # JWT 인증 필요
):
    """ 특정 ID의 복약 일정을 삭제합니다. """
    
    if delete_medication_schedule(db, active_medication_id, user_id):
        return {"message": f"복약 일정 ID {active_medication_id}가 성공적으로 삭제되었습니다."}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="해당 ID의 복약 일정을 찾을 수 없거나 삭제 권한이 없습니다."
    )