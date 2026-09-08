from dataclasses import dataclass


@dataclass(frozen=True)
class PreprocessingConfig:
    median_kernel_size: int = 3
    resize_scale: float = 2.0


DEFAULT_PREPROCESSING_CONFIG = PreprocessingConfig()
