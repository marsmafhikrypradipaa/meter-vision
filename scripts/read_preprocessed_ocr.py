from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.ocr_engine import PaddleOCREngine
from app.parser import parse_voltage_values


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run PaddleOCR on preprocessed PM5100 crop images.",
    )
    parser.add_argument("image_paths", nargs="+", type=Path)
    args = parser.parse_args()

    engine = PaddleOCREngine(language="en")
    for image_path in args.image_paths:
        raw_result = engine.read_text(str(image_path))
        parsed_result = parse_voltage_values(
            raw_result.raw_text,
            confidence=raw_result.confidence,
        )

        print(f"{image_path}:")
        print(f"  status: {parsed_result.status.value}")
        print(f"  confidence: {parsed_result.confidence}")
        print("  raw_text:")
        for line in parsed_result.raw_text.splitlines():
            print(f"    {line}")
        print(f"  values: {parsed_result.values}")


if __name__ == "__main__":
    main()
