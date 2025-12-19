from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from app.models.drug_info import PillIdentifier # 모델 임포트 변경

def get_drugs_by_query(db: Session, query: str):
    """
    검색어(query)를 기반으로 약품을 조회합니다.
    """
    if not query:
        return []

    search_pattern = f"%{query.lower()}%"
    
    stmt = select(
        PillIdentifier.item_seq,      # PK
        PillIdentifier.item_name,     # 품목명
        PillIdentifier.company_name,  # 업체명
        PillIdentifier.form_code_name, # 제형코드이름
        PillIdentifier.item_image     # 이미지
    ).where(
        PillIdentifier.item_name.ilike(search_pattern)
    )

    results = db.execute(stmt).all()
    
    drugs_list = []
    for row in results:
        drugs_list.append({
            "id": row[0],
            "drug_name": row[1],
            "manufacturer": row[2],
            "form_type": row[3],
            "item_image": row[4]
        })
        
    return drugs_list


def get_drug_by_id(db: Session, item_seq: int):
    """
    item_seq(약품 ID)를 기반으로 단일 약품의 상세 정보를 조회합니다.
    """
    
    stmt = select(
        PillIdentifier.item_seq,        # 0
        PillIdentifier.item_name,       # 1
        PillIdentifier.company_name,    # 2
        PillIdentifier.form_code_name,  # 3

        # 🚨 소문자 속성 사용 (매핑된 이름)
        PillIdentifier.etc_otc_name,    # 4
        PillIdentifier.drug_shape,      # 5 
        PillIdentifier.color_class1,    # 6
        PillIdentifier.color_class2,    # 7
        PillIdentifier.print_front,     # 8
        PillIdentifier.leng_long,       # 9
        PillIdentifier.leng_short,      # 10
        PillIdentifier.entp_seq,        # 11
        PillIdentifier.class_name,      # 12
        PillIdentifier.class_no,        # 13
        PillIdentifier.item_image       # 14
    ).where(
        PillIdentifier.item_seq == item_seq
    )
    
    result = db.execute(stmt).first()

    if not result:
        return None

    return {
        "item_seq": result[0],          # 0
        "item_name": result[1],         # 1
        "company_name": result[2],      # 2
        "form_code_name": result[3],    # 3
        
        "etc_otc_name": result[4],      # 4
        "drug_shape": result[5],        # 5
        "color_class1": result[6],      # 6
        "color_class2": result[7],      # 7
        "print_front": result[8],       # 8
        "leng_long": result[9],         # 9
        "leng_short": result[10],       # 10
        "entp_seq": result[11],         # 11
        "class_name": result[12],       # 12
        "class_no": result[13],         # 13
        "item_image": result[14]        # 14
    }