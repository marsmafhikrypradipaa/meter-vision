import csv
import zipfile
from pathlib import Path

from app.report.export_report import (
    build_export_rows,
    export_report_to_csv,
    export_report_to_excel,
)


REPORT_TEXT = """LAPORAN PEMBACAAN METER

Tanggal : 13 September 2026
Waktu   : 10:01:44
Nama    : Fhikry

Foto 1
Ruangan   : Room A
Jenis LCD : V

Hasil Pembacaan:
V1 : 220.50 V
V2 : 221.10 V
V3 : 222.30 V

Foto 2
Ruangan   : Room B
Jenis LCD : I

Hasil Pembacaan:
I1 : 12.40 A
I2 : 12.50 A
I3 : 12.60 A
"""


def test_build_export_rows_from_report_text() -> None:
    rows = build_export_rows(REPORT_TEXT)

    assert rows[0] == {
        "Tanggal": "13 September 2026",
        "Waktu": "10:01:44",
        "Nama": "Fhikry",
        "Foto": "Foto 1",
        "Ruangan": "Room A",
        "Jenis LCD": "V",
        "Label": "V1",
        "Nilai": "220.50",
        "Satuan": "V",
        "Confidence OCR": "",
    }
    assert rows[3]["Foto"] == "Foto 2"
    assert rows[3]["Ruangan"] == "Room B"
    assert rows[3]["Jenis LCD"] == "I"
    assert rows[3]["Label"] == "I1"
    assert rows[3]["Nilai"] == "12.40"
    assert rows[3]["Satuan"] == "A"
    assert rows[3]["Confidence OCR"] == ""


def test_export_report_to_csv(tmp_path: Path) -> None:
    output_path = tmp_path / "report.csv"

    export_report_to_csv(REPORT_TEXT, output_path)

    with output_path.open(encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows[0]["Nama"] == "Fhikry"
    assert rows[0]["Nilai"] == "220.50"
    assert rows[3]["Ruangan"] == "Room B"
    assert rows[3]["Nilai"] == "12.40"


def test_export_report_to_excel(tmp_path: Path) -> None:
    output_path = tmp_path / "report.xlsx"

    export_report_to_excel(REPORT_TEXT, output_path)

    with zipfile.ZipFile(output_path) as xlsx:
        worksheet_xml = xlsx.read("xl/worksheets/sheet1.xml").decode()

    assert "Fhikry" in worksheet_xml
    assert "Room A" in worksheet_xml
    assert "220.50" in worksheet_xml
    assert "Room B" in worksheet_xml
    assert "12.40" in worksheet_xml
