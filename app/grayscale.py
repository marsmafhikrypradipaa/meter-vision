import cv2
from cv2.typing import MatLike


def to_grayscale(image: MatLike) -> MatLike:
    if image is None or image.size == 0:
        raise ValueError("Cannot convert an empty image to grayscale")

    if len(image.shape) == 2:
        return image.copy()

    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    raise ValueError(f"Unsupported image shape for grayscale conversion: {image.shape}")
