import pytesseract
from PIL import Image

# Windows 환경 대비 (Tesseract 실행 경로 등록)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="kor+eng")  # 한국어+영어 OCR
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"
