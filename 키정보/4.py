import pandas as pd
import numpy as np

# 현재 업로드된 수유부주의 약물 파일 로드 (인코딩 처리)
csv_file = '한국의약품안전관리원_수유부주의_20240121.csv'
try:
    df_lactating = pd.read_csv(csv_file, encoding='cp949')
except UnicodeDecodeError:
    df_lactating = pd.read_csv(csv_file, encoding='utf-8')

# -----------------
# 1. 데이터 클리닝 및 키 컬럼 확인
# -----------------
# NaN 값을 '정보 없음'으로 대체하여 검색 오류 방지
df_lactating = df_lactating.fillna('정보 없음')

# -----------------
# 2. 취약 계층 위험 정보 추출 (수유부)
# -----------------
def check_lactating_risk(prescription_name, df_data):
    """
    처방전 약품명이 수유부 주의/금기 약물 리스트에 있는지 확인합니다.
    """
    
    # 띄어쓰기 등 일부만 일치해도 검색되도록 str.contains 사용
    matched = df_data[df_data['제품명'].str.contains(prescription_name, case=False, na=False)]
    
    # 결과 출력
    if not matched.empty:
        print(f"===============================================================")
        print(f"🚨🚨 수유부 위험 경고: '{prescription_name}' 분석 결과")
        print(f"===============================================================")
        
        # 중복 제거를 위해 제품명과 비고만 추출
        unique_risks = matched[['제품명', '성분명', '비고']].drop_duplicates()
        
        for index, row in unique_risks.iterrows():
            print(f" - [제품명]: {row['제품명']}")
            print(f" - [성분명]: {row['성분명']}")
            print(f" - [위험 사유(비고)]: {row['비고']}")
            print("-" * 50)
            
        print(f"⚠️ 권고: 이 약물은 수유 중 투여 시 신중해야 하거나 금기일 수 있으므로, 반드시 전문가(의사/약사)와 상담하세요.")
    else:
        print(f"✅ '{prescription_name}' (으)로 검색된 수유부 주의/금기 약물은 없습니다.")

# -----------------
# 3. 테스트 실행
# -----------------
print("--- [수유부 주의 약물 처방전 안전 점검 테스트] ---")

# 테스트 1: 위험 약물 (데이터셋 앞부분에서 임의로 추출한 성분/제품)
# 예를 들어, Afatinib (아파티닙) 성분은 항암제로 수유부에게 투여 금기일 가능성이 높습니다.
check_prescription_risk("지오트립정", df_lactating) 

# 테스트 2: 일반적인 약품 (데이터셋에 없을 가능성이 높은 이름)
check_prescription_risk("타이레놀", df_lactating)