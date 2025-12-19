def compare_medication(
    prescription: dict,
    medicine_bag: dict
) -> dict:
    """
    처방전 vs 약봉투 비교
    """

    results = []
    severity = "OK"  # OK / WARNING / ERROR

    def add_issue(level, message):
        nonlocal severity
        results.append({
            "level": level,
            "message": message
        })
        if level == "ERROR":
            severity = "ERROR"
        elif level == "WARNING" and severity != "ERROR":
            severity = "WARNING"

    # 1️⃣ 약 이름
    if prescription["name"] != medicine_bag["name"]:
        add_issue(
            "ERROR",
            f"약 이름 불일치: 처방전({prescription['name']}) / 약봉투({medicine_bag['name']})"
        )

    # 2️⃣ 1회 투약량
    if prescription["dose"] != medicine_bag["dose"]:
        add_issue(
            "ERROR",
            f"1회 투약량 불일치: 처방전({prescription['dose']}) / 약봉투({medicine_bag['dose']})"
        )

    # 3️⃣ 하루 복용 횟수
    if prescription["frequency"] != medicine_bag["frequency"]:
        add_issue(
            "WARNING",
            f"1일 복용 횟수 다름: 처방전({prescription['frequency']}회) / 약봉투({medicine_bag['frequency']}회)"
        )

    # 4️⃣ 복용 시간대
    if set(prescription["timing"]) != set(medicine_bag["timing"]):
        add_issue(
            "WARNING",
            f"복용 시간대 차이: 처방전({prescription['timing']}) / 약봉투({medicine_bag['timing']})"
        )

    # 5️⃣ 식전/식후
    if prescription.get("meal_relation") != medicine_bag.get("meal_relation"):
        add_issue(
            "WARNING",
            f"복용 시점 차이: 처방전({prescription.get('meal_relation')}) / 약봉투({medicine_bag.get('meal_relation')})"
        )

    # 6️⃣ 복용 기간
    if prescription["days"] != medicine_bag["days"]:
        add_issue(
            "WARNING",
            f"복용 기간 차이: 처방전({prescription['days']}일) / 약봉투({medicine_bag['days']}일)"
        )

    return {
        "status": severity,
        "issues": results
    }
