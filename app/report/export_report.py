import csv
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


EXPORT_COLUMNS = [
    "Tanggal",
    "Waktu",
    "Nama",
    "Foto",
    "Ruangan",
    "Jenis LCD",
    "Label",
    "Nilai",
    "Satuan",
    "Confidence OCR",
]


def export_report_to_csv(report_text: str, output_path: str | Path) -> None:
    rows = build_export_rows(report_text)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def export_report_to_excel(report_text: str, output_path: str | Path) -> None:
    rows = build_export_rows(report_text)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_xlsx(path, rows)


def build_export_rows(report_text: str) -> list[dict[str, str]]:
    batch = {
        "Tanggal": "",
        "Waktu": "",
        "Nama": "",
    }
    current_photo = ""
    current_room = ""
    current_lcd_type = ""
    current_confidence = ""
    current_rows: list[dict[str, str]] = []
    rows: list[dict[str, str]] = []

    def flush_current_rows() -> None:
        for row in current_rows:
            row["Confidence OCR"] = current_confidence
            rows.append(row)
        current_rows.clear()

    for raw_line in report_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("Foto "):
            flush_current_rows()
            current_photo = line
            current_room = ""
            current_lcd_type = ""
            current_confidence = ""
            continue

        key, separator, value = line.partition(":")
        if not separator:
            continue

        key = key.strip()
        value = value.strip()
        if key == "Hasil Pembacaan":
            continue
        if key in batch:
            batch[key] = value
        elif key == "Ruangan":
            current_room = value
        elif key == "Jenis LCD":
            current_lcd_type = value
        elif key == "Confidence OCR":
            current_confidence = value
        elif key:
            parsed_value, unit = _split_value_and_unit(value)
            current_rows.append(
                {
                    "Tanggal": batch["Tanggal"],
                    "Waktu": batch["Waktu"],
                    "Nama": batch["Nama"],
                    "Foto": current_photo,
                    "Ruangan": current_room,
                    "Jenis LCD": current_lcd_type,
                    "Label": key,
                    "Nilai": parsed_value,
                    "Satuan": unit,
                    "Confidence OCR": current_confidence,
                },
            )

    flush_current_rows()
    return rows


def _split_value_and_unit(value: str) -> tuple[str, str]:
    parts = value.rsplit(maxsplit=1)
    if len(parts) != 2:
        return value, ""
    return parts[0], parts[1]


def _write_xlsx(path: Path, rows: list[dict[str, str]]) -> None:
    table = [EXPORT_COLUMNS]
    table.extend([[row[column] for column in EXPORT_COLUMNS] for row in rows])

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr("[Content_Types].xml", _content_types_xml())
        xlsx.writestr("_rels/.rels", _root_relationships_xml())
        xlsx.writestr("xl/workbook.xml", _workbook_xml())
        xlsx.writestr("xl/_rels/workbook.xml.rels", _workbook_relationships_xml())
        xlsx.writestr("xl/styles.xml", _styles_xml())
        xlsx.writestr("xl/worksheets/sheet1.xml", _worksheet_xml(table))


def _worksheet_xml(table: list[list[str]]) -> str:
    rows_xml = []
    for row_index, row in enumerate(table, start=1):
        cells_xml = []
        for column_index, value in enumerate(row, start=1):
            cell_ref = f"{_column_name(column_index)}{row_index}"
            cells_xml.append(
                f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>',
            )
        rows_xml.append(f'<row r="{row_index}">{"".join(cells_xml)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(rows_xml)}</sheetData>'
        "</worksheet>"
    )


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _content_types_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )


def _root_relationships_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def _workbook_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Data OCR" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )


def _workbook_relationships_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )


def _styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<fonts count=\"1\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts>"
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        "</styleSheet>"
    )
