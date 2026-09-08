from collections.abc import Callable
from pathlib import Path

from cv2.typing import MatLike

from app.config import DEFAULT_PREPROCESSING_CONFIG, PreprocessingConfig
from app.image_loader import load_image
from app.models import OCRRawResult, OCRStatus, PhotoProcessingResult, PhotoStatus
from app.parser import parse_voltage_values
from app.preprocessing import preprocess_for_pm5100_numbers


CropSelector = Callable[[MatLike], MatLike | None]
OCRReader = Callable[[MatLike], OCRRawResult]


def process_single_image(
    image_path: str | Path,
    crop_selector: CropSelector,
    ocr_reader: OCRReader,
    config: PreprocessingConfig = DEFAULT_PREPROCESSING_CONFIG,
) -> PhotoProcessingResult:
    path = Path(image_path)

    try:
        image = load_image(path)
        cropped_image = crop_selector(image)
        if cropped_image is None or cropped_image.size == 0:
            return _failed_result(path, "Crop was cancelled or empty")

        preprocessed_image = preprocess_for_pm5100_numbers(cropped_image, config=config)
        raw_result = ocr_reader(preprocessed_image)
        ocr_result = parse_voltage_values(
            raw_result.raw_text,
            confidence=raw_result.confidence,
        )

        if ocr_result.status != OCRStatus.SUCCESS:
            return PhotoProcessingResult(
                image_path=str(path),
                ocr_result=ocr_result,
                final_values=[],
                status=PhotoStatus.FAILED,
                error_message="OCR parser did not find 3 voltage values",
            )

        return PhotoProcessingResult(
            image_path=str(path),
            ocr_result=ocr_result,
            final_values=ocr_result.values,
            status=PhotoStatus.SUCCESS,
        )
    except Exception as error:
        return _failed_result(path, str(error))


def process_multiple_images(
    image_paths: list[str | Path],
    crop_selector: CropSelector,
    ocr_reader: OCRReader,
    config: PreprocessingConfig = DEFAULT_PREPROCESSING_CONFIG,
) -> list[PhotoProcessingResult]:
    return [
        process_single_image(
            image_path=image_path,
            crop_selector=crop_selector,
            ocr_reader=ocr_reader,
            config=config,
        )
        for image_path in image_paths
    ]


def with_manual_correction(
    result: PhotoProcessingResult,
    corrected_values: list[str],
) -> PhotoProcessingResult:
    return PhotoProcessingResult(
        image_path=result.image_path,
        ocr_result=result.ocr_result,
        final_values=corrected_values,
        status=PhotoStatus.CORRECTED,
        error_message=result.error_message,
    )


def _failed_result(path: Path, error_message: str) -> PhotoProcessingResult:
    return PhotoProcessingResult(
        image_path=str(path),
        ocr_result=None,
        final_values=[],
        status=PhotoStatus.FAILED,
        error_message=error_message,
    )
