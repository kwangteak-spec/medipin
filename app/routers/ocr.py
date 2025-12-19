from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pytesseract
from PIL import Image, ImageFilter, ImageOps
import shutil
import os
from uuid import uuid4
from datetime import date
from io import BytesIO
import logging
import time

# -------------------------------------------------
# ✅ Logging 설정
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ocr")

# -------------------------------------------------
# ✅ 서비스 모듈들
# -------------------------------------------------
from app.services.document_classifier import detect_document_type
from app.services.prescription_parser import parse_prescription_text
from app.services.ocr_parser import parse_medication_text
from app.services.schedule_builder import build_schedule_from_ocr
from app.services.calendar_builder import build_calendar_events
from app.services.ocr_confidence import calculate_ocr_confidence
from app.services.medication_normalizer import normalize_medications
from app.services.prescription_comparator import compare_prescription_and_bag
from app.services.alert_level import determine_alert_level
from app.services.ocr_cache import (
    make_file_hash,
    get_cached_result,
    set_cached_result,
)

# -------------------------------------------------
# ✅ 설정값
# -------------------------------------------------
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ocr_router = APIRouter(prefix="/ocr", tags=["OCR Processing"])


# -------------------------------------------------
# ✅ 공통 응답 포맷
# -------------------------------------------------
def build_response(
    data: dict | None = None,
    message: str = "OK",
    code: str = "OK",
    alert: dict | None = None,
    success: bool = True,
):
    if alert is None:
        alert = {"level": "NORMAL", "reason": None}

    return {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
        "alert": alert,
    }


# -------------------------------------------------
# ✅ 공통 OCR 처리 함수
# -------------------------------------------------
def process_image(file_path: str):
    img = Image.open(file_path)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)

    text = pytesseract.image_to_string(img, lang="kor+eng")
    return text, img


# -------------------------------------------------
# ✅ 단일 문서 OCR
# -------------------------------------------------
@ocr_router.post("/read")
async def read_text(file: UploadFile = File(...)):
    start_time = time.time()
    logger.info(f"[OCR START] filename={file.filename}")

    # 1) 확장자 체크
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        logger.warning(f"[INVALID FILE] filename={file.filename}")
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    # 2) 파일 전체 바이트 읽기
    contents = await file.read()

    # 2-1) 파일 크기 제한
    if len(contents) > MAX_FILE_SIZE:
        logger.warning(f"[FILE TOO LARGE] filename={file.filename}, size={len(contents)}")
        raise HTTPException(status_code=413, detail="파일 크기는 최대 5MB까지 가능합니다.")

    # 2-2) 해시 생성 (여기서 file_hash 정의‼️)
    file_hash = make_file_hash(contents)

    # 2-3) 캐시 조회
    cached = get_cached_result(file_hash)
    if cached:
        elapsed = time.time() - start_time
        logger.info(
            f"[OCR CACHE HIT] filename={file.filename}, elapsed={elapsed:.3f}s"
        )
        return build_response(
            message="캐시된 OCR 결과 반환",
            data=cached["data"],
            alert=cached["alert"],
        )

    # 캐시가 없으면, BytesIO로 다시 감싸서 실제 OCR 수행
    file.file = BytesIO(contents)

    temp_path = f"temp_{uuid4().hex}.png"

    try:
        # 3) 임시 파일로 저장
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4) OCR 실행
        extracted_text, image = process_image(temp_path)

        if not extracted_text or len(extracted_text.strip()) < 10:
            logger.warning(f"[OCR EMPTY] filename={file.filename}")
            return build_response(
                success=False,
                code="OCR_EMPTY",
                message="텍스트 인식에 실패했습니다. 다시 촬영해 주세요.",
                data={"filename": file.filename},
                alert={"level": "WARNING", "reason": "OCR 결과 부족"},
            )

        # 5) OCR 신뢰도 / 문서 타입 / alert 레벨
        confidence = calculate_ocr_confidence(image)
        doc_type = detect_document_type(extracted_text)
        alert = determine_alert_level(confidence)

        start_date = date.today()
        days = 3

        # -------------------------------------------------
        # ✅ 약봉투
        # -------------------------------------------------
        if doc_type == "medicine_bag":
            parsed = parse_medication_text(extracted_text)
            schedule = build_schedule_from_ocr(parsed)
            calendar_events = build_calendar_events(
                schedules=schedule,
                start_date=start_date,
                days=days,
                alert_level=alert,
            )

            response_data = {
                "type": "medicine_bag",
                "confidence": confidence,
                "parsed_medication": parsed,
                "schedule": schedule,
                "calendar_events": calendar_events,
            }

            # ✅ 캐시에 저장
            set_cached_result(
                file_hash,
                {
                    "data": response_data,
                    "alert": alert,
                },
            )

            elapsed = time.time() - start_time
            logger.info(
                f"[OCR DONE] type=medicine_bag filename={file.filename} elapsed={elapsed:.3f}s"
            )

            return build_response(
                message="약봉투 OCR 분석 성공",
                data=response_data,
                alert=alert,
            )

        # -------------------------------------------------
        # ✅ 처방전
        # -------------------------------------------------
        elif doc_type == "prescription":
            parsed = parse_prescription_text(extracted_text)

            response_data = {
                "type": "prescription",
                "confidence": confidence,
                "parsed_prescription": parsed,
            }

            # ✅ 처방전도 캐시에 저장 가능 (원하면)
            set_cached_result(
                file_hash,
                {
                    "data": response_data,
                    "alert": alert,
                },
            )

            elapsed = time.time() - start_time
            logger.info(
                f"[OCR DONE] type=prescription filename={file.filename} elapsed={elapsed:.3f}s"
            )

            return build_response(
                message="처방전 OCR 분석 성공",
                data=response_data,
                alert=alert,
            )

        # -------------------------------------------------
        # ✅ 알 수 없음
        # -------------------------------------------------
        elapsed = time.time() - start_time
        logger.info(
            f"[OCR UNKNOWN] filename={file.filename} elapsed={elapsed:.3f}s"
        )

        response_data = {
            "confidence": confidence,
            "raw_text": extracted_text,
        }

        return build_response(
            success=False,
            code="UNKNOWN_DOCUMENT",
            message="문서 유형을 인식하지 못했습니다.",
            data=response_data,
            alert=alert,
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -------------------------------------------------
# ✅ 처방전 + 약봉투 비교
# -------------------------------------------------
@ocr_router.post("/compare")
async def compare_documents(files: List[UploadFile] = File(...)):
    if len(files) != 2:
        return build_response(
            success=False,
            code="INVALID_FILE_COUNT",
            message="이미지 2개(처방전 + 약봉투)를 업로드해야 합니다.",
            alert={"level": "WARNING", "reason": "입력 부족"},
        )

    parsed_rx = None
    parsed_bag = None
    confidence_bag = None

    for file in files:
        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"{file.filename} 크기(5MB) 초과",
            )

        file.file = BytesIO(contents)
        temp_path = f"temp_{uuid4().hex}.png"

        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            extracted_text, image = process_image(temp_path)
            doc_type = detect_document_type(extracted_text)

            if doc_type == "prescription":
                parsed_rx = parse_prescription_text(extracted_text)
            elif doc_type == "medicine_bag":
                parsed_bag = parse_medication_text(extracted_text)
                confidence_bag = calculate_ocr_confidence(image)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    if not parsed_rx or not parsed_bag:
        return build_response(
            success=False,
            code="MISSING_DOCUMENT",
            message="처방전과 약봉투가 모두 필요합니다.",
            alert={"level": "WARNING", "reason": "비교 불가"},
        )

    normalized_rx = normalize_medications(parsed_rx)
    normalized_bag = normalize_medications(parsed_bag)

    comparison = compare_prescription_and_bag(
        prescription={"medicines": normalized_rx},
        medicine_bag={"medicines": normalized_bag},
    )

    alert = determine_alert_level(confidence_bag, comparison)

    result = {
        "comparison": comparison,
        "prescription": normalized_rx,
        "medicine_bag": normalized_bag,
    }

    if comparison["is_safe"]:
        start_date = date.today()
        days = 3

        schedule = build_schedule_from_ocr(parsed_bag)
        calendar_events = build_calendar_events(
            schedules=schedule,
            start_date=start_date,
            days=days,
            alert_level=alert,
        )

        result["schedule"] = schedule
        result["calendar_events"] = calendar_events

    return build_response(
        message="처방전-약봉투 비교 완료",
        data=result,
        alert=alert,
    )
