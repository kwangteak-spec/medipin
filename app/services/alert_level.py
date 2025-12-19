def determine_alert_level(confidence: dict, comparison: dict | None = None):
    """
    OCR 신뢰도 + 비교 결과 기반 alert 레벨 생성
    """

    # ① 비교 결과가 위험하면 최우선 차단
    if comparison and not comparison["is_safe"]:
        return {
            "level": "BLOCKED",
            "reason": "처방전과 약봉투 내용이 일치하지 않습니다."
        }

    # ② OCR 신뢰도 기준
    if confidence["level"] == "LOW":
        return {
            "level": "WARNING",
            "reason": "OCR 인식 정확도가 낮습니다."
        }

    if confidence["level"] == "MEDIUM":
        return {
            "level": "CAUTION",
            "reason": "OCR 인식 정확도가 보통 수준입니다."
        }

    # ③ 문제 없음
    return {
        "level": "NORMAL",
        "reason": None
    }
