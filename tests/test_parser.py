from app.models import OCRStatus
from app.parser import parse_voltage_values


def test_parse_u12_voltage_keeps_decimal_point() -> None:
    result = parse_voltage_values("U12 394.12 V")

    assert result.values == ["394.12"]
    assert result.status == OCRStatus.FAILED


def test_parse_u23_voltage_keeps_decimal_point() -> None:
    result = parse_voltage_values("U23 397.68 V")

    assert result.values == ["397.68"]
    assert result.status == OCRStatus.FAILED


def test_parse_u31_voltage_keeps_decimal_point() -> None:
    result = parse_voltage_values("U31 395.05 V")

    assert result.values == ["395.05"]
    assert result.status == OCRStatus.FAILED


def test_parse_three_u_mode_values_success() -> None:
    result = parse_voltage_values("U12 394.12 V\nU23 397.68 V\nU31 395.05 V")

    assert result.values == ["394.12", "397.68", "395.05"]
    assert result.status == OCRStatus.SUCCESS


def test_parse_three_v_mode_values_success() -> None:
    result = parse_voltage_values("V1 227.17 V\nV2 228.50 V\nV3 229.52 V")

    assert result.values == ["227.17", "228.50", "229.52"]
    assert result.status == OCRStatus.SUCCESS


def test_parse_three_i_mode_values_success() -> None:
    result = parse_voltage_values("I1 10.25 A\nI2 10.11 A\nI3 9.98 A")

    assert result.values == ["10.25", "10.11", "9.98"]
    assert result.status == OCRStatus.SUCCESS


def test_parse_repairs_missing_decimal_point_for_five_digit_voltage() -> None:
    result = parse_voltage_values("394.12\n397.68\n39505")

    assert result.values == ["394.12", "397.68", "395.05"]
    assert result.status == OCRStatus.SUCCESS
