# app/services/ocr_cache.py
import hashlib
from typing import Dict, Any

_OCR_CACHE: Dict[str, Dict[str, Any]] = {}

def make_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def get_cached_result(file_hash: str):
    return _OCR_CACHE.get(file_hash)

def set_cached_result(file_hash: str, result: dict):
    _OCR_CACHE[file_hash] = result

def cache_size() -> int:
    return len(_OCR_CACHE)
