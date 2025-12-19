import pandas as pd
import numpy as np

# 현재 업로드된 연령금기 약물 파일 로드 (인코딩 처리)
csv_file = '한국의약품안전관리원_연령금기_20240625.csv'
try:
    df_age_restriction = pd.read_csv(csv_file, encoding='cp949')
except UnicodeDecodeError:
    df_age_restriction = pd.read_csv(csv_file, encoding='utf-8')

# -----------------
# 1. 데이터 클리닝 및 키 컬럼 확인
# -----------------
df_age_restriction = df_age_restriction.fillna('정보 없음')

# '특정연령단위'를 표준화 (예: '세' -> '년', '개월 이하' -> '개월')
def normalize_unit(unit):
    if '개월' in unit:
        return '개월'
    elif '세' in unit or '년' in unit:
        return '년'
    return unit

df_age_restriction['특정연령단위_정규화'] = df_age_restriction['특정연령단위'].apply(normalize_unit)
df_age_restriction['특정연령_숫자'] = pd.to_numeric(df_age_restriction['특정연령'], errors='coerce')


# -----------------
# 2. 어린이 연령 금기 위험 정보 추출 함수
# -----------------
def check_child_age_restriction(prescription_name, child_age, age_unit, df_data):
    """
    처방전 약품명이 특정 나이의 어린이에게 금기인지 확인합니다.
    """
    
    # 처방전 약품명 매칭
    matched_drugs = df_data[df_data['제품명'].str.contains(prescription_name, case=False, na=False)]
    
    if matched_drugs.empty:
        return f"✅ '{prescription_name}' (으)로 검색된 연령 금기 약물은 없습니다."

    # 매칭된 약물 중, 해당 어린이에게 금기인 약물 필터링
    risky_drugs = []
    
    for index, row in matched_drugs.iterrows():
        restriction_age = row['특정연령_숫자']
        restriction_unit = row['특정연령단위_정규화']
        
        # 유효한 연령 정보가 있어야 비교 가능
        if np.isnan(restriction_age) or restriction_unit == '정보 없음':
            continue

        is_restricted = False

        if restriction_unit == '개월':
            # 금기 연령이 '개월'이고, 입력된 연령이 '년'이면 '개월'로 변환 후 비교
            input_age_in_months = child_age if age_unit == '개월' else child_age * 12
            
            # 입력된 개월 수가 금기 개월 수보다 작거나 같으면 금기
            if input_age_in_months <= restriction_age:
                is_restricted = True
        
        elif restriction_unit == '년':
            # 금기 연령이 '년'일 때 (예: 6세 미만 금기)
            # 입력된 연령이 '년'이면 직접 비교
            if age_unit == '년' and child_age < restriction_age:
                is_restricted = True
            # 입력된 연령이 '개월'이면 1년 미만으로 간주 (1세 미만)
            elif age_unit == '개월' and restriction_age >= 1: # 1년(1세) 미만은 금기
                is_restricted = True

        if is_restricted:
            risky_drugs.append(row)

    if risky_drugs:
        output = [f"==============================================================="]
        output.append(f"🚨🚨 연령 금기 경고: {child_age}{age_unit} 아동에게 '{prescription_name}' 투여 시 주의")
        output.append(f"===============================================================")
        
        # 고유한 위험 사유만 추출
        unique_risks = pd.DataFrame(risky_drugs)[['제품명', '특정연령', '특정연령단위', '상세정보']].drop_duplicates()
        
        for index, row in unique_risks.iterrows():
            output.append(f" - [제품명]: {row['제품명']}")
            output.append(f" - [금기 연령]: {row['특정연령']} {row['특정연령단위']}")
            output.append(f" - [상세 사유]: {row['상세정보']}")
            output.append("-" * 50)
            
        output.append(f"⚠️ 권고: 해당 약물은 {row['특정연령']} {row['특정연령단위']} 아동에게 투여 금지되거나 신중해야 하므로, 반드시 전문가(의사/약사)와 상담하세요.")
        return '\n'.join(output)
    else:
        return f"✅ '{prescription_name}'은(는) {child_age}{age_unit} 아동에게 연령 금기 기준에 해당하지 않습니다."

# -----------------
# 3. 테스트 실행
# -----------------
print("--- [어린이 연령 금기 약물 처방전 안전 점검 테스트] ---")

# 테스트 1: 세티리진(Cetirizine) - 보통 6세 미만 금기
# 5세 아동 테스트
result_1 = check_child_age_restriction("세티리진정", 5, '년', df_age_restriction)
print(result_1)

print("\n" + "#" * 30 + "\n")

# 테스트 2: lidocaine, prilocaine 크림 - 3개월 이하 금기
# 2개월 영아 테스트
result_2 = check_child_age_restriction("아네스크림", 2, '개월', df_age_restriction)
print(result_2)