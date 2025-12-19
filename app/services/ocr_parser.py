# app/services/ocr_parser.py

def parse_medication_text(text: str) -> dict:
    """
    OCR 텍스트를 받아 투약 정보를 구조화
    """

    meal_times = []
    timing = []

    if "아침" in text:
        meal_times.append("아침")
    if "점심" in text:
        meal_times.append("점심")
    if "저녁" in text:
        meal_times.append("저녁")
    if "취침전" in text:
        meal_times.append("취침전")

    if "식전 30분" in text or "식전30분" in text:
        timing.append("식전 30분")
    if "식후 30분" in text or "식후30분" in text:
        timing.append("식후 30분")

    return {
        "meal_times": meal_times,
        "timing": timing,
        "raw_text": text
    }
