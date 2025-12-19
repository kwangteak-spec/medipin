import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any

# 용량주의 약물 파일명
CSV_FILE = '한국의약품안전관리원_용량주의약물_20240501.csv'

# --- 1. 데이터 로드 및 전처리 ---

def load_and_preprocess_dosage_data(file_name: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 '1일최대투여량'과 '점검기준 성분함량'을 숫자형으로 변환합니다."""
    print(f"데이터셋 로딩: {file_name}")
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return pd.DataFrame()
    
    df = df.fillna('정보 없음')

    # '1일최대투여량'에서 숫자만 추출하여 계산에 사용 (예: 아세트아미노펜으로써 4000mg -> 4000)
    df['1일최대투여량_숫자'] = df['1일최대투여량'].apply(normalize_dosage_unit)
    
    # '점검기준 성분함량'에서 숫자만 추출하여 계산에 사용 (예: 400mg -> 400)
    df['성분함량_숫자'] = df['점검기준 성분함량 (총함량)'].apply(normalize_dosage_unit)
    
    return df.dropna(subset=['1일최대투여량_숫자', '성분함량_숫자']) # 계산에 필요한 필수 컬럼만 유지

def normalize_dosage_unit(text: str) -> float:
    """텍스트에서 숫자만 추출하여 float 형태로 반환합니다."""
    if isinstance(text, str):
        # 쉼표 제거 (예: 4,000mg -> 4000mg)
        text = text.replace(',', '')
        # 숫자만 추출 (소수점 포함)
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
    return np.nan

# 데이터 로드 및 전처리
DF_DOSAGE = load_and_preprocess_dosage_data(CSV_FILE)

if DF_DOSAGE.empty:
    print("데이터 로드에 실패하여 스크립트를 종료합니다.")
    exit()

print(f"✅ 용량주의 약물 데이터 로딩 완료. 총 {len(DF_DOSAGE)}개의 유효 데이터.")


# --- 2. 용량 초과 검사 핵심 함수 ---

def check_daily_max_dose(prescription_name: str, dose_per_take: int, times_per_day: int, df_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    처방전 약품이 1일 최대 투여량을 초과하는지 확인합니다.
    (주의: 이 함수는 단일 성분 처방 또는 복합제 내 단일 성분의 용량 초과만 검사합니다.
     복합제 여러 개를 동시에 복용하는 총 성분량 합산은 더 복잡한 로직이 필요합니다.)
    """
    
    results = []
    
    # 1. 처방전 약품명 매칭 (대소문자 무시)
    matched = df_data[df_data['제품명'].str.contains(prescription_name, case=False, na=False)]
    
    if matched.empty:
        results.append({"status": "SAFE", "message": f"✅ '{prescription_name}'에 대한 용량주의 기준 정보가 데이터셋에 없습니다."})
        return results

    # 2. 성분명별로 그룹화하여 검사 (동일 성분 복합제 고려)
    for ingredient, group in matched.groupby('성분명'):
        
        # 성분명별로 1일 최대 투여량 기준을 정합니다. (가장 큰 값을 기준으로 사용)
        max_daily_dose = group['1일최대투여량_숫자'].max()
        
        # 해당 성분이 들어있는 제품의 함량 정보를 가져옵니다. 
        # (이 예제에서는 매칭된 제품 중 첫 번째 제품의 함량 정보를 기준으로 사용)
        base_drug = group.iloc[0] 
        ingredient_amount_per_pill = base_drug['성분함량_숫자']
        
        # 3. 환자의 1일 총 성분 복용량 계산
        # (1회 복용량) * (1일 복용 횟수) * (알약 1개당 성분 함량)
        patient_daily_dose = dose_per_take * times_per_day * ingredient_amount_per_pill
        
        # 4. 비교 및 경고 생성
        if patient_daily_dose > max_daily_dose:
            results.append({
                "status": "DANGER", 
                "ingredient": ingredient,
                "drug_name": base_drug['제품명'],
                "patient_dose": f"{patient_daily_dose:.0f}",
                "max_dose": f"{max_daily_dose:.0f}",
                "unit": "mg",
                "message": (
                    f"🚨🚨 용량 초과 경고: 성분 '{ingredient}'"
                    f" (환자 복용량: {patient_daily_dose:.0f} mg)이 "
                    f"안전 최대 투여량 ({max_daily_dose:.0f} mg)을 초과합니다."
                )
            })
        else:
             results.append({
                "status": "SAFE", 
                "ingredient": ingredient,
                "drug_name": base_drug['제품명'],
                "patient_dose": f"{patient_daily_dose:.0f}",
                "max_dose": f"{max_daily_dose:.0f}",
                "unit": "mg",
                "message": (
                    f"✅ 안전: 성분 '{ingredient}'의 1일 투여량 ({patient_daily_dose:.0f} mg)은 "
                    f"최대 안전 용량 ({max_daily_dose:.0f} mg) 이내입니다."
                )
            })

    return results

# --- 3. 테스트 실행 ---

def run_tests():
    print("\n" + "="*50)
    print("  [용량주의 약물 투여량 검사 테스트 시작]")
    print("="*50)
    
    # 테스트 1: 아세트아미노펜 (Acetaminophen) - 용량 초과 유발
    # * 아세트아미노펜의 1일 최대 안전 용량은 보통 4000mg
    # * '리스카펜정' (400mg/정)을 1회 2정, 1일 6회 복용 가정
    # * 계산: 2정 * 6회 * 400mg/정 = 4800mg (4000mg 초과) -> 경고 발생 예상
    drug_name_1 = "리스카펜정"
    dose_1 = 2
    times_1 = 6
    print(f"\n--- [테스트 1: 용량 초과] - 약품: {drug_name_1}, 1회 {dose_1}정, 1일 {times_1}회 ---")
    results_1 = check_daily_max_dose(drug_name_1, dose_1, times_1, DF_DOSAGE)
    for res in results_1:
        print(res['message'])
    
    # 테스트 2: 아세트아미노펜 (Acetaminophen) - 안전 용량
    # * '리스카펜정' (400mg/정)을 1회 1정, 1일 5회 복용 가정
    # * 계산: 1정 * 5회 * 400mg/정 = 2000mg (4000mg 이내) -> 안전 예상
    drug_name_2 = "리스카펜정"
    dose_2 = 1
    times_2 = 5
    print(f"\n--- [테스트 2: 안전 용량] - 약품: {drug_name_2}, 1회 {dose_2}정, 1일 {times_2}회 ---")
    results_2 = check_daily_max_dose(drug_name_2, dose_2, times_2, DF_DOSAGE)
    for res in results_2:
        print(res['message'])

    # 테스트 3: 정보 부재 약물 (데이터셋에 없는 임의의 약품)
    drug_name_3 = "새로운_항생제_A"
    print(f"\n--- [테스트 3: 정보 부재] - 약품: {drug_name_3} ---")
    results_3 = check_daily_max_dose(drug_name_3, 1, 2, DF_DOSAGE)
    for res in results_3:
        print(res['message'])

    # 테스트 4: 다른 성분 (Abrocitinib) - 안전 용량
    # * '시빈코정' (abrocitinib, 200mg/정) 1일 최대 200mg
    # * 복용: 1회 1정, 1일 1회 복용 가정
    # * 계산: 1정 * 1회 * 200mg/정 = 200mg (200mg 이내) -> 안전 예상
    drug_name_4 = "시빈코정"
    dose_4 = 1
    times_4 = 1
    print(f"\n--- [테스트 4: 다른 성분 - 안전 용량] - 약품: {drug_name_4}, 1회 {dose_4}정, 1일 {times_4}회 ---")
    results_4 = check_daily_max_dose(drug_name_4, dose_4, times_4, DF_DOSAGE)
    for res in results_4:
        print(res['message'])

# 메인 실행
if __name__ == "__main__":
    run_tests()