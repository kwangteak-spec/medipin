import pytesseract
from pytesseract import Output
from PIL import Image, ImageFilter, ImageOps


def calculate_ocr_confidence(image: Image.Image) -> dict:
    """
    OCR 결과 신뢰도 계산
    """

    data = pytesseract.image_to_data(
        image,
        lang="kor+eng",
        output_type=Output.DICT
    )

    confidences = []

    for conf in data["conf"]:
        try:
            conf = int(conf)
            if conf >= 0:
                confidences.append(conf)
        except:
            pass

    if not confidences:
        avg_conf = 0
    else:
        avg_conf = sum(confidences) / len(confidences)

    # 🔍 등급 분류
    if avg_conf >= 80:
        level = "HIGH"
        message = "인식 정확도가 높습니다."
    elif avg_conf >= 60:
        level = "MEDIUM"
        message = "인식 정확도가 보통입니다. 복용 전 확인이 필요합니다."
    else:
        level = "LOW"
        message = "인식 정확도가 낮습니다. 반드시 직접 확인하세요."

    return {
        "score": round(avg_conf),
        "level": level,
        "message": message
    }
