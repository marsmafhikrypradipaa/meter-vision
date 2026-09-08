import numpy as np

from app.ocr_engine import _prepare_image_for_paddleocr


def test_prepare_image_for_paddleocr_keeps_path_input() -> None:
    assert _prepare_image_for_paddleocr("image.png") == "image.png"


def test_prepare_image_for_paddleocr_converts_grayscale_to_bgr() -> None:
    grayscale_image = np.zeros((10, 20), dtype=np.uint8)

    prepared_image = _prepare_image_for_paddleocr(grayscale_image)

    assert prepared_image.shape == (10, 20, 3)
    assert prepared_image.dtype == np.uint8


def test_prepare_image_for_paddleocr_keeps_bgr_image() -> None:
    bgr_image = np.zeros((10, 20, 3), dtype=np.uint8)

    prepared_image = _prepare_image_for_paddleocr(bgr_image)

    assert prepared_image.shape == (10, 20, 3)
