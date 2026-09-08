import cv2
from cv2.typing import MatLike


def apply_median_filter(image: MatLike, kernel_size: int) -> MatLike:
    if image is None or image.size == 0:
        raise ValueError("Cannot denoise an empty image")

    if kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("Median filter kernel size must be an odd number >= 3")

    return cv2.medianBlur(image, kernel_size)
