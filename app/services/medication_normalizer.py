import re
from typing import List, Dict


def normalize_medications(parsed_text: dict) -> List[Dict]:
    """
    약봉투 / 처방전 파싱 결과를
    🔹 표준화된 약 데이터 리스트로 변환

    return 예시:
    [
        {
            "name": "씬지록신정",
            "dose": "1정",
            "frequency_per_day": 2,
            "timing": ["아침", "저녁"],
            "meal_relation": "식후 30분",
            "days": 7
        }
    ]
    """

    normalized = []

    medicines = parsed_text.get("medicines", [])
    timing_info = parsed_text.get("timing", [])
    meal_info = parsed_text.get("meal_relation", "")

    for med in medicines:
        name = clean_med_name(med.get("name", ""))

        dose = normalize_dose(med.get("dose", "1정"))
        freq = normalize_frequency(med.get("frequency", ""))

        normalized.append({
            "name": name,
            "dose": dose,
            "frequency_per_day": freq["count"],
            "timing": freq["timings"],
            "meal_relation": meal_info or "무관",
            "days": parsed_text.get("days", 1)
        })

    return normalized


# ------------------------------
# 아래는 내부 헬퍼 함수들
# ------------------------------

def clean_med_name(name: str) -> str:
    """약 이름 정제"""
    name = name.replace("정", "").strip()
    name = re.sub(r"\(.*?\)", "", name)
    return name


def normalize_dose(dose: str) -> str:
    """투약량 정규화"""
    if "½" in dose or "0.5" in dose:
        return "0.5정"

    numbers = re.findall(r"\d+\.?\d*", dose)
    if numbers:
        return f"{numbers[0]}정"

    return "1정"


def normalize_frequency(text: str) -> dict:
    """
    복용 횟수 / 시간대 파싱
    """
    timings = []
    count = 1

    if "아침" in text:
        timings.append("아침")
    if "점심" in text:
        timings.append("점심")
    if "저녁" in text:
        timings.append("저녁")
    if "취침" in text:
        timings.append("취침전")

    if "1일 2회" in text or "BID" in text:
        count = 2
    elif "1일 3회" in text or "TID" in text:
        count = 3
    elif "QD" in text:
        count = 1

    if not timings:
        timings = ["아침"]

    return {
        "count": count,
        "timings": timings
    }
