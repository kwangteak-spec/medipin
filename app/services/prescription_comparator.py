from difflib import SequenceMatcher
from typing import List, Dict

SIMILARITY_THRESHOLD = 0.85


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def compare_prescription_and_bag(
    prescription: List[Dict],
    medicine_bag: List[Dict]
) -> dict:
    """
    ✅ 표준화(normalized)된 약 리스트 기준 비교
    """

    mismatches = []
    matched = []

    for rx in prescription:
        rx_name = rx["name"]
        found = False

        for bag in medicine_bag:
            score = similar(rx_name, bag["name"])

            if score >= SIMILARITY_THRESHOLD:
                found = True
                issues = []

                if rx["dose"] != bag["dose"]:
                    issues.append({
                        "field": "dose",
                        "prescription": rx["dose"],
                        "medicine_bag": bag["dose"]
                    })

                if set(rx["timing"]) != set(bag["timing"]):
                    issues.append({
                        "field": "timing",
                        "prescription": rx["timing"],
                        "medicine_bag": bag["timing"]
                    })

                if rx["days"] != bag["days"]:
                    issues.append({
                        "field": "days",
                        "prescription": rx["days"],
                        "medicine_bag": bag["days"]
                    })

                if issues:
                    mismatches.append({
                        "drug": rx_name,
                        "issues": issues
                    })
                else:
                    matched.append(rx_name)

                break

        if not found:
            mismatches.append({
                "drug": rx_name,
                "issues": ["약봉투에 없음"]
            })

    return {
        "is_safe": len(mismatches) == 0,
        "matched": matched,
        "mismatches": mismatches
    }
