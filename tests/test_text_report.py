import pytest

from app.models import OCRResult, OCRStatus, PhotoProcessingResult, PhotoStatus
from app.report.text_report import (
    BatchReportMetadata,
    PhotoReportEntry,
    PhotoReportMetadata,
    generate_text_report,
)


def test_generate_text_report_uses_metadata_per_photo() -> None:
    metadata = BatchReportMetadata(
        date="11 Agustus 2026",
        time="10:30:15",
        name="Budi",
    )
    entries = [
        PhotoReportEntry(
            metadata=PhotoReportMetadata(room="Room A", lcd_type="V"),
            result=PhotoProcessingResult(
                image_path="foto1.jpg",
                ocr_result=_ocr_result(["220.50"], 0.94),
                final_values=["220.50"],
                status=PhotoStatus.SUCCESS,
            ),
        ),
        PhotoReportEntry(
            metadata=PhotoReportMetadata(room="Room B", lcd_type="I"),
            result=PhotoProcessingResult(
                image_path="foto2.jpg",
                ocr_result=_ocr_result(["12.40"], 0.91),
                final_values=["12.40"],
                status=PhotoStatus.SUCCESS,
            ),
        ),
        PhotoReportEntry(
            metadata=PhotoReportMetadata(room="Room C", lcd_type="U"),
            result=PhotoProcessingResult(
                image_path="foto3.jpg",
                ocr_result=_ocr_result(["221.10"], 0.96),
                final_values=["221.10"],
                status=PhotoStatus.CORRECTED,
            ),
        ),
    ]

    report = generate_text_report(metadata=metadata, entries=entries)

    expected = (
        "Tanggal: 11 Agustus 2026\n"
        "Waktu: 10:30:15\n"
        "Nama: Budi\n"
        "\n"
        "Foto 1\n"
        "File: foto1.jpg\n"
        "Ruangan: Room A\n"
        "Jenis LCD: V\n"
        "V12: 220.50 V\n"
        "V23: - V\n"
        "V31: - V\n"
        "Confidence: 94.00%\n"
        "\n"
        "Foto 2\n"
        "File: foto2.jpg\n"
        "Ruangan: Room B\n"
        "Jenis LCD: I\n"
        "I12: 12.40 A\n"
        "I23: - A\n"
        "I31: - A\n"
        "Confidence: 91.00%\n"
        "\n"
        "Foto 3\n"
        "File: foto3.jpg\n"
        "Ruangan: Room C\n"
        "Jenis LCD: U\n"
        "U12: 221.10 V\n"
        "U23: - V\n"
        "U31: - V\n"
        "Confidence: 96.00%"
    )
    assert report == expected


def test_generate_text_report_rejects_invalid_lcd_type() -> None:
    metadata = BatchReportMetadata(
        date="11 Agustus 2026",
        time="10:30:15",
        name="Budi",
    )
    entry = PhotoReportEntry(
        metadata=PhotoReportMetadata(room="Ruang Panel 1", lcd_type="X"),
        result=PhotoProcessingResult(
            image_path="foto1.jpg",
            ocr_result=None,
            final_values=["394.12", "397.68", "395.05"],
            status=PhotoStatus.SUCCESS,
        ),
    )

    with pytest.raises(ValueError, match="LCD type must be one of"):
        generate_text_report(metadata=metadata, entries=[entry])


def test_generate_text_report_uses_ampere_unit_for_i_lcd_type() -> None:
    metadata = BatchReportMetadata(
        date="11 Agustus 2026",
        time="10:30:15",
        name="Budi",
    )
    entry = PhotoReportEntry(
        metadata=PhotoReportMetadata(room="Ruang Panel 1", lcd_type="I"),
        result=PhotoProcessingResult(
            image_path="foto1.jpg",
            ocr_result=None,
            final_values=["10.25", "10.11", "9.98"],
            status=PhotoStatus.SUCCESS,
        ),
    )

    report = generate_text_report(metadata=metadata, entries=[entry])

    assert "I12: 10.25 A" in report
    assert "I23: 10.11 A" in report
    assert "I31: 9.98 A" in report
    assert "I12: 10.25 V" not in report


def _ocr_result(values: list[str], confidence: float) -> OCRResult:
    return OCRResult(
        raw_text="\n".join(values),
        values=values,
        confidence=confidence,
        status=OCRStatus.SUCCESS,
    )
