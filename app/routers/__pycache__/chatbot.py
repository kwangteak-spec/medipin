# app/routers/chatbot.py (최종 완성)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.security.jwt_handler import get_current_user
from app.services.chatbot_service import generate_chatbot_response
from app.schemas.chatbot import ChatRequest, ChatResponse 

chatbot_router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@chatbot_router.post("/", response_model=ChatResponse)
def chatbot_query(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    로그인한 주사용자의 질문에 대해 DB 정보를 기반으로 답변합니다.
    (JWT 인증 필요)
    """
    # get_current_user 의존성에서 인증 실패 시 이미 401 오류가 발생하지만, 
    # 로직의 안전성을 위해 None 체크를 유지합니다.
    if current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증되지 않은 사용자입니다."
        )

    try:
        # 챗봇 서비스 함수 호출
        response_text = generate_chatbot_response(
            db, 
            user_id=current_user_id, 
            question=payload.question
        )
    except Exception as e:
        # 서비스 레이어에서 발생한 오류 처리 (예: DB 조회 실패)
        print(f"Chatbot Service Error: {e}")
        # 500 오류를 반환하여 문제 발생을 알립니다.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"챗봇 서비스 처리 중 오류가 발생했습니다: {e}" 
        )
    
    # ChatResponse 스키마에 맞춰 답변 반환
    return {"response": response_text}