from dataclasses import dataclass
from typing import Sequence

from app.models import PhotoProcessingResult


@dataclass(frozen=True)
class BatchReportMetadata:
    date: str
    time: str
    name: str


@dataclass(frozen=True)
class PhotoReportMetadata:
    room: str
    lcd_type: str


@dataclass(frozen=True)
class PhotoReportEntry:
    metadata: PhotoReportMetadata
    result: PhotoProcessingResult


def generate_text_report(
    metadata: BatchReportMetadata,
    entries: Sequence[PhotoReportEntry],
) -> str:
    lines = [
        "LAPORAN PEMBACAAN METER",
        "",
        f"Tanggal : {metadata.date}",
        f"Waktu   : {metadata.time}",
        f"Nama    : {metadata.name}",
        "",
    ]

    for index, entry in enumerate(entries, start=1):
        lcd_type = _normalize_lcd_type(entry.metadata.lcd_type)
        unit = _unit_for_lcd_type(lcd_type)
        labels = _labels_for_lcd_type(lcd_type)
        value_1, value_2, value_3 = _normalize_photo_values(entry.result.final_values)
        lines.extend(
            [
                f"Foto {index}",
                f"Ruangan   : {entry.metadata.room}",
                f"Jenis LCD : {lcd_type}",
                "",
                "Hasil Pembacaan:",
                f"{labels[0]} : {value_1} {unit}",
                f"{labels[1]} : {value_2} {unit}",
                f"{labels[2]} : {value_3} {unit}",
                "",
            ],
        )

    return "\n".join(lines).rstrip()


def _normalize_lcd_type(lcd_type: str) -> str:
    normalized = lcd_type.strip().upper()
    if normalized not in {"V", "I", "U"}:
        raise ValueError("LCD type must be one of: V, I, U")
    return normalized


def _unit_for_lcd_type(lcd_type: str) -> str:
    if lcd_type == "I":
        return "A"
    return "V"


def _labels_for_lcd_type(lcd_type: str) -> tuple[str, str, str]:
    if lcd_type == "U":
        return "U12", "U23", "U31"
    return f"{lcd_type}1", f"{lcd_type}2", f"{lcd_type}3"


def _normalize_photo_values(values: Sequence[str]) -> tuple[str, str, str]:
    normalized_values = [value.strip() for value in values if value.strip()]
    while len(normalized_values) < 3:
        normalized_values.append("-")
    return normalized_values[0], normalized_values[1], normalized_values[2]
