import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, TypedDict, Optional

# --- 0. 데이터 모델 정의 ---

# 환자 정보 모델 (Python 3.8+에서 TypedDict 사용 가능)
class Patient(TypedDict):
    age: int
    is_pregnant: bool
    is_lactating: bool

# 처방 항목 모델
class PrescriptionItem(TypedDict):
    name: str # 제품명
    dose_per_take: int # 1회 투여량 (정/캡슐 등)
    times_per_day: int # 1일 투여 횟수
    duration_days: int # 투여 기간 (일)
    
# 분석 결과 모델
class AnalysisResult(TypedDict):
    type: str  # 위험 유형 (e.g., 'Elderly Caution', 'Concurrent Contraindication')
    drug: str  # 관련 약품명 (단일 또는 조합)
    level: str # 위험 레벨 (e.g., 'Warning', 'Contraindication')
    message: str # 상세 설명

# --- 1. 데이터 로드 및 전처리 ---

def load_csv_data(file_name: str, key_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """CSV 파일을 로드하고 인코딩 및 결측치를 처리합니다."""
    print(f"  🔍 데이터셋 로딩: {file_name}")
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_name, encoding='utf-8')
        except FileNotFoundError:
            print(f"  ❌ 오류: 파일을 찾을 수 없습니다: {file_name}. 이 데이터셋에 대한 검사를 건너뜁니다.")
            return pd.DataFrame()
    except FileNotFoundError:
        print(f"  ❌ 오류: 파일을 찾을 수 없습니다: {file_name}. 이 데이터셋에 대한 검사를 건너뜁니다.")
        return pd.DataFrame()
    
    # 필요한 컬럼만 선택하고, 결측치를 '정보 없음'으로 대체
    if key_columns:
        df = df[key_columns].copy()
    
    # 모든 문자열 타입 컬럼의 결측치 처리
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna('정보 없음')

    return df

# 파일 경로 설정 (사용자 환경에 맞게 조정)
FILE_ELDERLY_CAUTION = '노인주의약물.csv'
FILE_CONCURRENT_PROHIBITED = '한국의약품안전관리원_병용금기약물_5줄.csv'
FILE_HAZARDOUS = '건강보험심사평가원_의약품유통_위해의약품 정보_20241031.csv'
FILE_PREGNANCY_CAUTION = '한국의약품안전관리원_임부금기약물_20240625.csv'
FILE_DOSAGE_LIMIT = '한국의약품안전관리원_용량주의약물_20240501.csv'
FILE_DURATION_LIMIT = '한국의약품안전관리원_투여기간주의약물_20231108.csv'


print("--- 📚 데이터 로딩 시작 ---")

# 1. 노인 주의 약물 데이터 로드
DF_ELDERLY = load_csv_data(
    FILE_ELDERLY_CAUTION, 
    ['제품명', '성분명', '약품상세정보']
)

# 2. 병용 금기 약물 데이터 로드
DF_CONCURRENT = load_csv_data(
    FILE_CONCURRENT_PROHIBITED, 
    ['제품명1', '제품명2', '금기사유']
)

# 3. 위해 의약품 데이터 로드
DF_HAZARDOUS = load_csv_data(
    FILE_HAZARDOUS, 
    ['제품명', '회수사유', '위험등급']
)
# 위험등급이 숫자로 되어있을 경우 문자열로 통일
if '위험등급' in DF_HAZARDOUS.columns:
    DF_HAZARDOUS['위험등급'] = DF_HAZARDOUS['위험등급'].astype(str)

# 4. 임부 금기 약물 데이터 로드
DF_PREGNANCY = load_csv_data(
    FILE_PREGNANCY_CAUTION,
    ['제품명', '성분명', '금기등급', '상세정보']
)

# 5. 용량 주의 약물 데이터 로드 (시뮬레이션을 위해 최대투여량만 정제)
DF_DOSAGE = load_csv_data(
    FILE_DOSAGE_LIMIT,
    ['제품명', '점검기준 성분함량', '1일최대투여량']
)
if not DF_DOSAGE.empty:
    # '1일최대투여량'에서 숫자와 단위(mg/g)만 추출하여 단순화 (실제로는 더 복잡한 정제 필요)
    def extract_max_dose_mg(text):
        match = re.search(r'(\d+)\s*mg', str(text), re.IGNORECASE)
        if match:
            return int(match.group(1))
        # g -> mg 변환 단순화
        match_g = re.search(r'(\d+)\s*g', str(text), re.IGNORECASE)
        if match_g:
            return int(match_g.group(1)) * 1000
        return np.nan

    DF_DOSAGE['max_dose_mg'] = DF_DOSAGE['1일최대투여량'].apply(extract_max_dose_mg)
    DF_DOSAGE['mg_per_take'] = DF_DOSAGE['점검기준 성분함량'].apply(lambda x: extract_max_dose_mg(x.split('(')[-1].replace(')', ''))) # 제품명 뒤 괄호 속 성분량 추출 시도
    DF_DOSAGE = DF_DOSAGE.dropna(subset=['max_dose_mg', 'mg_per_take'])


# 6. 투여 기간 주의 약물 데이터 로드 (시뮬레이션을 위해 최대투여기간만 정제)
DF_DURATION = load_csv_data(
    FILE_DURATION_LIMIT,
    ['제품명', '최대투여기간일수', '성분명']
)
if not DF_DURATION.empty:
    DF_DURATION['max_days'] = pd.to_numeric(DF_DURATION['최대투여기간일수'], errors='coerce')
    DF_DURATION = DF_DURATION.dropna(subset=['max_days'])


print("--- 🏁 데이터 로딩 완료 ---")

# --- 2. 안전성 검사 함수 구현 ---

def check_elderly_caution(drug_name: str, patient_age: int, df_elderly: pd.DataFrame) -> List[AnalysisResult]:
    """노인 주의 약물 목록을 검사합니다."""
    results: List[AnalysisResult] = []
    
    if patient_age < 65:
        return results # 65세 미만은 검사 불필요

    matched = df_elderly[df_elderly['제품명'].str.contains(drug_name, case=False, na=False)]
    
    if not matched.empty:
        # 노인 주의 약물 상세 정보 추출
        risk_info = matched['약품상세정보'].iloc[0]
        results.append({
            'type': '노인 주의 약물',
            'drug': drug_name,
            'level': 'Warning',
            'message': f"고령(65세 이상) 환자 주의: {risk_info}"
        })
    return results

def check_concurrent_contraindication(prescription: List[PrescriptionItem], df_concurrent: pd.DataFrame) -> List[AnalysisResult]:
    """처방전 내 약물 간 병용 금기 여부를 검사합니다."""
    results: List[AnalysisResult] = []
    drug_names = [p['name'] for p in prescription]
    
    # 처방된 모든 약물 쌍을 검사
    for i in range(len(drug_names)):
        for j in range(i + 1, len(drug_names)):
            drug_a = drug_names[i]
            drug_b = drug_names[j]
            
            # (A=1 & B=2) 또는 (B=1 & A=2) 조합 검색 (제품명에 부분 일치하는 경우 포함)
            match_ab = df_concurrent[
                (df_concurrent['제품명1'].str.contains(drug_a, na=False)) & 
                (df_concurrent['제품명2'].str.contains(drug_b, na=False))
            ]
            match_ba = df_concurrent[
                (df_concurrent['제품명1'].str.contains(drug_b, na=False)) & 
                (df_concurrent['제품명2'].str.contains(drug_a, na=False))
            ]
            
            matched_results = pd.concat([match_ab, match_ba]).drop_duplicates()

            if not matched_results.empty:
                # 첫 번째 금기 사유를 추출
                reason = matched_results['금기사유'].iloc[0]
                results.append({
                    'type': '병용 금기 약물',
                    'drug': f"{drug_a} & {drug_b}",
                    'level': 'Contraindication',
                    'message': f"두 약물 병용 금기 사유: {reason}"
                })
    return results

def check_hazardous_drug(drug_name: str, df_hazardous: pd.DataFrame) -> List[AnalysisResult]:
    """회수 및 위해 의약품 목록을 검사합니다."""
    results: List[AnalysisResult] = []
    
    matched = df_hazardous[df_hazardous['제품명'].str.contains(drug_name, case=False, na=False)]
    
    if not matched.empty:
        # 가장 최근/심각한 위험 정보 추출
        row = matched.iloc[0]
        level = f"위험등급 {row['위험등급']}" if row['위험등급'] != '정보 없음' else 'Serious Warning'
        results.append({
            'type': '위해 의약품 (회수/부적합)',
            'drug': drug_name,
            'level': level,
            'message': f"식약처 회수 및 위해 의약품으로 등록됨. 사유: {row['회수사유']}"
        })
    return results

def check_pregnancy_lactating_risk(drug_name: str, patient: Patient, df_pregnancy: pd.DataFrame) -> List[AnalysisResult]:
    """임부 및 수유부 금기 약물 목록을 검사합니다. (현재 임부 데이터로 통합 검색)"""
    results: List[AnalysisResult] = []
    
    if not patient['is_pregnant'] and not patient['is_lactating']:
        return results

    matched = df_pregnancy[df_pregnancy['제품명'].str.contains(drug_name, case=False, na=False)]

    if not matched.empty:
        # 금기 등급 및 상세 정보 추출
        grade = matched['금기등급'].iloc[0]
        detail = matched['상세정보'].iloc[0]
        
        target = []
        if patient['is_pregnant']: target.append("임부")
        # 수유부 데이터셋이 별도로 필요하지만, 여기서는 임부 금기 데이터로 통합하여 사용합니다.
        if patient['is_lactating'] and grade in ['1', '2']: target.append("수유부") 
        
        if target:
            level = 'Contraindication' if grade == '1' else 'Severe Warning'
            results.append({
                'type': '임부/수유부 금기',
                'drug': drug_name,
                'level': level,
                'message': f"{'/'.join(target)} {grade}등급 금기/주의 약물. 상세: {detail}"
            })
    return results

def check_dosage_limit(item: PrescriptionItem, df_dosage: pd.DataFrame) -> List[AnalysisResult]:
    """1일 최대 투여량 초과 여부를 검사합니다. (단순화된 로직)"""
    results: List[AnalysisResult] = []
    
    # 제품명으로 최대 투여량 정보 찾기 (부분 일치 검색)
    matched = df_dosage[df_dosage['제품명'].str.contains(item['name'], case=False, na=False)]

    if not matched.empty:
        # 해당 약품에 대한 모든 용량 정보를 순회하며 검사
        for index, row in matched.iterrows():
            max_dose = row['max_dose_mg']  # 1일 최대 허용 용량 (mg)
            dose_mg = row['mg_per_take']   # 1회 투여 정/캡슐 당 성분 함량 (mg)
            
            # 실제 1일 총 투여량 계산 (정제 수 * 횟수 * 정제당 성분량)
            prescribed_daily_dose = item['dose_per_take'] * item['times_per_day'] * dose_mg
            
            if prescribed_daily_dose > max_dose:
                results.append({
                    'type': '용량 초과 위험',
                    'drug': item['name'],
                    'level': 'Contraindication',
                    'message': (
                        f"1일 최대 투여량 초과 위험. 처방: {prescribed_daily_dose}mg. "
                        f"최대 허용: {max_dose}mg. (기준 성분: {row['점검기준 성분함량']})"
                    )
                })
                # 하나의 제품에 대해 용량 초과가 확인되면 루프 종료 (가장 심각한 것 하나만 보고)
                break 

    return results

def check_duration_limit(item: PrescriptionItem, df_duration: pd.DataFrame) -> List[AnalysisResult]:
    """최대 투여 기간 초과 여부를 검사합니다. (단순화된 로직)"""
    results: List[AnalysisResult] = []
    
    # 제품명으로 최대 투여 기간 정보 찾기 (부분 일치 검색)
    matched = df_duration[df_duration['제품명'].str.contains(item['name'], case=False, na=False)]

    if not matched.empty:
        # 최대 투여 기간(일)을 추출 (가장 짧은 기간을 기준으로 검사)
        max_days = matched['max_days'].min()
        
        if item['duration_days'] > max_days:
            # 해당 약품의 성분명 추출
            ingredient = matched['성분명'].iloc[0] if not matched.empty else item['name']
            
            results.append({
                'type': '투여 기간 초과 위험',
                'drug': item['name'],
                'level': 'Warning',
                'message': (
                    f"최대 투여 기간 초과 위험. 처방 기간: {item['duration_days']}일. "
                    f"최대 권장/제한 기간: {max_days}일. (성분: {ingredient})"
                )
            })

    return results


# --- 3. 통합 분석 함수 ---

def analyze_prescription(patient: Patient, prescriptions: List[PrescriptionItem]) -> List[AnalysisResult]:
    """환자와 처방전 정보를 기반으로 통합 안전성 분석을 실행합니다."""
    
    all_results: List[AnalysisResult] = []
    
    print("\n" + "="*80)
    print(f"🏥 처방전 안전성 통합 분석 시작 (환자: {patient['age']}세, 임부: {patient['is_pregnant']}, 수유부: {patient['is_lactating']})")
    print("="*80)
    
    # 1. 병용 금기 검사 (약물 간 상호작용)
    if not DF_CONCURRENT.empty:
        print("\n[1. 병용 금기 약물 검사]")
        all_results.extend(check_concurrent_contraindication(prescriptions, DF_CONCURRENT))
    else:
        print("  - 데이터셋 부재로 검사 생략.")
        
    # 2. 개별 약물 검사 (노인주의, 위해의약품, 임부/수유부, 용량, 기간)
    print("\n[2. 개별 약물 안전성 검사]")
    for item in prescriptions:
        drug_name = item['name']
        
        print(f"  > 약품: {drug_name}")
        
        # 노인 주의 검사
        if not DF_ELDERLY.empty:
            all_results.extend(check_elderly_caution(drug_name, patient['age'], DF_ELDERLY))
        
        # 위해 의약품 검사
        if not DF_HAZARDOUS.empty:
            all_results.extend(check_hazardous_drug(drug_name, DF_HAZARDOUS))
            
        # 임부/수유부 금기 검사
        if not DF_PREGNANCY.empty:
            all_results.extend(check_pregnancy_lactating_risk(drug_name, patient, DF_PREGNANCY))
            
        # 용량 초과 검사
        if not DF_DOSAGE.empty:
            all_results.extend(check_dosage_limit(item, DF_DOSAGE))
            
        # 투여 기간 초과 검사
        if not DF_DURATION.empty:
            all_results.extend(check_duration_limit(item, DF_DURATION))

    return all_results

# --- 4. 실행 예시 ---

# 테스트 환자 및 처방전 데이터 정의
patient_senior: Patient = {'age': 70, 'is_pregnant': False, 'is_lactating': False}
patient_young_female: Patient = {'age': 30, 'is_pregnant': True, 'is_lactating': False}

# 시뮬레이션 처방전 (데이터셋에 있는 약품명과 일치/부분 일치하도록 설정)
prescription_list: List[PrescriptionItem] = [
    # 1. 노인주의 약물 (데이터셋의 'ethyl loflazepate' 성분 포함 가정)
    {'name': '빅손정', 'dose_per_take': 1, 'times_per_day': 1, 'duration_days': 7}, 
    
    # 2. 병용금기 약물 (데이터셋의 '제클라정'과 '심바로드정' 조합 가정)
    {'name': '제클라정', 'dose_per_take': 1, 'times_per_day': 2, 'duration_days': 10}, 
    {'name': '심바로드정', 'dose_per_take': 1, 'times_per_day': 1, 'duration_days': 30}, 
    
    # 3. 위해의약품 (데이터셋의 '바른진피' 포함 가정)
    {'name': '바른진피', 'dose_per_take': 1, 'times_per_day': 3, 'duration_days': 90},
    
    # 4. 임부 금기 약물 (데이터셋의 '피마듀오정' 포함 가정)
    {'name': '피마듀오정', 'dose_per_take': 1, 'times_per_day': 1, 'duration_days': 30},
    
    # 5. 용량 초과 예상 (데이터셋의 '리스카펜정'(Acetaminophen) 400mg/정, 최대 4000mg 가정)
    # 1회 3정 * 1일 4회 * 400mg/정 = 4800mg -> 초과 예상
    {'name': '리스카펜정', 'dose_per_take': 3, 'times_per_day': 4, 'duration_days': 5}, 
    
    # 6. 기간 초과 예상 (데이터셋의 '스틸녹스정' 최대 28일 가정)
    {'name': '스틸녹스정', 'dose_per_take': 1, 'times_per_day': 1, 'duration_days': 35}, 
]

# --- 5. 분석 실행 및 결과 출력 ---

# 1. 70세 환자 분석
print("\n" + "#"*80)
print("### [CASE 1] 70세 노인 환자의 처방전 분석 ###")
print("#"*80)
results_senior = analyze_prescription(patient_senior, prescription_list)

# 2. 30세 임부 환자 분석
print("\n" + "#"*80)
print("### [CASE 2] 30세 임부(Pregnant) 환자의 처방전 분석 ###")
print("#"*80)
results_young_female = analyze_prescription(patient_young_female, prescription_list)


def print_report(title: str, results: List[AnalysisResult]):
    """분석 결과를 깔끔하게 정리하여 출력합니다."""
    print("\n" + "="*80)
    print(f"🚨 {title} - 최종 안전성 분석 보고서 (총 {len(results)}건의 위험 감지)")
    print("="*80)
    
    if not results:
        print("✅ 모든 처방 항목이 검사 기준을 통과했습니다.")
        return
        
    for i, res in enumerate(results):
        level_str = ""
        if res['level'] in ['Contraindication', 'Severe Warning', '위험등급 1']:
            level_str = "🔴 금기/중대 위험"
        elif res['level'] in ['Warning', '위험등급 2', 'Serious Warning']:
            level_str = "🟠 주의/경고"
        else:
            level_str = "🟡 정보 필요"
            
        print(f"\n[{i+1}. {res['type']}] - {level_str}")
        print(f"  - 관련 약품: {res['drug']}")
        print(f"  - 위험 수준: {res['level']}")
        print(f"  - 상세 사유: {res['message']}")
        print("-" * 60)

# 보고서 출력
print_report("70세 노인 환자", results_senior)
print_report("30세 임부 환자", results_young_female)

# 데이터셋 로드에 문제가 있는 경우 (파일명을 확인하세요.)
if DF_ELDERLY.empty or DF_CONCURRENT.empty or DF_HAZARDOUS.empty:
    print("\n\n⚠️ 주의: 일부 데이터셋 파일을 찾을 수 없거나 로드할 수 없어 일부 검사가 생략되었습니다. 파일명이 올바른지 확인해주세요.")