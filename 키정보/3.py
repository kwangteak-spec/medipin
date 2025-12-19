import pandas as pd

# 1. CSV 파일 로드 (인코딩은 'cp949' 또는 'utf-8' 사용)
csv_file = '한국의약품안전관리원_병용금기약물_5줄.csv'
try:
    df = pd.read_csv(csv_file, encoding='cp494') # cp494 또는 utf-8 시도
except UnicodeDecodeError:
    df = pd.read_csv(csv_file, encoding='utf-8')

# 2. 주요 분석 컬럼 선택
# 제품명1, 제품명2: 사용자 입력과 매칭
# 금기사유: 부작용 분류 (가장 중요한 컬럼)
prohibited_df = df[['제품명1', '제품명2', '금기사유']]

# 3. 데이터 샘플 및 핵심 정보 출력 (5줄만 있으므로 전체 출력)
print("--- 🔍 병용 금기 약물 데이터 샘플 분석 (총 5줄) ---")
print(prohibited_df.to_string(index=False))
print("-" * 50)

# 4. 처방전 약품 간 병용 금기 여부를 확인하는 기능
def check_concurrent_risk(drug_a_name, drug_b_name, dataframe):
    """
    두 약품명(drug_a, drug_b)이 병용 금기 목록에 있는지 확인합니다.
    (순서에 관계없이 약물1, 약물2 컬럼에서 모두 검색)
    """
    
    # 1. (Drug A = 약물1 AND Drug B = 약물2) 조합 검색
    match_ab = dataframe[
        (dataframe['제품명1'].str.contains(drug_a_name, na=False)) & 
        (dataframe['제품명2'].str.contains(drug_b_name, na=False))
    ]
    
    # 2. (Drug A = 약물2 AND Drug B = 약물1) 조합 검색 (순서 역전)
    match_ba = dataframe[
        (dataframe['제품명1'].str.contains(drug_b_name, na=False)) & 
        (dataframe['제품명2'].str.contains(drug_a_name, na=False))
    ]
    
    # 두 결과를 합칩니다
    matched_results = pd.concat([match_ab, match_ba]).drop_duplicates()

    print(f"\n[약품 병용 금기 안전 점검: '{drug_a_name}' & '{drug_b_name}']")
    
    if not matched_results.empty:
        print("🚨🚨 치명적 위험 경고! 🚨🚨")
        for index, row in matched_results.iterrows():
            # 부작용 분류 컬럼(금기사유) 출력
            print(f"   - 금기 약물 조합: {row['제품명1']}과 {row['제품명2']}")
            print(f"   - **부작용 분류 (금기사유): {row['금기사유']}**")
            print("     -> [조치] 반드시 의사 또는 약사와 상담하세요.")
    else:
        print("✅ 현재 검사한 두 약품 간의 직접적인 병용 금기 정보는 목록에서 발견되지 않았습니다.")

# 테스트: 샘플 데이터에 있는 '제클라정'과 '심바로드정' 조합 검사
check_prescription_risk("제클라정", "심바로드정", prohibited_df)

# 테스트 2: 금기 정보가 없는 조합 검사 (예시)
# check_prescription_risk("타이레놀", "아로나민", prohibited_df)