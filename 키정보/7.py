import pandas as pd
from typing import List, Dict, Any

# 임부 금기 약물 파일명
CSV_FILE = '한국의약품안전관리원_임부금기약물_20240625.csv'

# --- 1. 데이터 로드 및 전처리 ---

def load_and_preprocess_pregnancy_data(file_name: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 결측치를 처리합니다."""
    print(f"데이터셋 로딩: {file_name}")
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return pd.DataFrame()
    
    # 필수 컬럼의 결측치는 '정보 없음'으로 대체하고, 필요한 컬럼만 선택
    df = df[['제품명', '성분명', '금기등급', '상세정보']].fillna('정보 없음')
    
    return df

# 데이터 로드 및 전처리
DF_PREGNANCY = load_and_preprocess_pregnancy_data(CSV_FILE)

if DF_PREGNANCY.empty:
    print("데이터 로드에 실패하여 스크립트를 종료합니다.")
    exit()

# 금기 등급 설명 (데이터셋의 '금기등급' 컬럼 값에 대한 일반적인 해석)
GRADE_INFO = {
    1: "🔴 1등급 (절대 금기): 태아에 대한 위험성이 높고, 이 약의 치료상의 유익성이 위험성을 상회하지 않음. 임신 중 절대 투여 금지.",
    2: "🟠 2등급 (상대 금기): 태아에 대한 위험성이 있으나, 때로는 이 약의 치료상의 유익성이 위험성을 상회할 수 있음. 신중 투여 필요.",
    '정보 없음': "⚫ 금기 등급 정보 없음: 데이터셋에 상세 등급 정보가 없습니다."
}

print(f"✅ 임부 금기 약물 데이터 로딩 완료. 총 {len(DF_PREGNANCY)}개의 유효 데이터.")


# --- 2. 임부 금기 검사 핵심 함수 ---

def check_pregnancy_restriction(drug_name: str, df_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    처방전 약품이 임부 금기 약물인지 확인하고 상세 정보를 반환합니다.
    """
    
    results = []
    
    # 1. 처방전 약품명 매칭 (대소문자 무시)
    # 중복된 약품명이 있을 수 있으므로 모두 찾습니다.
    matched = df_data[df_data['제품명'].str.contains(drug_name, case=False, na=False)]
    
    if matched.empty:
        results.append({"status": "SAFE", "message": f"✅ '{drug_name}'은(는) 데이터셋에 임부 금기 약물로 등록되어 있지 않습니다. (추가 검토 필요)"})
        return results

    # 2. 매칭된 결과를 기반으로 경고 생성
    for _, row in matched.drop_duplicates(subset=['제품명', '금기등급', '상세정보']).iterrows():
        
        grade_str = str(row['금기등급'])
        grade_info = GRADE_INFO.get(row['금기등급'], GRADE_INFO['정보 없음'])
        
        results.append({
            "status": "DANGER", 
            "drug_name": row['제품명'],
            "ingredient": row['성분명'],
            "restriction_grade": grade_str,
            "detailed_reason": row['상세정보'],
            "message": (
                f"❌❌ 임부 금기 경고: 약품 '{row['제품명']}' (성분: {row['성분명']})"
                f" - {grade_info}\n"
                f"   [상세 사유]: {row['상세정보']}"
            )
        })

    return results

# --- 3. 테스트 실행 ---

def run_tests():
    print("\n" + "="*50)
    print("  [임부 금기 약물 검사 시스템] - 테스트 시작")
    print("="*50)
    
    # 테스트 1: 금기 2등급 약물 (데이터셋의 '피마듀오정')
    drug_name_1 = "피마듀오정"
    print(f"\n--- [테스트 1: 2등급 금기 약물] - 약품: {drug_name_1} ---")
    results_1 = check_pregnancy_restriction(drug_name_1, DF_PREGNANCY)
    for res in results_1:
        print(res['message'])
    
    # 테스트 2: 금기 1등급 약물 (임의의 약물명, 데이터셋에 '피오글리타존' 성분으로 존재)
    # 데이터셋에 '피오렌정'이 2등급으로 등록되어 있습니다.
    # 만약 1등급 약물이 있다면 그 약물로 테스트하거나, 성분명으로 검색합니다.
    # 여기서는 데이터셋에 있는 '피오렌정'을 다시 검색하여 결과를 확인합니다.
    drug_name_2 = "피오렌정"
    print(f"\n--- [테스트 2: 2등급 금기 약물] - 약품: {drug_name_2} ---")
    results_2 = check_pregnancy_restriction(drug_name_2, DF_PREGNANCY)
    for res in results_2:
        print(res['message'])
        
    # 테스트 3: 정보 부재 약물 (데이터셋에 없을 가능성이 높은 일반적인 약품)
    drug_name_3 = "타이레놀" # Acetaminophen 성분으로 검색
    print(f"\n--- [테스트 3: 정보 부재 약물] - 약품: {drug_name_3} ---")
    results_3 = check_pregnancy_restriction(drug_name_3, DF_PREGNANCY)
    for res in results_3:
        print(res['message'])
        
    # 테스트 4: 로션/크림 제제 (데이터셋의 '모리코트로션')
    drug_name_4 = "모리코트로션"
    print(f"\n--- [테스트 4: 로션 제제 (2등급 금기)] - 약품: {drug_name_4} ---")
    results_4 = check_pregnancy_restriction(drug_name_4, DF_PREGNANCY)
    for res in results_4:
        print(res['message'])


# 메인 실행
if __name__ == "__main__":
    run_tests()