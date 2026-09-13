from dataclasses import dataclass

import cv2
from cv2.typing import MatLike
from tkinter import Tk


MAX_DISPLAY_FRACTION = 0.9
PREVIEW_DISPLAY_FRACTION = 0.75
CROP_CONFIRM = "confirm"
CROP_RECROP = "recrop"
CROP_CANCEL = "cancel"


@dataclass(frozen=True)
class CropRectangle:
    x: int
    y: int
    width: int
    height: int


def crop_image(image: MatLike, rectangle: CropRectangle) -> MatLike:
    if image is None or image.size == 0:
        raise ValueError("Cannot crop an empty image")

    height, width = image.shape[:2]
    _validate_crop_rectangle(rectangle, image_width=width, image_height=height)

    x_end = rectangle.x + rectangle.width
    y_end = rectangle.y + rectangle.height
    return image[rectangle.y:y_end, rectangle.x:x_end].copy()


def select_crop_manually(window_name: str, image: MatLike) -> MatLike | None:
    if image is None or image.size == 0:
        raise ValueError("Cannot crop an empty image")

    image_height, image_width = image.shape[:2]
    screen_width, screen_height = _get_screen_resolution()
    display_image, scale = _build_display_image(
        image=image,
        screen_width=screen_width,
        screen_height=screen_height,
    )

    while True:
        selected = cv2.selectROI(
            window_name,
            display_image,
            showCrosshair=True,
            fromCenter=False,
        )
        cv2.destroyWindow(window_name)

        rectangle = _to_original_rectangle(
            selected=selected,
            scale=scale,
            image_width=image_width,
            image_height=image_height,
        )
        if rectangle is None:
            return None

        cropped_image = crop_image(image, rectangle)
        action = _confirm_crop_selection(
            window_name=f"{window_name} - preview crop",
            cropped_image=cropped_image,
            screen_width=screen_width,
            screen_height=screen_height,
        )
        if action == CROP_CONFIRM:
            return cropped_image
        if action == CROP_CANCEL:
            return None



def _get_screen_resolution() -> tuple[int, int]:
    root = Tk()
    root.withdraw()
    root.update_idletasks()
    try:
        return root.winfo_screenwidth(), root.winfo_screenheight()
    finally:
        root.destroy()


def _build_display_image(
    image: MatLike,
    screen_width: int,
    screen_height: int,
) -> tuple[MatLike, float]:
    image_height, image_width = image.shape[:2]
    max_width = max(1, int(screen_width * MAX_DISPLAY_FRACTION))
    max_height = max(1, int(screen_height * MAX_DISPLAY_FRACTION))

    scale = min(
        max_width / image_width,
        max_height / image_height,
        1.0,
    )
    if scale == 1.0:
        return image, 1.0

    resized = cv2.resize(
        image,
        dsize=None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale


def _confirm_crop_selection(
    window_name: str,
    cropped_image: MatLike,
    screen_width: int,
    screen_height: int,
) -> str:
    preview_image = _build_crop_preview_image(
        cropped_image=cropped_image,
        screen_width=screen_width,
        screen_height=screen_height,
    )
    cv2.imshow(window_name, preview_image)
    try:
        while True:
            action = _crop_confirmation_from_key(cv2.waitKey(0))
            if action is not None:
                return action
    finally:
        cv2.destroyWindow(window_name)


def _build_crop_preview_image(
    cropped_image: MatLike,
    screen_width: int,
    screen_height: int,
) -> MatLike:
    if len(cropped_image.shape) == 2:
        preview_source = cv2.cvtColor(cropped_image, cv2.COLOR_GRAY2BGR)
    else:
        preview_source = cropped_image

    preview_image, _scale = _build_display_image(
        image=preview_source,
        screen_width=int(screen_width * PREVIEW_DISPLAY_FRACTION),
        screen_height=int(screen_height * PREVIEW_DISPLAY_FRACTION),
    )
    instruction_height = 40
    instruction_bar = preview_image.copy()
    instruction_bar = cv2.copyMakeBorder(
        instruction_bar,
        instruction_height,
        0,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=(245, 245, 245),
    )
    cv2.putText(
        instruction_bar,
        "ENTER/SPACE: lanjut   R: crop ulang   C/ESC: batal",
        (10, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (30, 30, 30),
        1,
        cv2.LINE_AA,
    )
    return instruction_bar


def _crop_confirmation_from_key(key: int) -> str | None:
    normalized_key = key & 0xFF
    if normalized_key in {13, 32}:
        return CROP_CONFIRM
    if normalized_key in {ord("r"), ord("R")}:
        return CROP_RECROP
    if normalized_key in {27, ord("c"), ord("C")}:
        return CROP_CANCEL
    return None


def _to_original_rectangle(
    selected: tuple[int, int, int, int],
    scale: float,
    image_width: int,
    image_height: int,
) -> CropRectangle | None:
    x, y, width, height = (int(value) for value in selected)
    if width == 0 or height == 0:
        return None

    if scale <= 0:
        raise ValueError("Scale must be greater than zero")

    x_original = int(round(x / scale))
    y_original = int(round(y / scale))
    width_original = int(round(width / scale))
    height_original = int(round(height / scale))

    x_original = min(max(0, x_original), image_width - 1)
    y_original = min(max(0, y_original), image_height - 1)
    width_original = min(max(1, width_original), image_width - x_original)
    height_original = min(max(1, height_original), image_height - y_original)

    return CropRectangle(
        x=x_original,
        y=y_original,
        width=width_original,
        height=height_original,
    )


def _validate_crop_rectangle(
    rectangle: CropRectangle,
    image_width: int,
    image_height: int,
) -> None:
    if rectangle.width <= 0 or rectangle.height <= 0:
        raise ValueError("Crop rectangle width and height must be greater than zero")

    if rectangle.x < 0 or rectangle.y < 0:
        raise ValueError("Crop rectangle coordinates cannot be negative")

    if rectangle.x + rectangle.width > image_width:
        raise ValueError("Crop rectangle exceeds image width")

    if rectangle.y + rectangle.height > image_height:
        raise ValueError("Crop rectangle exceeds image height")
