import cv2
from cv2.typing import MatLike


def resize_by_scale(image: MatLike, scale: float) -> MatLike:
    if image is None or image.size == 0:
        raise ValueError("Cannot resize an empty image")

    if scale <= 0:
        raise ValueError("Resize scale must be greater than zero")

    height, width = image.shape[:2]
    target_width = max(1, int(width * scale))
    target_height = max(1, int(height * scale))

    interpolation = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
    return cv2.resize(image, (target_width, target_height), interpolation=interpolation)
