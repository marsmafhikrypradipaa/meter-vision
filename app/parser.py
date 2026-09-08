import re

from app.models import OCRResult, OCRStatus


EXPECTED_VOLTAGE_COUNT = 3
METER_VALUE_MIN = 0.0
METER_VALUE_MAX = 9999.0
DECIMAL_PATTERN = re.compile(r"(?<!\d)(\d{1,4}[.,]\d{1,3})(?!\d)")
MISSING_DOT_PATTERN = re.compile(r"(?<!\d)(\d{5})(?!\d)")


def parse_voltage_values(raw_text: str, confidence: float | None = None) -> OCRResult:
    normalized_text = _normalize_text(raw_text)
    values = _extract_decimal_values(normalized_text)

    if len(values) < EXPECTED_VOLTAGE_COUNT:
        values.extend(_extract_missing_dot_values(normalized_text, existing_values=values))

    final_values = values[:EXPECTED_VOLTAGE_COUNT]
    status = (
        OCRStatus.SUCCESS
        if len(final_values) == EXPECTED_VOLTAGE_COUNT
        else OCRStatus.FAILED
    )

    return OCRResult(
        raw_text=raw_text,
        values=final_values,
        confidence=confidence,
        status=status,
    )


def _normalize_text(raw_text: str) -> str:
    return raw_text.replace(",", ".")


def _extract_decimal_values(text: str) -> list[str]:
    values: list[str] = []
    for match in DECIMAL_PATTERN.finditer(text):
        value = _format_decimal_value(match.group(1))
        if _is_valid_meter_value(value):
            values.append(value)
    return values


def _extract_missing_dot_values(text: str, existing_values: list[str]) -> list[str]:
    repaired_values: list[str] = []
    existing = set(existing_values)

    for match in MISSING_DOT_PATTERN.finditer(text):
        candidate = f"{match.group(1)[:3]}.{match.group(1)[3:]}"
        if _is_valid_meter_value(candidate) and candidate not in existing:
            repaired_values.append(candidate)
            existing.add(candidate)

    return repaired_values


def _format_decimal_value(value: str) -> str:
    number = float(value)
    return f"{number:.2f}"


def _is_valid_meter_value(value: str) -> bool:
    try:
        number = float(value)
    except ValueError:
        return False

    return METER_VALUE_MIN <= number <= METER_VALUE_MAX
