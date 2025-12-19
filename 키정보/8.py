import pandas as pd
from typing import List, Dict, Any

# 투여 기간 주의 약물 파일명
CSV_FILE = '한국의약품안전관리원_투여기간주의약물_20231108.csv'

# --- 1. 데이터 로드 및 전처리 ---

def load_and_preprocess_duration_data(file_name: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 '최대투여기간일수'를 숫자형으로 변환합니다."""
    print(f"데이터셋 로딩: {file_name}")
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return pd.DataFrame()
    
    # '최대투여기간일수'를 정수형으로 변환, 변환 불가능한 값은 제거
    df['최대투여기간일수_숫자'] = pd.to_numeric(df['최대투여기간일수'], errors='coerce')
    
    # 필수 컬럼의 결측치 제거 후, 필요한 컬럼만 선택
    df = df.dropna(subset=['최대투여기간일수_숫', '제품명', '성분명'])
    df = df[['제품명', '성분명', '최대투여기간일수_숫자']].drop_duplicates()
    
    return df

# 데이터 로드 및 전처리
DF_DURATION = load_and_preprocess_duration_data(CSV_FILE)

if DF_DURATION.empty:
    print("데이터 로드에 실패하여 스크립트를 종료합니다.")
    exit()

print(f"✅ 투여 기간 주의 약물 데이터 로딩 완료. 총 {len(DF_DURATION)}개의 유효 데이터.")


# --- 2. 투여 기간 초과 검사 핵심 함수 ---

def check_duration_limit(drug_name: str, intended_duration_days: int, df_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    처방 기간이 약물의 최대 권장 투여 기간을 초과하는지 확인합니다.
    """
    
    results = []
    
    # 1. 처방전 약품명 매칭 (대소문자 무시)
    matched = df_data[df_data['제품명'].str.contains(drug_name, case=False, na=False)]
    
    if matched.empty:
        results.append({"status": "SAFE", "message": f"✅ '{drug_name}'에 대한 투여 기간 주의 기준 정보가 데이터셋에 없습니다."})
        return results

    # 2. 매칭된 결과를 기반으로 검사 및 경고 생성
    # 동일 제품명에 여러 성분/기간 기준이 있을 수 있으므로 모두 검사
    for _, row in matched.iterrows():
        
        max_days = int(row['최대투여기간일수_숫자'])
        ingredient = row['성분명']
        product_name = row['제품명']
        
        if intended_duration_days > max_days:
            results.append({
                "status": "DANGER", 
                "drug_name": product_name,
                "ingredient": ingredient,
                "intended_days": intended_duration_days,
                "max_days": max_days,
                "message": (
                    f"🚨🚨 투여 기간 초과 경고: 약품 '{product_name}' (성분: {ingredient})\n"
                    f"   - 처방 기간: {intended_duration_days}일 | 최대 권장 기간: {max_days}일\n"
                    f"   - 장기 투여 시 안전성 문제가 발생할 수 있습니다."
                )
            })
        else:
             results.append({
                "status": "SAFE", 
                "drug_name": product_name,
                "ingredient": ingredient,
                "intended_days": intended_duration_days,
                "max_days": max_days,
                "message": (
                    f"✅ 안전: 약품 '{product_name}' (성분: {ingredient})의 투여 기간 ({intended_duration_days}일)은 "
                    f"최대 권장 기간 ({max_days}일) 이내입니다."
                )
            })

    return results

# --- 3. 테스트 실행 ---

def run_tests():
    print("\n" + "="*50)
    print("  [투여 기간 주의 약물 검사 시스템] - 테스트 시작")
    print("="*50)
    
    # 테스트 1: 졸피뎀 (Zolpidem) - 최대 28일 기준. 30일 처방 시 초과 경고 예상
    # 데이터셋에 '스틸녹스정'이 28일로 등록되어 있음
    drug_name_1 = "스틸녹스정"
    duration_1 = 30
    print(f"\n--- [테스트 1: 기간 초과] - 약품: {drug_name_1}, 처방 {duration_1}일 ---")
    results_1 = check_duration_limit(drug_name_1, duration_1, DF_DURATION)
    for res in results_1:
        print(res['message'])
    
    # 테스트 2: 졸피뎀 (Zolpidem) - 20일 처방 시 안전 예상
    drug_name_2 = "스틸녹스정"
    duration_2 = 20
    print(f"\n--- [테스트 2: 안전 기간] - 약품: {drug_name_2}, 처방 {duration_2}일 ---")
    results_2 = check_duration_limit(drug_name_2, duration_2, DF_DURATION)
    for res in results_2:
        print(res['message'])

    # 테스트 3: 케토롤락 (Ketorolac tromethamine) - 최대 2일 기준. 3일 처방 시 초과 경고 예상
    # 데이터셋에 '케토신주사'가 2일로 등록되어 있음
    drug_name_3 = "케토신주사"
    duration_3 = 3
    print(f"\n--- [테스트 3: 단기 투여 기간 초과] - 약품: {drug_name_3}, 처방 {duration_3}일 ---")
    results_3 = check_duration_limit(drug_name_3, duration_3, DF_DURATION)
    for res in results_3:
        print(res['message'])

    # 테스트 4: 정보 부재 약물 (데이터셋에 없는 임의의 약품)
    drug_name_4 = "가상_백신"
    duration_4 = 7
    print(f"\n--- [테스트 4: 정보 부재] - 약품: {drug_name_4} ---")
    results_4 = check_duration_limit(drug_name_4, duration_4, DF_DURATION)
    for res in results_4:
        print(res['message'])

# 메인 실행
if __name__ == "__main__":
    run_tests()