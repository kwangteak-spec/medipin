import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Union

# ==============================================================================
# 1. 데이터 파일 경로 정의 (업로드된 파일 및 기존 분석 코드에 사용된 파일명 기준)
# ==============================================================================
# 모든 CSV 파일은 'cp949' 또는 'utf-8' 인코딩으로 로드됩니다.
DATA_FILES = {
    'elderly_caution': '한국의약품안전관리원_노인주의약물_20240813.csv',
    'concurrent_prohibition': '한국의약품안전관리원_병용금기약물_5줄.csv', # 5줄 샘플 파일
    'lactating_caution': '한국의약품안전관리원_수유부주의_20240121.csv',
    'age_restriction': '한국의약품안전관리원_연령금기_20240625.csv',
    'dosage_limit': '한국의약품안전관리원_용량주의약물_20240501.csv',
    'pregnancy_prohibition': '한국의약품안전관리원_임부금기약물_20240625.csv',
    'duration_limit': '한국의약품안전관리원_투여기간주의약물_20231108.csv',
    'efficacy_duplication': '한국의약품안전관리원_효능군중복주의약물_20240813.csv',
}

# 노인 및 기저질환 위험 키워드 정의 (1.py 기반)
RISK_KEYWORDS = ['낙상', '골절', '치매', '인지기능', '뇌혈관질환', '저혈압', '섬망']

# ==============================================================================
# 2. 데이터 로드 및 전처리 유틸리티
# ==============================================================================

def load_data(file_name: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 인코딩 오류 및 결측치를 처리합니다."""
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 오류: 파일 '{file_name}' 로드 중 예상치 못한 오류 발생: {e}")
        return pd.DataFrame()

    # 모든 NaN 값을 '정보 없음'으로 대체하여 검색 오류 방지 (전처리 단순화)
    return df.fillna('정보 없음')

def normalize_dosage_unit(dosage_string: str) -> Union[float, None]:
    """'1일최대투여량' 문자열에서 숫자만 추출하여 mg 단위로 변환합니다. (6.py 기반)"""
    # 숫자와 소수점만 포함하는 패턴을 찾습니다. (예: 4000mg, 4000)
    match = re.search(r'(\d+\.?\d*)', dosage_string)
    if match:
        return float(match.group(1))
    return None

# ==============================================================================
# 3. 데이터 로드 및 전처리 실행
# ==============================================================================
print("🔍 약물 안전성 분석 데이터 로드 시작...")

DF_ELDERLY = load_data(DATA_FILES['elderly_caution'])
DF_CONCURRENT = load_data(DATA_FILES['concurrent_prohibition'])
DF_LACTATING = load_data(DATA_FILES['lactating_caution'])
DF_AGE = load_data(DATA_FILES['age_restriction'])
DF_DOSAGE = load_data(DATA_FILES['dosage_limit'])
DF_PREGNANCY = load_data(DATA_FILES['pregnancy_prohibition'])
DF_DURATION = load_data(DATA_FILES['duration_limit'])
DF_DUPLICATION = load_data(DATA_FILES['efficacy_duplication'])

# 용량주의 데이터프레임 추가 전처리 (6.py 기반)
if not DF_DOSAGE.empty:
    DF_DOSAGE['1일최대투여량_숫자'] = DF_DOSAGE['1일최대투여량'].apply(normalize_dosage_unit)
    DF_DOSAGE['점검기준 성분함량_숫자'] = DF_DOSAGE['점검기준 성분함량'].apply(normalize_dosage_unit)
    DF_DOSAGE = DF_DOSAGE.dropna(subset=['1일최대투여량_숫자', '점검기준 성분함량_숫자'])

# 연령금기 데이터프레임 추가 전처리 (5.py 기반)
def normalize_age_unit(unit):
    if '개월' in unit: return '개월'
    elif '세' in unit or '년' in unit: return '년'
    return unit

if not DF_AGE.empty:
    DF_AGE['특정연령단위_정규화'] = DF_AGE['특정연령단위'].apply(normalize_age_unit)
    DF_AGE['특정연령_숫자'] = pd.to_numeric(DF_AGE['특정연령'], errors='coerce')
    DF_AGE = DF_AGE.dropna(subset=['특정연령_숫자'])

# 투여기간주의 데이터프레임 추가 전처리 (8.py 기반)
if not DF_DURATION.empty:
    DF_DURATION['최대투여기간일수_숫자'] = pd.to_numeric(DF_DURATION['최대투여기간일수'], errors='coerce')
    DF_DURATION = DF_DURATION.dropna(subset=['최대투여기간일수_숫자'])

print("✅ 데이터 로드 및 전처리 완료.")
print("-" * 50)


# ==============================================================================
# 4. 개별 위험 검사 기능 함수 정의
# ==============================================================================

def format_result(risk_type: str, severity: str, message: str, details: Dict[str, Any]) -> Dict[str, str]:
    """검사 결과를 표준화된 딕셔너리 형태로 반환합니다."""
    return {'type': risk_type, 'severity': severity, 'message': message, 'details': str(details)}

def check_elderly_risk(prescription_drug: str, dataframe: pd.DataFrame, keywords: List[str]) -> List[Dict[str, str]]:
    """노인 주의 약물 (키워드 기반) 검사 (1.py 기반)"""
    results = []
    pattern = '|'.join(keywords)
    matched = dataframe[
        dataframe['제품명'].str.contains(prescription_drug, case=False, na=False) &
        dataframe['약품상세정보'].str.contains(pattern, case=False, na=False)
    ]
    if not matched.empty:
        risks = matched[['제품명', '성분명', '약품상세정보']].drop_duplicates().to_dict('records')
        results.append(format_result(
            '노인/기저질환 주의', '주의', 
            f"'{prescription_drug}'은(는) 노인 및 기저질환자에게 위험할 수 있는 키워드(예: 낙상, 치매, 저혈압)를 포함하고 있습니다.",
            {'matched_drugs': risks}
        ))
    return results

def check_interaction(prescription_drugs: List[str], dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """약물 병용 금기 검사 (3.py 기반)"""
    results = []
    if len(prescription_drugs) < 2:
        return results
    
    # 처방된 모든 약물 쌍을 검사
    for i in range(len(prescription_drugs)):
        for j in range(i + 1, len(prescription_drugs)):
            drug_a = prescription_drugs[i]
            drug_b = prescription_drugs[j]
            
            # 순서에 관계없이 검색: (A=1 & B=2) 또는 (B=1 & A=2)
            match_ab = dataframe[
                (dataframe['제품명1'].str.contains(drug_a, case=False, na=False)) &
                (dataframe['제품명2'].str.contains(drug_b, case=False, na=False))
            ]
            match_ba = dataframe[
                (dataframe['제품명1'].str.contains(drug_b, case=False, na=False)) &
                (dataframe['제품명2'].str.contains(drug_a, case=False, na=False))
            ]
            
            matched_results = pd.concat([match_ab, match_ba]).drop_duplicates()
            
            if not matched_results.empty:
                reason = matched_results['금기사유'].iloc[0]
                results.append(format_result(
                    '병용 금기/주의', '금기',
                    f"'{drug_a}'와 '{drug_b}'는 병용 금기 또는 주의 약물입니다. (사유: {reason})",
                    {'drug_a': drug_a, 'drug_b': drug_b, 'reason': reason}
                ))
    return results

def check_efficacy_duplication(prescription_drugs: List[str], dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """효능군 중복 검사 (9.py 기반)"""
    results = []
    
    # 처방된 약물별 효능군 그룹 추출
    drug_groups = {}  # {group_key: [drug_names]}
    
    for drug in prescription_drugs:
        matched = dataframe[dataframe['제품명'].str.contains(drug, case=False, na=False)]
        
        if not matched.empty:
            for _, row in matched.iterrows():
                group_key = f"{row['효능군']} ({row['그룹구분']})"
                if group_key in drug_groups:
                    drug_groups[group_key].append(row['제품명'])
                else:
                    drug_groups[group_key] = [row['제품명']]

    # 중복 검사
    for group, drugs in drug_groups.items():
        unique_drugs = set(drugs)
        if len(unique_drugs) > 1:
            results.append(format_result(
                '효능군 중복 주의', '주의',
                f"동일 효능군에 속하는 약물이 2가지 이상 처방되었습니다. (효능군: {group}, 약물: {', '.join(unique_drugs)})",
                {'efficacy_group': group, 'duplicated_drugs': list(unique_drugs)}
            ))
            
    return results

def check_pregnancy_risk(prescription_drug: str, dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """임부 금기 약물 검사 (7.py 기반)"""
    results = []
    matched = dataframe[dataframe['제품명'].str.contains(prescription_drug, case=False, na=False)]
    
    if not matched.empty:
        for _, row in matched[['제품명', '성분명', '금기등급', '상세정보']].drop_duplicates().iterrows():
            severity = '금기' if '1등급' in str(row['금기등급']) or '2등급' in str(row['금기등급']) else '주의'
            
            results.append(format_result(
                '임부 금기/주의', severity,
                f"임부 금기/주의 약물로 확인되었습니다. (등급: {row['금기등급']}, 사유: {row['상세정보']})",
                row.to_dict()
            ))
    return results

def check_lactating_risk(prescription_drug: str, dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """수유부 주의 약물 검사 (4.py 기반)"""
    results = []
    matched = dataframe[dataframe['제품명'].str.contains(prescription_drug, case=False, na=False)]
    
    if not matched.empty:
        for _, row in matched[['제품명', '성분명', '비고']].drop_duplicates().iterrows():
            results.append(format_result(
                '수유부 주의', '주의',
                f"수유부 주의 약물로 확인되었습니다. (사유: {row['비고']})",
                row.to_dict()
            ))
    return results

def check_child_age_risk(prescription_drug: str, age: int, age_unit: str, dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """어린이 연령 금기 약물 검사 (5.py 기반)"""
    results = []
    normalized_unit = normalize_age_unit(age_unit)
    matched = dataframe[dataframe['제품명'].str.contains(prescription_drug, case=False, na=False)]
    
    for _, row in matched.iterrows():
        try:
            target_age = row['특정연령_숫자']
            target_unit = row['특정연령단위_정규화']
            
            is_restricted = False
            
            if target_unit == '개월' and normalized_unit == '개월':
                is_restricted = age <= target_age
            elif target_unit == '년' and normalized_unit == '년':
                is_restricted = age <= target_age
            elif target_unit == '개월' and normalized_unit == '년':
                is_restricted = (age * 12) <= target_age
            elif target_unit == '년' and normalized_unit == '개월':
                # 연령 금기 기준이 '년'인데, 현재 환자가 '개월'인 경우 (극히 드물지만 처리)
                is_restricted = (age / 12) <= target_age

            if is_restricted:
                results.append(format_result(
                    '특정 연령 금기', '금기',
                    f"'{prescription_drug}'은(는) {row['특정연령']}{row['특정연령단위']} 미만에게 금기/주의입니다. (현재 연령: {age}{age_unit})",
                    row.to_dict()
                ))
        except:
            # 데이터 오류 등 예외 처리
            continue
            
    return results

def check_daily_max_dose_risk(prescription_item: Dict[str, Any], dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """1일 최대 투여 용량 초과 검사 (6.py 기반)"""
    results = []
    drug_name = prescription_item.get('name', '')
    dose_per_time = prescription_item.get('dose_per_time', 0)
    times_per_day = prescription_item.get('times_per_day', 0)
    
    if not drug_name or dose_per_time == 0 or times_per_day == 0:
        return results

    matched = dataframe[dataframe['제품명'].str.contains(drug_name, case=False, na=False)]
    
    for _, row in matched.iterrows():
        max_dose = row['1일최대투여량_숫자']
        component_content = row['점검기준 성분함량_숫자']
        
        # 일일 투여 총량 (성분 함량 기준) = 1회 복용량 * 1일 횟수 * 1정당 성분 함량
        daily_total_dose = dose_per_time * times_per_day * component_content
        
        if daily_total_dose > max_dose:
            results.append(format_result(
                '용량 초과 위험', '금기',
                f"일일 최대 투여 용량({max_dose}mg)을 초과했습니다. (처방 총량: {daily_total_dose:.1f}mg, 제품: {row['제품명']})",
                row.to_dict()
            ))
            
    return results

def check_duration_limit_risk(prescription_item: Dict[str, Any], dataframe: pd.DataFrame) -> List[Dict[str, str]]:
    """최대 투여 기간 초과 검사 (8.py 기반)"""
    results = []
    drug_name = prescription_item.get('name', '')
    duration_days = prescription_item.get('duration_days', 0)

    if not drug_name or duration_days == 0:
        return results
    
    matched = dataframe[dataframe['제품명'].str.contains(drug_name, case=False, na=False)]
    
    for _, row in matched.iterrows():
        max_days = row['최대투여기간일수_숫자']
        
        if duration_days > max_days:
            results.append(format_result(
                '투여 기간 초과 위험', '주의',
                f"처방 기간({duration_days}일)이 최대 투여 기간({max_days}일)을 초과했습니다. (제품: {row['제품명']}, 사유: {row['상세정보']})",
                row.to_dict()
            ))
            
    return results


# ==============================================================================
# 5. 종합 위험 분석 마스터 함수
# ==============================================================================

def run_comprehensive_risk_analysis(
    patient_profile: Dict[str, Any], 
    prescription: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """
    환자 정보와 처방전을 바탕으로 모든 안전성 검사를 종합적으로 수행합니다.
    """
    all_risks: List[Dict[str, str]] = []
    
    # 처방 약물 목록 (이름만) 추출
    drug_names = [item['name'] for item in prescription]
    
    # ----------------------------------------------------
    # 1. 약물-약물 상호작용 및 중복 검사 (환자 무관)
    # ----------------------------------------------------
    print("\n[1. 약물 상호작용 및 중복 검사]")
    all_risks.extend(check_interaction(drug_names, DF_CONCURRENT))
    all_risks.extend(check_efficacy_duplication(drug_names, DF_DUPLICATION))

    # ----------------------------------------------------
    # 2. 환자 맞춤형 위험 검사
    # ----------------------------------------------------
    
    # A. 노인/기저질환 위험 검사
    if patient_profile.get('is_elderly'):
        print("\n[2A. 노인/기저질환 주의 약물 검사]")
        for drug in drug_names:
            all_risks.extend(check_elderly_risk(drug, DF_ELDERLY, RISK_KEYWORDS))
            
    # B. 임부/수유부 위험 검사
    if patient_profile.get('is_pregnant'):
        print("\n[2B. 임부 금기 약물 검사]")
        for drug in drug_names:
            all_risks.extend(check_pregnancy_risk(drug, DF_PREGNANCY))
            
    if patient_profile.get('is_lactating'):
        print("\n[2C. 수유부 주의 약물 검사]")
        for drug in drug_names:
            all_risks.extend(check_lactating_risk(drug, DF_LACTATING))

    # C. 소아/청소년 연령 금기 검사
    child_age = patient_profile.get('child_age')
    child_age_unit = patient_profile.get('child_age_unit')
    if child_age is not None and child_age_unit:
        print("\n[2D. 특정 연령 금기 약물 검사 (소아/청소년)]")
        for drug in drug_names:
            all_risks.extend(check_child_age_risk(drug, child_age, child_age_unit, DF_AGE))
            
    # D. 용량 및 기간 초과 검사 (처방 상세 정보 필요)
    print("\n[2E. 용량 및 투여 기간 초과 검사]")
    for item in prescription:
        all_risks.extend(check_daily_max_dose_risk(item, DF_DOSAGE))
        all_risks.extend(check_duration_limit_risk(item, DF_DURATION))
        
    return all_risks

# ==============================================================================
# 6. 테스트 실행 예시
# ==============================================================================

if __name__ == "__main__":
    
    # --- 테스트 케이스 정의 ---
    
    # 1. 환자 프로필 (다양한 위험 요소 포함)
    test_patient_profile = {
        'name': '김안전',
        'age': 75,                      # 노인 기준
        'is_elderly': True,             # 노인 주의 약물 검사 활성화
        'is_pregnant': False,
        'is_lactating': False,
        'child_age': None,              # 소아 아님
        'child_age_unit': None,
        # is_elderly가 True이므로 노인 관련 위험을 검사
        
        # 다른 환자 테스트 케이스를 위한 주석 처리된 예시:
        # 'name': '박임산부', 'is_pregnant': True, 'is_lactating': False, 'is_elderly': False
        # 'name': '이아동', 'is_elderly': False, 'child_age': 5, 'child_age_unit': '년'
    }
    
    # 2. 처방전 (다양한 위험 시나리오 포함)
    # **주의: 실제 데이터셋의 샘플 제품명('노인주의약물_20240813.csv', '병용금기약물_5줄.csv', etc)을 기반으로 설정했습니다.**
    test_prescription = [
        # 1. 용량 초과 위험 (스틸녹스정 (10mg/정) - 졸피뎀. 1일 최대 10mg)
        # * DF_DOSAGE에 '타코펜정(아세트아미노펜)'이 있다고 가정하고 아세트아미노펜 성분 검사
        {'name': '타코펜정', 'dose_per_time': 2, 'times_per_day': 6, 'duration_days': 7}, # 일일 12정 복용. 용량 초과 예상 (6.py 스니펫 가정)
        
        # 2. 노인 주의 위험 (ethyl loflazepate: 낙상, 인지기능 저하 위험)
        {'name': '빅손정1밀리그람', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 30},
        
        # 3. 투여 기간 초과 위험 (스틸녹스정 - 졸피뎀. 최대 28일)
        {'name': '스틸녹스정', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 35}, # 28일 초과 예상
        
        # 4. 병용 금기 위험 (clarithromycin & simvastatin: 근병증 위험)
        {'name': '제클라정', 'dose_per_time': 1, 'times_per_day': 2, 'duration_days': 7},
        {'name': '심바로드정20밀리그람', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 30},
        
        # 5. 효능군 중복 위험 (듀얼로우정 & 듀이젠정: 혈압강하작용 Group 10 중복)
        {'name': '듀얼로우정', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 30},
        {'name': '듀이젠정', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 30},
        
        # 6. 임부 금기 위험 (임부 테스트 시 사용 가능)
        # {'name': '피마듀오정', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 30},
    ]

    # --- 종합 분석 실행 ---
    
    print("\n" + "="*80)
    print(f"🏥 종합 약물 안전성 분석 시작: 환자 '{test_patient_profile['name']}' ({test_patient_profile['age']}세)")
    print("="*80)
    
    analysis_results = run_comprehensive_risk_analysis(test_patient_profile, test_prescription)

    print("\n" + "="*80)
    print(f"🚨 최종 위험 분석 결과 (총 {len(analysis_results)}건의 위험 감지)")
    print("="*80)

    if not analysis_results:
        print("✅ 처방된 약물에서 특별한 위험은 감지되지 않았습니다.")
    else:
        for i, risk in enumerate(analysis_results):
            print(f"\n--- 위험 {i+1} ({risk['severity']}): {risk['type']} ---")
            print(f"  [메시지]: {risk['message']}")
            # 상세 정보는 Dict 형태로 출력되어 가독성을 높입니다.
            details = eval(risk['details'])
            for key, value in details.items():
                 # DataFrame row 객체가 포함된 경우 예쁘게 출력 (딕셔너리, 시리즈 등)
                 if isinstance(value, dict) or isinstance(value, pd.Series):
                      print(f"  [{key} 상세]:")
                      for sub_key, sub_value in value.items():
                          # 데이터프레임의 to_string 결과를 역변환한 경우를 대비
                          if isinstance(sub_value, str) and '\n' in sub_value:
                             print(f"    {sub_key}: \n{sub_value}")
                          else:
                             print(f"    {sub_key}: {sub_value}")
                 else:
                     print(f"  [{key}]: {value}")
            
    print("\n" + "="*80)

    # --- 환자 정보 변경 후 소아 연령 금기 테스트 예시 ---
    print("\n\n--- 🧪 추가 테스트: 소아 환자 연령 금기 검사 ---")
    child_patient_profile = {
        'name': '이아동', 
        'age': 5, 
        'is_elderly': False, 
        'is_pregnant': False, 
        'is_lactating': False,
        'child_age': 5, 
        'child_age_unit': '년' # 5세 (6세 미만 금기인 약물에 걸릴 수 있음)
    }
    child_prescription = [
        # 데이터셋에 '지르텍정' (6세 미만 금기)이 있다고 가정
        {'name': '지르텍정', 'dose_per_time': 1, 'times_per_day': 1, 'duration_days': 7},
    ]
    
    child_results = run_comprehensive_risk_analysis(child_patient_profile, child_prescription)
    
    print("\n" + "="*80)
    print(f"🚨 소아 환자 연령 금기 분석 결과 (총 {len(child_results)}건의 위험 감지)")
    print("="*80)
    
    if not child_results:
        print("✅ 소아 환자에게 특별한 위험은 감지되지 않았습니다.")
    else:
        for risk in child_results:
            print(f"\n--- 위험 ({risk['severity']}): {risk['type']} ---")
            print(f"  [메시지]: {risk['message']}")