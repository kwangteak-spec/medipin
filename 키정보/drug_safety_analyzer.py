import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Optional

# --- 1. 파일 경로 정의 ---
FILES = {
    '노인주의': '한국의약품안전관리원_노인주의약물_20240813.csv',
    '병용금기': '한국의약품안전관리원_병용금기약물_5줄.csv', # 데이터 부족으로 실제 사용에 한계가 있을 수 있음
    '임부금기': '한국의약품안전관리원_임부금기약물_20240625.csv',
    '수유부주의': '한국의약품안전관리원_수유부주의_20240121.csv',
    '연령금기': '한국의약품안전관리원_연령금기_20240625.csv',
    '용량주의': '한국의약품안전관리원_용량주의약물_20240501.csv',
    '기간주의': '한국의약품안전관리원_투여기간주의약물_20231108.csv',
    '효능군중복': '한국의약품안전관리원_효능군중복주의약물_20240813.csv',
}

# --- 2. 데이터 로드 및 전처리 공통 함수 ---

def load_data(file_name: str) -> Optional[pd.DataFrame]:
    """CSV 파일을 로드하고 기본 전처리를 수행합니다."""
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return None
    except Exception as e:
        print(f"❌ 데이터 로드 중 오류 발생 ({file_name}): {e}")
        return None
    
    # 모든 NaN 값을 '정보 없음'으로 대체
    df = df.fillna('정보 없음')
    return df

# 모든 데이터셋을 로드합니다.
DF_DATA = {key: load_data(path) for key, path in FILES.items()}


# --- 3. 위험 검사 함수들 ---

def check_elderly_risk(drug_name: str, df: pd.DataFrame) -> List[Dict[str, str]]:
    """노인 주의 약물 검사 (낙상, 치매, 저혈압 등 위험 키워드 포함)"""
    if df is None: return [{'type': '노인주의', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    # 노인에게 치명적인 부작용 키워드
    risk_keywords = ['낙상', '골절', '치매', '인지기능', '뇌혈관질환', '저혈압', '섬망']
    pattern = '|'.join(risk_keywords) 

    # 약품명과 키워드가 모두 일치하는 행 검색
    matched_drugs = df[
        df['제품명'].str.contains(drug_name, case=False, na=False) &
        df['약품상세정보'].str.contains(pattern, case=False, na=False)
    ].drop_duplicates(subset=['제품명', '약품상세정보'])

    results = []
    if not matched_drugs.empty:
        for _, row in matched_drugs.iterrows():
            results.append({
                'type': '노인주의',
                'status': 'Warning',
                'message': f"🚨 노인 위험: '{row['제품명']}'은(는) {row['약품상세정보']} 등의 위험으로 고령자 신중 투여가 필요합니다.",
                'details': f"성분명: {row['성분명']}"
            })
    else:
        results.append({'type': '노인주의', 'status': 'Safe', 'message': f"✅ '{drug_name}'은(는) 주요 노인 위험 키워드에 해당하지 않습니다."})
    
    return results

def check_concurrent_risk(drug_a_name: str, drug_b_name: str, df: pd.DataFrame) -> List[Dict[str, str]]:
    """두 약품 간 병용 금기 검사"""
    if df is None: return [{'type': '병용금기', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    # 1. (Drug A = 약물1 AND Drug B = 약물2) 조합 검색
    match_ab = df[
        (df['제품명1'].str.contains(drug_a_name, case=False, na=False)) & 
        (df['제품명2'].str.contains(drug_b_name, case=False, na=False))
    ]
    
    # 2. (Drug A = 약물2 AND Drug B = 약물1) 조합 검색 (순서 역전)
    match_ba = df[
        (df['제품명1'].str.contains(drug_b_name, case=False, na=False)) & 
        (df['제품명2'].str.contains(drug_a_name, case=False, na=False))
    ]
    
    matched_results = pd.concat([match_ab, match_ba]).drop_duplicates(subset=['제품명1', '제품명2', '금기사유'])

    results = []
    if not matched_results.empty:
        for _, row in matched_results.iterrows():
            results.append({
                'type': '병용금기',
                'status': 'Critical',
                'message': f"❌ 병용 금기: '{row['제품명1']}'과 '{row['제품명2']}'은(는) 함께 복용 시 금기입니다. 사유: {row['금기사유']}",
                'details': '즉시 의사/약사와 상담이 필요합니다.'
            })
    else:
        results.append({'type': '병용금기', 'status': 'Safe', 'message': f"✅ '{drug_a_name}'와 '{drug_b_name}' 간의 주요 병용 금기 사항은 확인되지 않습니다."})
    
    return results

def check_pregnancy_risk(drug_name: str, df: pd.DataFrame) -> List[Dict[str, str]]:
    """임부 금기 약물 검사"""
    if df is None: return [{'type': '임부금기', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    matched_drugs = df[df['제품명'].str.contains(drug_name, case=False, na=False)].drop_duplicates(subset=['제품명', '금기등급'])
    results = []

    if not matched_drugs.empty:
        for _, row in matched_drugs.iterrows():
            grade = str(row['금기등급'])
            status = 'Critical' if grade in ['1', '2'] else 'Warning' if grade == '3' else 'Info'
            message = f"🚨 임부 주의/금기 ({grade}등급): '{row['제품명']}' 투여 시 위험. 상세: {row['상세정보']}"
            results.append({
                'type': '임부금기',
                'status': status,
                'message': message,
                'details': f"성분명: {row['성분명']}"
            })
    else:
        results.append({'type': '임부금기', 'status': 'Safe', 'message': f"✅ '{drug_name}'은(는) 임부 금기 목록에서 확인되지 않습니다."})
        
    return results

def check_lactating_risk(drug_name: str, df: pd.DataFrame) -> List[Dict[str, str]]:
    """수유부 주의 약물 검사"""
    if df is None: return [{'type': '수유부주의', 'message': '데이터 로드 오류', 'status': 'Error'}]

    matched_drugs = df[df['제품명'].str.contains(drug_name, case=False, na=False)].drop_duplicates(subset=['제품명', '비고'])
    results = []

    if not matched_drugs.empty:
        for _, row in matched_drugs.iterrows():
            results.append({
                'type': '수유부주의',
                'status': 'Warning',
                'message': f"🚨 수유부 주의: '{row['제품명']}'은(는) 수유 중 투여 시 신중해야 합니다. 사유: {row['비고']}",
                'details': f"성분명: {row['성분명']}"
            })
    else:
        results.append({'type': '수유부주의', 'status': 'Safe', 'message': f"✅ '{drug_name}'은(는) 수유부 주의 목록에서 확인되지 않습니다."})
        
    return results

def normalize_unit(unit):
    """연령 단위 표준화 (년/개월)"""
    if '개월' in unit: return '개월'
    elif '세' in unit or '년' in unit: return '년'
    return unit

def check_child_age_restriction(prescription_name: str, child_age: int, age_unit: str, df: pd.DataFrame) -> List[Dict[str, str]]:
    """어린이 연령 금기 약물 검사"""
    if df is None: return [{'type': '연령금기', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    # 전처리된 컬럼을 활용
    df['특정연령단위_정규화'] = df['특정연령단위'].apply(normalize_unit)
    df['특정연령_숫자'] = pd.to_numeric(df['특정연령'], errors='coerce')
    
    # 약품명 일치 및 특정 연령 정보가 있는 행만 필터링
    matched = df[
        df['제품명'].str.contains(prescription_name, case=False, na=False) &
        df['특정연령_숫자'].notna()
    ]
    
    results = []
    
    if matched.empty:
        results.append({'type': '연령금기', 'status': 'Safe', 'message': f"✅ '{prescription_name}'은(는) {child_age}{age_unit} 아동에 대한 연령 금기 기준에 해당하지 않습니다."})
        return results

    for _, row in matched.iterrows():
        restricted_age = row['특정연령_숫자']
        restricted_unit = row['특정연령단위_정규화']
        
        is_restricted = False
        
        # 연령 단위 비교 및 금기 조건 확인
        if restricted_unit == '년':
            if age_unit == '년' and child_age <= restricted_age:
                is_restricted = True
            elif age_unit == '개월' and (child_age / 12) <= restricted_age:
                # 개월을 연으로 환산하여 비교
                is_restricted = True
        elif restricted_unit == '개월':
            if age_unit == '개월' and child_age <= restricted_age:
                is_restricted = True
            elif age_unit == '년' and child_age * 12 <= restricted_age:
                # 연을 개월로 환산하여 비교
                is_restricted = True

        if is_restricted:
             results.append({
                'type': '연령금기',
                'status': 'Critical',
                'message': f"❌ 연령 금기: '{row['제품명']}'은(는) {restricted_age}{restricted_unit} 이하에게 금기됩니다. {child_age}{age_unit} 아동에게는 투여 금지되거나 신중해야 합니다. 상세: {row['상세정보']}",
                'details': f"금기 연령: {row['특정연령']} {row['특정연령단위']}"
            })

    if not results:
         results.append({'type': '연령금기', 'status': 'Safe', 'message': f"✅ '{prescription_name}'은(는) {child_age}{age_unit} 아동에 대한 연령 금기 기준에 해당하지 않습니다."})
        
    return results


def check_daily_max_dose(drug_name: str, dose_per_time: float, times_per_day: int, df: pd.DataFrame) -> List[Dict[str, str]]:
    """1일 최대 용량 초과 검사"""
    if df is None: return [{'type': '용량주의', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    # '점검기준 성분함량'에서 숫자만 추출하는 함수
    def extract_strength(text):
        match = re.search(r'(\d+(\.\d+)?)mg', str(text), re.IGNORECASE)
        return float(match.group(1)) if match else np.nan

    # '1일최대투여량'에서 숫자만 추출하는 함수
    def extract_max_dose(text):
        match = re.search(r'(\d+(\.\d+)?)mg', str(text), re.IGNORECASE)
        return float(match.group(1)) if match else np.nan

    df['성분함량_mg'] = df['점검기준 성분함량'].apply(extract_strength)
    df['최대투여량_mg'] = df['1일최대투여량'].apply(extract_max_dose)

    matched_drugs = df[
        df['제품명'].str.contains(drug_name, case=False, na=False) & 
        df['성분함량_mg'].notna() &
        df['최대투여량_mg'].notna()
    ].drop_duplicates(subset=['제품명', '성분함량_mg', '최대투여량_mg'])

    if matched_drugs.empty:
        return [{'type': '용량주의', 'status': 'Info', 'message': f"ℹ️ 용량 정보 없음: '{drug_name}'에 대한 일일 최대 용량 정보가 데이터셋에 없습니다."}]

    results = []
    
    # 복용 총량 계산 (예: 1회 2정, 1일 3회, 1정당 400mg)
    # 일일 총 복용량 = 1회 복용 정수 * 1일 복용 횟수 * 1정당 성분 함량
    daily_intake = dose_per_time * times_per_day * matched_drugs['성분함량_mg'].iloc[0] # 첫 번째 매칭된 성분 함량 사용

    for _, row in matched_drugs.iterrows():
        max_dose = row['최대투여량_mg']
        
        if daily_intake > max_dose:
            results.append({
                'type': '용량주의',
                'status': 'Critical',
                'message': f"❌ 용량 초과: '{row['제품명']}' 복용 시 일일 최대 투여량({max_dose}mg)을 초과({daily_intake}mg)합니다.",
                'details': f"1회 {dose_per_time}정, 1일 {times_per_day}회, 1정당 {row['성분함량_mg']}mg. 투여량 조정이 필요합니다."
            })
        else:
            results.append({
                'type': '용량주의',
                'status': 'Safe',
                'message': f"✅ 용량 안전: '{row['제품명']}'의 일일 총 복용량({daily_intake}mg)은 최대 투여량({max_dose}mg) 이내입니다."
            })

    return results

def check_duration_limit(drug_name: str, duration_days: int, df: pd.DataFrame) -> List[Dict[str, str]]:
    """최대 투여 기간 초과 검사"""
    if df is None: return [{'type': '기간주의', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    df['최대투여기간일수_숫자'] = pd.to_numeric(df['최대투여기간일수'], errors='coerce')
    
    matched_drugs = df[
        df['제품명'].str.contains(drug_name, case=False, na=False) & 
        df['최대투여기간일수_숫자'].notna()
    ].drop_duplicates(subset=['제품명', '최대투여기간일수_숫자'])

    if matched_drugs.empty:
        return [{'type': '기간주의', 'status': 'Info', 'message': f"ℹ️ 기간 정보 없음: '{drug_name}'에 대한 최대 투여 기간 정보가 데이터셋에 없습니다."}]
    
    results = []
    
    for _, row in matched_drugs.iterrows():
        max_days = row['최대투여기간일수_숫자']
        
        if duration_days > max_days:
            results.append({
                'type': '기간주의',
                'status': 'Warning',
                'message': f"🚨 기간 초과: '{row['제품명']}'은(는) 최대 {max_days}일 투여 권고 약물입니다. 현재 처방 기간({duration_days}일) 초과 시 의존성 등 위험이 증가할 수 있습니다.",
                'details': f"성분명: {row['성분명']}"
            })
        else:
            results.append({
                'type': '기간주의',
                'status': 'Safe',
                'message': f"✅ 기간 안전: '{drug_name}'의 처방 기간({duration_days}일)은 최대 권고 기간({max_days}일) 이내입니다."
            })
            
    return results

def check_efficacy_duplication(drug_names: List[str], df: pd.DataFrame) -> List[Dict[str, str]]:
    """효능군 중복 검사"""
    if df is None: return [{'type': '효능군중복', 'message': '데이터 로드 오류', 'status': 'Error'}]
    
    results = []
    
    # 1. 처방된 약품들이 속한 효능군 그룹을 찾습니다.
    # 각 약품명에 대해 데이터프레임을 검색
    prescribed_drugs_info = df[df['제품명'].str.contains('|'.join(drug_names), case=False, na=False)].drop_duplicates(subset=['제품명', '그룹구분'])
    
    # 2. 효능군별 그룹 목록을 생성합니다. (Group 구분자를 사용하여 중복 검사)
    efficacy_groups: Dict[str, List[str]] = {} # {'Group 10': ['듀얼로우정', '듀이젠정'], ...}

    for _, row in prescribed_drugs_info.iterrows():
        group_key = f"{row['효능군']} ({row['그룹구분']})"
        drug = row['제품명']
        
        if group_key not in efficacy_groups:
            efficacy_groups[group_key] = []
        
        # 중복 약품명을 제거하고 추가
        if drug not in efficacy_groups[group_key]:
            efficacy_groups[group_key].append(drug)

    # 3. 중복 그룹을 검사하고 결과를 생성합니다.
    for group, drugs in efficacy_groups.items():
        if len(drugs) > 1:
            results.append({
                'type': '효능군중복',
                'status': 'Warning',
                'message': f"🚨 효능군 중복 주의: '{', '.join(drugs)}'은(는) 동일 효능군 '{group}'에 속하여 약효 중복 또는 과도한 효과를 유발할 수 있습니다.",
                'details': '의사/약사와 상담하여 투여 약물을 조정해야 합니다.'
            })
        
    if not results:
        results.append({'type': '효능군중복', 'status': 'Safe', 'message': f"✅ 처방된 약품들 간의 주요 효능군 중복 위험은 확인되지 않습니다."})

    return results


# --- 4. 통합 검사 함수 (최종 사용자 호출 함수) ---

def run_comprehensive_safety_check(
    prescription_drugs: List[str],
    patient_info: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    모든 약물 안전성 검사를 통합 실행하고 결과를 반환합니다.

    Args:
        prescription_drugs: 처방받은 약품명 리스트 (예: ["데파스정", "타이레놀정"])
        patient_info: 환자 정보 딕셔너리
            - 'is_elderly': bool (고령자 여부, 만 65세 이상)
            - 'is_pregnant': bool (임부 여부)
            - 'is_lactating': bool (수유부 여부)
            - 'child_age': int (아동 연령, 성인인 경우 0)
            - 'age_unit': str ('년' 또는 '개월', 성인인 경우 '년')
            - 'dose_info': List[Dict] (용량/기간 정보)
                [{"drug_name": "약품명", "dose_per_time": 1, "times_per_day": 3, "duration_days": 7}]
    """
    all_results = []
    
    # 1. 노인 주의 약물 검사
    if patient_info.get('is_elderly', False):
        for drug in prescription_drugs:
            all_results.extend(check_elderly_risk(drug, DF_DATA['노인주의']))
            
    # 2. 임부/수유부 금기 검사
    if patient_info.get('is_pregnant', False):
        for drug in prescription_drugs:
            all_results.extend(check_pregnancy_risk(drug, DF_DATA['임부금기']))

    if patient_info.get('is_lactating', False):
        for drug in prescription_drugs:
            all_results.extend(check_lactating_risk(drug, DF_DATA['수유부주의']))

    # 3. 아동 연령 금기 검사
    child_age = patient_info.get('child_age', 0)
    age_unit = patient_info.get('age_unit', '년')
    if child_age > 0 and (age_unit == '년' or age_unit == '개월'):
        for drug in prescription_drugs:
            all_results.extend(check_child_age_restriction(drug, child_age, age_unit, DF_DATA['연령금기']))
            
    # 4. 약품 간 병용 금기 검사 (2개 이상의 약물이 있을 때)
    if len(prescription_drugs) >= 2:
        for i in range(len(prescription_drugs)):
            for j in range(i + 1, len(prescription_drugs)):
                drug_a = prescription_drugs[i]
                drug_b = prescription_drugs[j]
                all_results.extend(check_concurrent_risk(drug_a, drug_b, DF_DATA['병용금기']))

    # 5. 용량 및 기간 주의 검사 (dose_info가 있을 때)
    dose_info = patient_info.get('dose_info', [])
    for info in dose_info:
        drug = info.get('drug_name')
        dose_per_time = info.get('dose_per_time')
        times_per_day = info.get('times_per_day')
        duration_days = info.get('duration_days')
        
        if drug and dose_per_time and times_per_day:
            all_results.extend(check_daily_max_dose(drug, dose_per_time, times_per_day, DF_DATA['용량주의']))
        
        if drug and duration_days:
            all_results.extend(check_duration_limit(drug, duration_days, DF_DATA['기간주의']))
            
    # 6. 효능군 중복 검사
    all_results.extend(check_efficacy_duplication(prescription_drugs, DF_DATA['효능군중복']))
    
    return all_results

# --- 5. 통합 테스트 실행 예시 ---

def run_integrated_test():
    """통합 검사 로직을 위한 테스트 데이터 및 실행"""
    
    print("\n" + "="*80)
    print("      💊 처방 약물 통합 안전성 검사 시스템 - 통합 테스트 시작 💊")
    print("="*80)

    # --- 테스트 케이스 정의 ---
    # 1. 고위험자 및 용량/기간 초과 시뮬레이션
    test_drugs_1 = ["데파스정", "타이레놀정", "스틸녹스정"]
    test_patient_info_1 = {
        'is_elderly': True, # 노인 주의 검사 트리거
        'is_pregnant': False,
        'is_lactating': False,
        'child_age': 0,
        'age_unit': '년',
        'dose_info': [
            # '데파스정' (etizolam)은 노인 주의 약물 (노인주의.csv) -> 낙상/치매 위험 경고 예상
            # '타이레놀정' (acetaminophen)은 용량 주의 약물 (용량주의.csv)
            {"drug_name": "타이레놀정", "dose_per_time": 2, "times_per_day": 5, "duration_days": 7}, # 용량 초과 테스트 (타이레놀 1정 500mg, 최대 4000mg. 2*5*500=5000mg -> 초과 예상)
            # '스틸녹스정' (zolpidem)은 기간 주의 약물 (기간주의.csv)
            {"drug_name": "스틸녹스정", "dose_per_time": 1, "times_per_day": 1, "duration_days": 30} # 기간 초과 테스트 (최대 28일. 30일 처방 -> 초과 예상)
        ]
    }
    
    print(f"\n--- [테스트 케이스 1: 고령자, 용량/기간 초과] - 약물: {test_drugs_1} ---")
    results_1 = run_comprehensive_safety_check(test_drugs_1, test_patient_info_1)
    
    # 결과 출력
    for res in results_1:
        print(f"[{res['status']:<10}] {res['type']:<8}: {res['message']}")
        
    print("\n" + "-"*80)
        
    # 2. 병용 금기 및 효능군 중복 시뮬레이션
    test_drugs_2 = ["제클라정", "심바스트정", "듀얼로우정", "위캡정"]
    test_patient_info_2 = {
        'is_elderly': False, 
        'is_pregnant': True, # 임부 금기 검사 트리거
        'is_lactating': False,
        'child_age': 0,
        'age_unit': '년',
        'dose_info': []
    }
    
    print(f"\n--- [테스트 케이스 2: 임부, 병용/효능군 중복] - 약물: {test_drugs_2} ---")
    results_2 = run_comprehensive_safety_check(test_drugs_2, test_patient_info_2)
    
    # 결과 출력
    for res in results_2:
        print(f"[{res['status']:<10}] {res['type']:<8}: {res['message']}")
        
    print("\n" + "="*80)

# 이 스크립트를 직접 실행할 때 테스트 실행
if __name__ == "__main__":
    run_integrated_test()