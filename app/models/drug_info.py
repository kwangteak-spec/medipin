from sqlalchemy import Column, Integer, String, Text, BigInteger, Float
from app.db import Base

# 1. 자체 관리 약물 정보
class Drug(Base):
    __tablename__ = "drugs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    ingredient = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    caution = Column(Text, nullable=True)
    interaction = Column(Text, nullable=True)

# 2. 공공데이터: 연령 금기
class AgeLimit(Base):
    __tablename__ = "age_limit"
    # No Primary Key defined in schema, assuming '제품코드' or composite might be unique, but SQLAlchemy needs a PK.
    # If schema doesn't have PK, we might map to an existing rowid or use one of the columns as PK if unique.
    # Usually '제품코드' is unique per distinct product, but maybe not in this warning table.
    # I will stick to schema but add a dummy pk if necessary, or assume one.
    # However, SQLAlchemy models REQUIRE a primary key.
    # I will attempt to use `성분코드` + `제품코드` or similar, or just map without PK if I read only?
    # No, SQLAlchemy requires PK. I will assume `제품코드` is PK for now, or use a composite.
    # Let's check `product_license`: `No` is bigint.
    # OpenData tables usually don't have a clean PK.
    # I will add a synthetic ID if needed, or pick a likely candidate.
    # For `age_limit`, `제품코드` might be repeated?
    # Let's inspect schema: `age_limit` has no PRIMARY KEY defined.
    # I will add `__mapper_args__ = {"primary_key": [...]}` to trick SA if needed, or pretend `제품코드` is PK.
    # Better: Inspect if there's a rownum or similar. `pill_identifier` has 'rownum'. `age_limit` does not.
    # I'll define `제품코드` as primary_key=True for now to make SA happy, even if not strictly unique in DB (SA just needs to know what to identify by).
    
    ingredient_name = Column("성분명", Text)
    ingredient_code = Column("성분코드", Text, primary_key=True) # Making this part of PK?
    product_code = Column("제품코드", BigInteger, primary_key=True)
    product_name = Column("제품명", Text)
    company_name = Column("업체명", Text)
    specific_age = Column("특정연령", BigInteger)
    specific_age_unit = Column("특정연령단위", Text)
    salary_type = Column("급여구분", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)
    details = Column("상세정보", Text)

# 3. 공공데이터: 수유부 금기
class Breastfeeding(Base):
    __tablename__ = "breastfeeding"
    ingredient_code = Column("성분코드", Text, primary_key=True)
    ingredient_name = Column("성분명", Text)
    product_code = Column("제품코드", BigInteger, primary_key=True)
    product_name = Column("제품명", Text)
    company_name = Column("업체명", Text)
    salary_type = Column("급여구분", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)
    remarks = Column("비고", Text)

# 4. 공공데이터: 위험 의약품
class DangerDrug(Base):
    __tablename__ = "danger_drug"
    product_name = Column("제품명", Text)
    std_code = Column("표준코드", BigInteger, primary_key=True)
    item_seq = Column("품목기준코드", BigInteger)
    recall_manager = Column("회수의무자", Text)
    recall_date = Column("회수일자", Text)
    make_no = Column("제조번호", Text, primary_key=True)
    make_date = Column("제조일자(사용일자)", Text)
    recall_reason = Column("회수사유", Text)
    risk_grade = Column("위험등급", Float)
    recall_end_date = Column("회수종료일자", Text)

# 5. 공공데이터: 용량 주의
class DoseLimit(Base):
    __tablename__ = "dose_limit"
    product_code = Column("제품코드", BigInteger, primary_key=True)
    product_name = Column("제품명", Text)
    ingredient_code = Column("성분코드", Text, primary_key=True)
    ingredient_name = Column("성분명", Text)
    max_dose_1day = Column("1일최대투여량", Text)
    max_dose_criteria = Column("1일최대 투여기준량", Float)
    check_criteria = Column("점검기준 성분함량 (총함량)", Float)
    salary_type = Column("급여구분", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)

# 6. 공공데이터: 약물 상호작용
class DrugInteraction(Base):
    __tablename__ = "drug_interaction"
    ingredient_name1 = Column("성분명1", Text)
    ingredient_code1 = Column("성분코드1", Text, primary_key=True)
    product_code1 = Column("제품코드1", BigInteger, primary_key=True)
    product_name1 = Column("제품명1", Text)
    company_name1 = Column("업체명1", Text)
    salary_type1 = Column("급여구분1", Text)
    ingredient_name2 = Column("성분명2", Text)
    ingredient_code2 = Column("성분코드2", Text, primary_key=True)
    product_code2 = Column("제품코드2", BigInteger, primary_key=True)
    product_name2 = Column("제품명2", Text)
    company_name2 = Column("업체명2", Text)
    salary_type2 = Column("급여구분2", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)
    prohibit_reason = Column("금기사유", Text)

# 7. 공공데이터: 효능군 중복
class DuplicateEfficacy(Base):
    __tablename__ = "duplicate_efficacy"
    efficacy_group = Column("효능군", Text)
    group_div = Column("그룹구분", Text)
    general_code = Column("일반명코드", Text)
    ingredient_code = Column("성분코드", Text, primary_key=True)
    ingredient_name = Column("성분명", Text)
    product_code = Column("제품코드", Text, primary_key=True)
    product_name = Column("제품명", Text)
    company_name = Column("업체명", Text)
    salary_type = Column("급여구분", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)

# 8. 공공데이터: 투여 기간 주의
class DurationWarning(Base):
    __tablename__ = "duration_warning"
    product_code = Column("제품코드", BigInteger, primary_key=True)
    product_name = Column("제품명", Text)
    ingredient_code = Column("성분코드", Text, primary_key=True)
    ingredient_name = Column("성분명", Text)
    max_days = Column("최대투여기간일수", BigInteger)
    notice_date = Column("공고일자", Text)
    notice_no = Column("공고번호", BigInteger)
    salary_type = Column("급여구분", Text)

# 9. 공공데이터: 임신부 금기
class PregnancyWarning(Base):
    __tablename__ = "pregnancy_warning"
    ingredient_name = Column("성분명", Text)
    ingredient_code = Column("성분코드", Text, primary_key=True)
    product_code = Column("제품코드", BigInteger, primary_key=True)
    product_name = Column("제품명", Text)
    company_name = Column("업체명", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)
    salary_type = Column("급여구분", Text)
    grade = Column("금기등급", Text)
    details = Column("상세정보", Text)

# 10. 공공데이터: 폼목 허가 정보 (Product License)
class ProductLicense(Base):
    __tablename__ = "product_license"
    no = Column("No", BigInteger, primary_key=True) # Assuming No is unique
    item_seq = Column("품목기준코드 [ITEM_SEQ]", BigInteger)
    item_name = Column("품목명 [ITEM_NAME]", Text)
    item_eng_name = Column("영문제품명 [ITEM_ENG_NAME]", Text)
    entp_name = Column("업체명 [ENTP_NAME]", Text)
    entp_eng_name = Column("영문업체명 [ENTP_ENG_NAME]", Text)
    entp_seq = Column("업일련번호 [ENTP_SEQ]", BigInteger)
    entp_no = Column("업허가번호 [ENTP_NO]", BigInteger)
    permit_date = Column("품목허가일자 [ITEM_PERMIT_DATE]", BigInteger)
    induty = Column("업종 [INDUTY]", Text)
    std_code = Column("품목일련번호 [PRDLST_STDR_CODE]", BigInteger)
    spclty_pblc = Column("전문/일반구분 [SPCLTY_PBLC]", Text)
    product_type = Column("분류명 [PRDUCT_TYPE]", Text)
    permit_no = Column("품목허가번호 [PRDUCT_PRMISN_NO]", BigInteger)
    ingr_name = Column("주성분 [ITEM_INGR_NAME]", Text)
    ingr_cnt = Column("주성분수 [ITEM_INGR_CNT]", Float)
    big_img_url = Column("큰제품이미지 [BIG_PRDT_IMG_URL]", Text)
    permit_kind = Column("신고/허가구분 [PERMIT_KIND_CODE]", Text)
    cancel_date = Column("취하일자 [CANCEL_DATE]", Float)
    cancel_name = Column("취하구분 [CANCEL_NAME]", Text)
    edi_code = Column("보험코드 [EDI_CODE]", Text)
    bizrno = Column("사업자등록번호 [BIZRNO]", Float)
    rownum = Column("rownum", BigInteger)

# 11. 공공데이터: 노인 주의
class SeniorWarning(Base):
    __tablename__ = "senior_warning"
    ingredient_name = Column("성분명", Text)
    ingredient_code = Column("성분코드", Text, primary_key=True)
    product_code = Column("제품코드", BigInteger, primary_key=True)
    product_name = Column("제품명", Text)
    company_name = Column("업체명", Text)
    notice_no = Column("공고번호", BigInteger)
    notice_date = Column("공고일자", Text)
    salary_type = Column("급여구분", Text)
    details = Column("약품상세정보", Text)

# 12. 공공데이터: 낱알 식별
class PillIdentifier(Base):
    __tablename__ = "pill_identifier"
    # Assuming ITEM_SEQ is unique enough or combining with others.
    # Schema has No, ITEM_SEQ...
    no = Column("No", BigInteger)
    item_seq = Column("ITEM_SEQ", BigInteger, primary_key=True)
    item_name = Column("ITEM_NAME", Text)
    entp_seq = Column("ENTP_SEQ", BigInteger)
    company_name = Column("COMPANY_NAME", Text)
    chart = Column("성상 [CHART]", Text)
    item_image = Column("ITEM_IMAGE", Text)
    print_front = Column("PRINT_FRONT", Text)
    print_back = Column("PRINT_BACK", Text)
    drug_shape = Column("DRUG_SHAPE", Text)
    color_class1 = Column("COLOR_CLASS1", Text)
    color_class2 = Column("COLOR_CLASS2", Text)
    line_front = Column("분할선(앞) [LINE_FRONT]", Text)
    line_back = Column("분할선(뒤) [LINE_BACK]", Text)
    leng_long = Column("LENG_LONG", Text)
    leng_short = Column("LENG_SHORT", Text)
    thick = Column("크기(두께) [THICK]", Text)
    img_regist_ts = Column("약학정보원 이미지 생성일 [IMG_REGIST_TS]", BigInteger)
    class_no = Column("CLASS_NO", Float)
    class_name = Column("CLASS_NAME", Text)
    etc_otc_name = Column("ETC_OTC_NAME", Text)
    permit_date = Column("품목허가일자 [ITEM_PERMIT_DATE]", BigInteger)
    form_code_name = Column("FORM_CODE_NAME", Text)
    mark_front_anal = Column("마크내용(앞) [MARK_CODE_FRONT_ANAL]", Text)
    mark_back_anal = Column("마크내용(뒤) [MARK_CODE_BACK_ANAL]", Text)
    mark_img_front = Column("마크이미지(앞) [MARK_CODE_FRONT_IMG]", Text)
    mark_img_back = Column("마크이미지(뒤) [MARK_CODE_BACK_IMG]", Text)
    item_eng_name = Column("품목영문명 [ITEM_ENG_NAME]", Text)
    change_date = Column("변경일 [CHANGE_DATE]", Float)
    mark_code_front = Column("마크코드(앞) [MARK_CODE_FRONT]", Text)
    mark_code_back = Column("마크코드(뒤) [MARK_CODE_BACK]", Text)
    edi_code = Column("보험코드 [EDI_CODE]", Text)
    bizrno = Column("사업자등록번호 [BIZRNO]", BigInteger)
    std_code = Column("표준코드 [STD_CD]", Text)
    rownum = Column("rownum", BigInteger)
