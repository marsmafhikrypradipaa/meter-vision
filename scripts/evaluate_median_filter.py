from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import DEFAULT_PREPROCESSING_CONFIG
from app.cropper import CropRectangle, crop_image
from app.denoise import apply_median_filter
from app.grayscale import to_grayscale
from app.image_loader import load_image
from app.resize import resize_by_scale


DEFAULT_CROPS: dict[str, CropRectangle] = {
    "v01.jpg": CropRectangle(x=300, y=455, width=165, height=165),
    "up1.jpg": CropRectangle(x=300, y=570, width=190, height=190),
}

OUTPUT_DIR = Path("output/evaluation")


def build_evaluation_images(image: MatLike, rectangle: CropRectangle) -> dict[str, MatLike]:
    original_crop = crop_image(image, rectangle)
    grayscale = to_grayscale(original_crop)
    median = apply_median_filter(
        grayscale,
        kernel_size=DEFAULT_PREPROCESSING_CONFIG.median_kernel_size,
    )
    resized = resize_by_scale(
        median,
        scale=DEFAULT_PREPROCESSING_CONFIG.resize_scale,
    )

    return {
        "A_original_crop": original_crop,
        "B_grayscale": grayscale,
        "C_grayscale_median_k3": median,
        "D_grayscale_median_k3_resize": resized,
    }


def build_threshold_experiment(image: MatLike) -> MatLike:
    _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresholded


def save_evaluation_images(
    source_path: Path,
    images: dict[str, MatLike],
    include_threshold: bool,
) -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    for suffix, image in images.items():
        output_path = OUTPUT_DIR / f"{source_path.stem}_{suffix}.png"
        _write_image(output_path, image)
        saved_paths.append(output_path)

    if include_threshold:
        thresholded = build_threshold_experiment(images["C_grayscale_median_k3"])
        output_path = OUTPUT_DIR / f"{source_path.stem}_E_threshold_otsu_experiment.png"
        _write_image(output_path, thresholded)
        images["E_threshold_otsu_experiment"] = thresholded
        saved_paths.append(output_path)

    comparison = build_comparison_grid(images)
    comparison_path = OUTPUT_DIR / f"{source_path.stem}_comparison.png"
    _write_image(comparison_path, comparison)
    saved_paths.append(comparison_path)

    return saved_paths


def build_comparison_grid(images: dict[str, MatLike]) -> MatLike:
    panels = [_prepare_panel(label, image) for label, image in images.items()]
    target_height = max(panel.shape[0] for panel in panels)
    normalized = [_pad_to_height(panel, target_height) for panel in panels]
    return cv2.hconcat(normalized)


def parse_crop(value: str) -> CropRectangle:
    parts = [int(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("Crop must use format x,y,width,height")

    return CropRectangle(x=parts[0], y=parts[1], width=parts[2], height=parts[3])


def _prepare_panel(label: str, image: MatLike) -> MatLike:
    if len(image.shape) == 2:
        panel = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        panel = image.copy()

    max_width = 360
    if panel.shape[1] > max_width:
        scale = max_width / panel.shape[1]
        panel = cv2.resize(
            panel,
            (max_width, max(1, int(panel.shape[0] * scale))),
            interpolation=cv2.INTER_AREA,
        )

    label_height = 38
    label_bar = np.full((label_height, panel.shape[1], 3), 245, dtype=np.uint8)
    cv2.putText(
        label_bar,
        label,
        (8, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (30, 30, 30),
        1,
        cv2.LINE_AA,
    )
    return cv2.vconcat([label_bar, panel])


def _pad_to_height(image: MatLike, target_height: int) -> MatLike:
    missing_height = target_height - image.shape[0]
    if missing_height <= 0:
        return image

    padding = np.full((missing_height, image.shape[1], 3), 255, dtype=np.uint8)
    return cv2.vconcat([image, padding])


def _write_image(path: Path, image: MatLike) -> None:
    success = cv2.imwrite(str(path), image)
    if not success:
        raise ValueError(f"Failed to write image: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate PM5100 median filter preprocessing visually.",
    )
    parser.add_argument("image_paths", nargs="+", type=Path)
    parser.add_argument(
        "--crop",
        type=parse_crop,
        help="Crop rectangle as x,y,width,height. Uses sample defaults when omitted.",
    )
    parser.add_argument(
        "--threshold",
        action="store_true",
        help="Also save Otsu threshold as a separate experiment.",
    )
    args = parser.parse_args()

    for image_path in args.image_paths:
        rectangle = args.crop or DEFAULT_CROPS.get(image_path.name)
        if rectangle is None:
            raise ValueError(
                f"No default crop for {image_path}. Pass --crop x,y,width,height.",
            )

        image = load_image(image_path)
        evaluation_images = build_evaluation_images(image, rectangle)
        saved_paths = save_evaluation_images(
            source_path=image_path,
            images=evaluation_images,
            include_threshold=args.threshold,
        )

        print(f"{image_path}:")
        print(f"  crop: x={rectangle.x}, y={rectangle.y}, w={rectangle.width}, h={rectangle.height}")
        for saved_path in saved_paths:
            print(f"  {saved_path}")


if __name__ == "__main__":
    main()
