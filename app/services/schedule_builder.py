from datetime import datetime, timedelta
from typing import List, Dict

BASE_TIMES = {
    "아침": "09:00",
    "점심": "13:00",
    "저녁": "19:00",
    "취침전": "22:30"
}


def build_schedule_from_normalized_data(
    medicines: List[Dict],
    start_date: datetime | None = None
) -> List[Dict]:

    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0)

    results = []

    for med in medicines:
        end_date = start_date + timedelta(days=med["days"] - 1)
        occurrences = []

        for day_offset in range(med["days"]):
            target_date = start_date + timedelta(days=day_offset)

            for timing in med["timing"]:
                if timing not in BASE_TIMES:
                    continue

                hour, minute = map(int, BASE_TIMES[timing].split(":"))
                hour, minute = adjust_meal_time(hour, minute, med["meal_relation"])

                occurrences.append({
                    "datetime": (
                        target_date.replace(hour=hour, minute=minute)
                        .isoformat(timespec="minutes")
                    ),
                    "timing": timing,
                    "notify": True
                })

        results.append({
            "drug_name": med["name"],
            "dose": med["dose"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "occurrences": occurrences
        })

    return results


def build_schedule_from_ocr(parsed_result: dict):
    """
    기존 OCR 파이프라인 호환용 래퍼 함수
    """
    from app.services.medication_normalizer import normalize_medications

    normalized = normalize_medications(parsed_result)
    return build_schedule_from_normalized_data(normalized)


def adjust_meal_time(hour, minute, relation):
    if not relation:
        return hour, minute

    if "식전" in relation:
        minute -= 30
    elif "식후" in relation:
        minute += 30

    if minute < 0:
        hour -= 1
        minute += 60
    elif minute >= 60:
        hour += 1
        minute -= 60

    return hour, minute
