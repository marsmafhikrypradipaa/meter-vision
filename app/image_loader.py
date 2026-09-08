from pathlib import Path

import cv2
from cv2.typing import MatLike


def load_image(image_path: str | Path) -> MatLike:
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image file: {path}")

    return image
