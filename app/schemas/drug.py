# app/schemas/drug.py

from pydantic import BaseModel, Field
from typing import Optional

class DrugDetailOut(BaseModel):
    # 기본 식별 정보
    item_seq: int = Field(..., alias="id")                 # 품목일련번호 (ITEM_SEQ)
    item_name: str = Field(..., alias="drug_name")         # 약품명
    company_name: str = Field(..., alias="manufacturer")   # 업체명 (COMPANY_NAME)
    entp_seq: Optional[int] = None                         # 업체일련번호 (ENTP_SEQ)

    # 약품 분류 및 타입 정보
    etc_otc_name: Optional[str] = None                     # 전문/일반 구분 (ETC_OTC_NAME)
    form_code_name: Optional[str] = None                   # 체형 코드 이름 (FORM_CODE_NAME)
    class_name: Optional[str] = None                       # 분류명 (CLASS_NAME)
    class_no: Optional[float] = None                         # 분류번호 (CLASS_NO)

    # 식별 정보 (모양 및 색상)
    drug_shape: Optional[str] = None                       # 의약품 모양 (DRUG_SHAPE)
    color_class1: Optional[str] = None                     # 색깔(앞) (COLOR_CLASS1)
    color_class2: Optional[str] = None                     # 색깔(뒤) (COLOR_CLASS2)
    print_front: Optional[str] = None                      # 표시(앞) (PRINT_FRONT)
    
    # 크기 정보
    leng_long: Optional[float] = None                      # 크기(장축) (LENG_LONG)
    leng_short: Optional[float] = None                     # 크기(단축) (LENG_SHORT)

    # 🚨 약품 사진 URL (미리 등록)
    item_image: Optional[str] = None                       # 사진정보 (ITEM_IMAGE)

    class Config:
        from_attributes = True
        populate_by_name = True