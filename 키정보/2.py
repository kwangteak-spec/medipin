import pandas as pd

# 1. CSV 파일 로드 (인코딩은 'cp949' 또는 'utf-8' 사용)
csv_file = '한국의약품안전관리원_노인주의약물_20240813.csv'
try:
    df = pd.read_csv(csv_file, encoding='cp949')
except UnicodeDecodeError:
    df = pd.read_csv(csv_file, encoding='utf-8')

# 2. 주요 분석 컬럼 선택
# 제품코드: Primary Key 후보
# 제품명: 처방전 매칭용
# 약품상세정보: 부작용/위해성 분류 및 상세 정보 (가장 중요한 컬럼)
caution_df = df[['제품명', '제품코드', '성분명', '약품상세정보']]

# 3. 노인 및 기저질환 위험 키워드 정의
# (낙상, 치매, 저혈압 등 노인 및 기저질환자에게 치명적인 부작용 키워드)
risk_keywords = ['낙상', '골절', '치매', '인지기능', '뇌혈관질환', '저혈압', '섬망']

# 4. 취약 계층 위험 약품 추출 함수
def find_risky_drugs_by_keyword(dataframe, keywords):
    """
    '약품상세정보'에서 특정 위험 키워드를 포함하는 약품을 추출합니다.
    """
    # 키워드를 '|'로 연결하여 정규식 패턴 생성 (예: '낙상|골절|치매...')
    pattern = '|'.join(keywords) 
    # na=False: 내용이 없는 행은 제외
    result = dataframe[dataframe['약품상세정보'].str.contains(pattern, na=False)]
    return result

# 5. 추출 실행 및 결과 출력
risky_drugs = find_risky_drugs_by_keyword(caution_df, risk_keywords)

print(f"🔍 노인 및 기저질환 위험 키워드({', '.join(risk_keywords)}) 포함 약품: 총 {len(risky_drugs)}건")
print("-" * 70)
print("📌 추출된 약품 목록 (상위 10개)")
print("-" * 70)

# 추출된 데이터 중 제품명과 위험 사유만 출력
print(risky_drugs[['제품명', '약품상세정보']].head(10).to_string(index=False)) 

# 6. 처방전 약품 부작용 확인 기능 예시
def check_prescription_side_effect(prescription_drug_name):
    """
    처방받은 약품명에 대한 상세 주의 정보를 확인합니다.
    """
    # 처방전의 약품명과 제품명 컬럼을 매칭 (부분 일치 검색)
    matched = caution_df[caution_df['제품명'].str.contains(prescription_drug_name, na=False)]
    
    print("\n[처방전 약품 주의 정보 확인]")
    if not matched.empty:
        print(f"⚠️ 경고! 처방받은 약품 '{prescription_drug_name}'은(는) 노인 주의 약물입니다.")
        for index, row in matched.iterrows():
            print(f"   - 제품명: {row['제품명']}")
            print(f"   - 성분명: {row['성분명']}")
            # 부작용 분류 칼럼인 약품상세정보 출력
            print(f"   - 주요 위험 사유 (분류 칼럼): {row['약품상세정보']}")
    else:
        print(f"✅ '{prescription_drug_name}'과(와) 일치하는 노인 주의 약물 정보는 발견되지 않았습니다.")

# 테스트: 처방전에 '빅손정'이 있다고 가정하고 검사
# (데이터 스니펫에서 '빅손정'은 '낙상, 골절' 위험이 있는 것으로 확인됨)
check_prescription_side_effect("빅손정")