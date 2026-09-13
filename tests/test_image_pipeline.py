from pathlib import Path

import cv2
import numpy as np
import pytest

from app.cropper import (
    CROP_CANCEL,
    CROP_CONFIRM,
    CROP_RECROP,
    CropRectangle,
    _build_display_image,
    _crop_confirmation_from_key,
    _to_original_rectangle,
    crop_image,
    select_crop_manually,
)
from app.denoise import apply_median_filter
from app.grayscale import to_grayscale
from app.image_loader import load_image
from app.resize import resize_by_scale


def test_image_successfully_loaded(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.full((20, 30, 3), 255, dtype=np.uint8)
    cv2.imwrite(str(image_path), image)

    loaded_image = load_image(image_path)

    assert loaded_image.shape == (20, 30, 3)
    assert loaded_image.dtype == np.uint8


def test_crop_returns_valid_image() -> None:
    image = np.zeros((50, 80, 3), dtype=np.uint8)
    rectangle = CropRectangle(x=10, y=5, width=30, height=20)

    cropped_image = crop_image(image, rectangle)

    assert cropped_image.shape == (20, 30, 3)
    assert cropped_image.size > 0


def test_crop_rejects_invalid_rectangle() -> None:
    image = np.zeros((50, 80, 3), dtype=np.uint8)
    rectangle = CropRectangle(x=70, y=5, width=30, height=20)

    with pytest.raises(ValueError, match="exceeds image width"):
        crop_image(image, rectangle)


def test_large_image_is_scaled_for_display() -> None:
    image = np.zeros((3000, 4000, 3), dtype=np.uint8)

    display_image, scale = _build_display_image(
        image=image,
        screen_width=1920,
        screen_height=1080,
    )

    assert scale < 1.0
    assert display_image.shape[1] <= int(1920 * 0.9)
    assert display_image.shape[0] <= int(1080 * 0.9)


def test_display_selection_is_mapped_back_to_original_coordinates() -> None:
    rectangle = _to_original_rectangle(
        selected=(100, 50, 200, 100),
        scale=0.5,
        image_width=4000,
        image_height=3000,
    )

    assert rectangle is not None
    assert rectangle.x == 200
    assert rectangle.y == 100
    assert rectangle.width == 400
    assert rectangle.height == 200


def test_crop_preview_key_mapping() -> None:
    assert _crop_confirmation_from_key(13) == CROP_CONFIRM
    assert _crop_confirmation_from_key(32) == CROP_CONFIRM
    assert _crop_confirmation_from_key(ord("r")) == CROP_RECROP
    assert _crop_confirmation_from_key(ord("R")) == CROP_RECROP
    assert _crop_confirmation_from_key(ord("c")) == CROP_CANCEL
    assert _crop_confirmation_from_key(27) == CROP_CANCEL
    assert _crop_confirmation_from_key(ord("x")) is None


def test_manual_crop_can_be_repeated_before_confirm(monkeypatch) -> None:
    image = np.zeros((50, 80, 3), dtype=np.uint8)
    selections = iter([(0, 0, 10, 10), (10, 5, 30, 20)])
    actions = iter([CROP_RECROP, CROP_CONFIRM])

    monkeypatch.setattr("app.cropper._get_screen_resolution", lambda: (800, 600))
    monkeypatch.setattr(cv2, "selectROI", lambda *_args, **_kwargs: next(selections))
    monkeypatch.setattr(cv2, "destroyWindow", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        "app.cropper._confirm_crop_selection",
        lambda **_kwargs: next(actions),
    )

    cropped_image = select_crop_manually("crop test", image)

    assert cropped_image is not None
    assert cropped_image.shape == (20, 30, 3)


def test_grayscale_returns_valid_image() -> None:
    image = np.zeros((50, 80, 3), dtype=np.uint8)

    grayscale_image = to_grayscale(image)

    assert grayscale_image.shape == (50, 80)
    assert grayscale_image.dtype == np.uint8


def test_median_filter_returns_valid_image() -> None:
    image = np.zeros((50, 80), dtype=np.uint8)
    image[10, 10] = 255

    denoised_image = apply_median_filter(image, kernel_size=3)

    assert denoised_image.shape == image.shape
    assert denoised_image.dtype == np.uint8


def test_resize_returns_valid_image() -> None:
    image = np.zeros((50, 80), dtype=np.uint8)

    resized_image = resize_by_scale(image, scale=2.0)

    assert resized_image.shape == (100, 160)
    assert resized_image.dtype == np.uint8
