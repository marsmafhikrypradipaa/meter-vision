from dataclasses import dataclass
from enum import Enum
from typing import Any


class OCRStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PhotoStatus(str, Enum):
    SUCCESS = "SUCCESS"
    CORRECTED = "CORRECTED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class OCRRawResult:
    raw_result: Any
    raw_text: str
    confidence: float | None


@dataclass(frozen=True)
class OCRResult:
    raw_text: str
    values: list[str]
    confidence: float | None
    status: OCRStatus


@dataclass(frozen=True)
class PhotoProcessingResult:
    image_path: str
    ocr_result: OCRResult | None
    final_values: list[str]
    status: PhotoStatus
    error_message: str | None = None
