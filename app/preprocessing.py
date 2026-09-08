from cv2.typing import MatLike

from app.config import DEFAULT_PREPROCESSING_CONFIG, PreprocessingConfig
from app.denoise import apply_median_filter
from app.grayscale import to_grayscale
from app.resize import resize_by_scale


def preprocess_for_pm5100_numbers(
    image: MatLike,
    config: PreprocessingConfig = DEFAULT_PREPROCESSING_CONFIG,
) -> MatLike:
    grayscale_image = to_grayscale(image)
    denoised_image = apply_median_filter(
        grayscale_image,
        kernel_size=config.median_kernel_size,
    )
    return resize_by_scale(denoised_image, scale=config.resize_scale)
