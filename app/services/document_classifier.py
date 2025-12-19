def detect_document_type(text: str) -> str:
    keywords_prescription = [
        "처방전", "Rx", "의사", "병원", "진료과", "처방일"
    ]

    keywords_bag = [
        "식후", "식전", "복용", "아침", "저녁", "취침"
    ]

    for k in keywords_prescription:
        if k in text:
            return "prescription"

    for k in keywords_bag:
        if k in text:
            return "medicine_bag"

    return "unknown"
