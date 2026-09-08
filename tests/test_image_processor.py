from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np

from app.image_processor import process_multiple_images, process_single_image
from app.models import OCRRawResult, PhotoStatus


def test_one_photo_can_be_processed(tmp_path: Path) -> None:
    image_path = _write_sample_image(tmp_path / "foto1.png")

    result = process_single_image(
        image_path=image_path,
        crop_selector=_return_input_crop,
        ocr_reader=_successful_ocr_reader("394.12\n397.68\n395.05"),
    )

    assert result.status == PhotoStatus.SUCCESS
    assert result.final_values == ["394.12", "397.68", "395.05"]
    assert result.image_path == str(image_path)


def test_two_or_more_photos_can_be_processed(tmp_path: Path) -> None:
    image_paths = [
        _write_sample_image(tmp_path / "foto1.png"),
        _write_sample_image(tmp_path / "foto2.png"),
    ]
    ocr_reader = _sequence_ocr_reader(
        [
            "394.12\n397.68\n395.05",
            "227.17\n228.50\n229.52",
        ],
    )

    results = process_multiple_images(
        image_paths=image_paths,
        crop_selector=_return_input_crop,
        ocr_reader=ocr_reader,
    )

    assert [result.status for result in results] == [
        PhotoStatus.SUCCESS,
        PhotoStatus.SUCCESS,
    ]
    assert results[0].final_values == ["394.12", "397.68", "395.05"]
    assert results[1].final_values == ["227.17", "228.50", "229.52"]


def test_one_photo_failure_does_not_stop_next_photo(tmp_path: Path) -> None:
    image_paths = [
        _write_sample_image(tmp_path / "foto1.png"),
        _write_sample_image(tmp_path / "foto2.png"),
        _write_sample_image(tmp_path / "foto3.png"),
    ]
    ocr_reader = _sequence_ocr_reader(
        [
            "394.12\n397.68\n395.05",
            "not readable",
            "227.17\n228.50\n229.52",
        ],
    )

    results = process_multiple_images(
        image_paths=image_paths,
        crop_selector=_return_input_crop,
        ocr_reader=ocr_reader,
    )

    assert [result.status for result in results] == [
        PhotoStatus.SUCCESS,
        PhotoStatus.FAILED,
        PhotoStatus.SUCCESS,
    ]
    assert results[2].final_values == ["227.17", "228.50", "229.52"]


def test_photo_results_are_not_swapped(tmp_path: Path) -> None:
    image_paths = [
        _write_sample_image(tmp_path / "foto_u.png"),
        _write_sample_image(tmp_path / "foto_v.png"),
    ]
    ocr_reader = _sequence_ocr_reader(
        [
            "394.12\n397.68\n395.05",
            "227.17\n228.50\n229.52",
        ],
    )

    results = process_multiple_images(
        image_paths=image_paths,
        crop_selector=_return_input_crop,
        ocr_reader=ocr_reader,
    )

    assert results[0].image_path == str(image_paths[0])
    assert results[0].final_values == ["394.12", "397.68", "395.05"]
    assert results[1].image_path == str(image_paths[1])
    assert results[1].final_values == ["227.17", "228.50", "229.52"]


def _write_sample_image(path: Path) -> Path:
    image = np.full((20, 30, 3), 255, dtype=np.uint8)
    cv2.imwrite(str(path), image)
    return path


def _return_input_crop(image):
    return image


def _successful_ocr_reader(raw_text: str):
    def read_text(_image) -> OCRRawResult:
        return OCRRawResult(raw_result=None, raw_text=raw_text, confidence=0.99)

    return read_text


def _sequence_ocr_reader(raw_texts: list[str]):
    iterator: Iterator[str] = iter(raw_texts)

    def read_text(_image) -> OCRRawResult:
        return OCRRawResult(
            raw_result=None,
            raw_text=next(iterator),
            confidence=0.99,
        )

    return read_text
