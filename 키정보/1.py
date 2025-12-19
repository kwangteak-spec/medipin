import pandas as pd
from typing import Dict, Any

# 파일명 정의
CSV_FILE = '건강보험심사평가원_의약품유통_위해의약품 정보_20241031.csv'

# 위험 등급 코드 설명 (식약처 기준)
# 1등급: 국민 보건에 미치는 위해도가 가장 심각한 경우 (치명적 결과 초래 가능)
# 2등급: 국민 보건에 미치는 위해도가 심각한 경우 (일시적/의학적 처치가 필요한 건강상의 문제 초래 가능)
# 3등급: 국민 보건에 미치는 위해도가 상대적으로 낮은 경우 (건강상의 문제 초래 가능성이 낮음)
RISK_LEVELS: Dict[Any, str] = {
    1: "1등급 (치명적 위해 가능)",
    2: "2등급 (심각한 위해 가능)",
    3: "3등급 (낮은 위해 가능)",
    None: "정보 없음",
    'NULL': "정보 없음"
}


def load_and_analyze_data(file_name: str) -> pd.DataFrame:
    """
    CSV 파일을 로드하고 초기 데이터 분석 및 클리닝을 수행합니다.
    """
    print(f"--- 1. 데이터셋 로딩 및 클리닝 시작: {file_name} ---")
    try:
        # 한국어 인코딩(CP949) 우선 시도, 실패 시 UTF-8 시도
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_name, encoding='utf-8')
        except FileNotFoundError:
            print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
            return pd.DataFrame()
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_name}")
        return pd.DataFrame()

    # '위험등급' 컬럼의 결측치 및 'NULL' 값을 처리
    df['위험등급'] = df['위험등급'].replace({None: 'NULL'}).fillna('NULL')
    
    # 데이터 구조 확인 (컬럼명, 데이터 타입)
    print("\n[컬럼 목록 및 데이터 타입]")
    print(df.info())
    print("-" * 50)
    
    # 핵심 컬럼 추출
    df_core = df[['제품명', '회수의무자', '회수일자', '회수사유', '위험등급']].copy()
    
    # 위험등급을 숫자로 변환 (분석 및 정렬을 위해)
    def parse_risk_level(level):
        try:
            return int(level)
        except (ValueError, TypeError):
            return 99 # 숫자 변환 불가능한 값(NULL, 정보 없음)은 가장 낮은 순위로 설정

    df_core['위험등급_순위'] = df_core['위험등급'].apply(parse_risk_level)
    
    print(f"\n✅ 로드 완료. 총 {len(df_core)}건의 위해의약품 정보 확인.")
    return df_core


def get_top_risky_drugs(df: pd.DataFrame, top_n: int = 10) -> None:
    """
    위험등급이 가장 높은(숫자가 낮은) 위해의약품 목록을 출력합니다.
    """
    if df.empty:
        return

    print("\n" + "="*70)
    print(f"  🚨 위험도 높은 위해의약품 목록 (상위 {top_n}건) 🚨")
    print("="*70)

    # 1. 위험등급 순위 (낮을수록 위험) 기준으로 정렬
    # 2. 회수일자 (최신순) 기준으로 2차 정렬
    sorted_df = df.sort_values(by=['위험등급_순위', '회수일자'], ascending=[True, False])
    
    # 상위 N개 추출 (중복 제품명 제거 후)
    top_risks = sorted_df.drop_duplicates(subset=['제품명', '회수사유']).head(top_n)

    for index, row in top_risks.iterrows():
        grade = row['위험등급_순위']
        display_grade = RISK_LEVELS.get(grade, row['위험등급'])

        print(f"[{display_grade}] - 제품명: {row['제품명']}")
        print(f"  - 회수 의무자: {row['회수의무자']}")
        print(f"  - 회수 일자: {row['회수일자']}")
        print(f"  - 회수 사유: {row['회수사유']}")
        print("-" * 70)


def filter_by_risk_reason(df: pd.DataFrame, keyword: str) -> None:
    """
    특정 회수 사유 키워드를 포함하는 위해의약품을 검색하고 출력합니다.
    """
    if df.empty:
        return

    print("\n" + "="*70)
    print(f"🔍 회수 사유 검색 결과: '{keyword}' 포함 약품")
    print("="*70)
    
    # '회수사유' 컬럼에서 키워드 검색
    filtered_df = df[df['회수사유'].str.contains(keyword, case=False, na=False)].drop_duplicates(subset=['제품명', '회수사유'])
    
    if filtered_df.empty:
        print(f"검색어 '{keyword}'에 해당하는 위해의약품이 없습니다.")
        return

    print(f"총 {len(filtered_df)}건의 위해의약품이 검색되었습니다.")
    print("-" * 50)
    
    # 결과 출력 (제품명, 위험등급, 회수사유만)
    for index, row in filtered_df.head(10).iterrows(): # 상위 10개만 출력
        display_grade = RISK_LEVELS.get(row['위험등급_순위'], row['위험등급'])
        print(f"[{display_grade}] {row['제품명']} (사유: {row['회수사유']})")


# --- 메인 실행 ---
df_harmful = load_and_analyze_data(CSV_FILE)

if not df_harmful.empty:
    # 1. 가장 위험한 약품 10개 출력
    get_top_risky_drugs(df_harmful, top_n=10)
    
    # 2. 특정 사유로 회수된 약품 검색 예시 (예: '부적합' 관련 제품)
    filter_by_risk_reason(df_harmful, "부적합")
    
    # 3. 특정 사유로 회수된 약품 검색 예시 (예: '기준' 관련 제품)
    filter_by_risk_reason(df_harmful, "기준")