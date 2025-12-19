import pandas as pd
from typing import List, Dict, Set

# 효능군 중복 주의 약물 파일명
CSV_FILE = '한국의약품안전관리원_효능군중복주의약물_20240813.csv'

# --- 1. 데이터 로드 및 전처리 ---

def load_and_preprocess_duplication_data(file_name: str) -> pd.DataFrame:
    """CSV 파일을 로드하고 효능군 중복 검사에 필요한 데이터프레임을 생성합니다."""
    print(f"데이터셋 로딩: {file_name}")
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return pd.DataFrame()
    
    # 중복 검사에 필요한 핵심 컬럼 선택 및 중복 제거
    # '효능군'과 '그룹구분'을 조합하여 고유한 중복 위험 그룹을 식별합니다.
    df = df[['제품명', '효능군', '그룹구분', '성분명']].drop_duplicates()
    df = df.fillna('정보 없음')
    
    return df

# 데이터 로드 및 전처리
DF_DUPLICATION = load_and_preprocess_duplication_data(CSV_FILE)

if DF_DUPLICATION.empty:
    print("데이터 로드에 실패하여 스크립트를 종료합니다.")
    exit()

print(f"✅ 효능군 중복 주의 약물 데이터 로딩 완료. 총 {len(DF_DUPLICATION)}개의 유효 데이터.")


# --- 2. 효능군 중복 검사 핵심 함수 ---

def check_efficacy_duplication(prescribed_drugs: List[str], df_data: pd.DataFrame) -> List[Dict[str, any]]:
    """
    처방된 약물 목록 내에서 동일 효능군 그룹의 약물이 중복되는지 검사합니다.
    """
    
    # 약물별 효능군 그룹 정보를 저장할 딕셔너리
    drug_to_groups = {} 
    
    # 이미 확인된 효능군 그룹을 저장하여 중복을 검사할 셋
    seen_groups: Set[str] = set() 
    
    # 최종 결과 목록
    results = []
    
    print("\n--- 1. 처방 약물별 효능군 정보 확인 ---")
    
    for drug in prescribed_drugs:
        
        # 1. 약물명으로 데이터 매칭 (대소문자 무시)
        matched = df_data[df_data['제품명'].str.contains(drug, case=False, na=False)]
        
        # 매칭되는 정보가 없는 경우
        if matched.empty:
            results.append({"status": "INFO", "drug": drug, "message": f"ℹ️ '{drug}'은(는) 중복 주의 약물 데이터셋에 없습니다."})
            continue

        # 2. 매칭된 효능군 그룹 추출
        # '효능군'과 '그룹구분'을 조합하여 고유한 그룹 ID를 생성합니다.
        matched_groups = []
        for _, row in matched.iterrows():
            group_id = f"{row['효능군']} ({row['그룹구분']})"
            matched_groups.append({
                "group_id": group_id,
                "efficacy_group": row['효능군'],
                "group_code": row['그룹구분'],
                "ingredient": row['성분명']
            })
            
        drug_to_groups[drug] = matched_groups
        print(f"[{drug}]: {', '.join([g['group_id'] for g in matched_groups])}")

    print("\n--- 2. 효능군 중복 검사 ---")
    
    # 3. 중복 검사
    duplication_detected = False
    
    for drug_1 in prescribed_drugs:
        if drug_1 not in drug_to_groups:
            continue
            
        groups_1 = drug_to_groups[drug_1]
        
        # 약물 1의 각 그룹에 대해
        for group_info_1 in groups_1:
            group_id_1 = group_info_1['group_id']
            
            # 이미 이 그룹이 중복으로 처리되었다면 건너뜁니다.
            if group_id_1 in seen_groups:
                continue

            # 나머지 약물들과 비교하여 중복을 찾습니다.
            for drug_2 in prescribed_drugs:
                if drug_1 == drug_2 or drug_2 not in drug_to_groups:
                    continue

                groups_2 = drug_to_groups[drug_2]
                
                # 약물 2의 그룹 중 약물 1의 그룹과 일치하는지 확인
                for group_info_2 in groups_2:
                    if group_id_1 == group_info_2['group_id']:
                        
                        # 중복 발견!
                        duplication_detected = True
                        seen_groups.add(group_id_1)
                        
                        results.append({
                            "status": "DANGER",
                            "group_id": group_id_1,
                            "drugs": [drug_1, drug_2],
                            "message": (
                                f"❌❌ 효능군 중복 경고: '{group_id_1}' 효능군에 속하는 약물이 중복 처방되었습니다.\n"
                                f"   - 관련 약물: '{drug_1}' 및 '{drug_2}'\n"
                                f"   - 성분: {group_info_1['ingredient']} (과량 투여 또는 부작용 위험 증가 가능)"
                            )
                        })
                        
                        # 중복이 발견되면 더 이상 이 그룹에 대해 다른 약물과 비교할 필요 없음
                        break 
                
                if group_id_1 in seen_groups:
                    break

    if not duplication_detected and len(prescribed_drugs) > 1:
        results.append({"status": "SAFE", "message": "✅ 처방된 약물들 간에 효능군 중복 위험이 확인되지 않았습니다."})
    elif len(prescribed_drugs) == 1:
        results.append({"status": "SAFE", "message": "✅ 처방된 약물이 하나이므로 효능군 중복 위험이 없습니다."})

    return results

# --- 3. 테스트 실행 ---

def run_tests():
    print("\n" + "="*50)
    print("  [효능군 중복 주의 약물 검사 시스템] - 테스트 시작")
    print("="*50)
    
    # 데이터셋 분석 결과:
    # 1. 듀얼로우정 (fimasartan)과 듀이젠정 (fimasartan + S-amlodipine)은 '혈압강하작용의약품 Group 10'에 모두 속함
    # 2. 펙수클루정 (Fexuprazan)과 위캡정 (Fexuprazan)은 '소화성궤양용제 Group 3'에 모두 속함
    
    # 테스트 1: 명백한 중복 (혈압강하작용의약품 Group 10 중복)
    drugs_1 = ["듀얼로우정", "듀이젠정"]
    print(f"\n--- [테스트 1: Group 10 중복] - 처방 목록: {drugs_1} ---")
    results_1 = check_efficacy_duplication(drugs_1, DF_DUPLICATION)
    for res in results_1:
        print(res['message'])
    
    # 테스트 2: 다른 효능군의 중복 (소화성궤양용제 Group 3 중복)
    drugs_2 = ["펙수클루정", "위캡정"]
    print(f"\n--- [테스트 2: Group 3 중복] - 처방 목록: {drugs_2} ---")
    results_2 = check_efficacy_duplication(drugs_2, DF_DUPLICATION)
    for res in results_2:
        print(res['message'])

    # 테스트 3: 중복 없음 + 데이터셋에 없는 약물 포함
    drugs_3 = ["듀얼로우정", "타이레놀", "펙수클루정"]
    print(f"\n--- [테스트 3: 중복 + 정보 없음] - 처방 목록: {drugs_3} ---")
    results_3 = check_efficacy_duplication(drugs_3, DF_DUPLICATION)
    for res in results_3:
        print(res['message'])

    # 테스트 4: 중복 없음 (효능군은 다르지만 같은 목록)
    drugs_4 = ["듀얼로우정", "펙수클루정"]
    print(f"\n--- [테스트 4: 중복 없음] - 처방 목록: {drugs_4} ---")
    results_4 = check_efficacy_duplication(drugs_4, DF_DUPLICATION)
    for res in results_4:
        print(res['message'])

# 메인 실행
if __name__ == "__main__":
    run_tests()