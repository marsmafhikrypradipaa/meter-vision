from collections.abc import Iterable
from typing import Any

import cv2
from cv2.typing import MatLike

from app.models import OCRRawResult


class PaddleOCREngine:
    def __init__(self, language: str = "en") -> None:
        from paddleocr import PaddleOCR

        self._ocr = PaddleOCR(
            lang=language,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def read_text(self, image: str | MatLike) -> OCRRawResult:
        raw_result = self._ocr.predict(_prepare_image_for_paddleocr(image))
        texts = _extract_rec_texts(raw_result)
        scores = _extract_rec_scores(raw_result)

        return OCRRawResult(
            raw_result=raw_result,
            raw_text="\n".join(texts),
            confidence=_average(scores),
        )


def _prepare_image_for_paddleocr(image: str | MatLike) -> str | MatLike:
    if isinstance(image, str):
        return image

    if image is None or image.size == 0:
        raise ValueError("Cannot run OCR on an empty image")

    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return image


def _extract_rec_texts(raw_result: Any) -> list[str]:
    texts: list[str] = []
    for item in _iter_result_items(raw_result):
        if isinstance(item, dict) and "rec_texts" in item:
            texts.extend(str(text) for text in item["rec_texts"])
    return texts


def _extract_rec_scores(raw_result: Any) -> list[float]:
    scores: list[float] = []
    for item in _iter_result_items(raw_result):
        if isinstance(item, dict) and "rec_scores" in item:
            scores.extend(float(score) for score in item["rec_scores"])
    return scores


def _iter_result_items(raw_result: Any) -> Iterable[Any]:
    if raw_result is None:
        return []

    if isinstance(raw_result, list):
        return raw_result

    return [raw_result]


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)
