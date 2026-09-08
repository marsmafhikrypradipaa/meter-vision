from datetime import datetime
from pathlib import Path
from tkinter import Button, Text, Tk, filedialog, messagebox, simpledialog
from typing import Protocol

from app.config import DEFAULT_PREPROCESSING_CONFIG
from app.cropper import select_crop_manually
from app.image_processor import process_single_image, with_manual_correction
from app.models import PhotoProcessingResult, PhotoStatus
from app.ocr_engine import PaddleOCREngine
from app.parser import parse_voltage_values
from app.report.text_report import (
    BatchReportMetadata,
    PhotoReportEntry,
    PhotoReportMetadata,
    generate_text_report,
)


class TextContentWidget(Protocol):
    def get(self, index1: str, index2: str | None = None) -> str:
        ...


def choose_image_paths() -> list[Path]:
    root = Tk()
    root.withdraw()
    root.update()
    selected_paths = filedialog.askopenfilenames(
        title="Pilih foto PM5100",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()

    return [Path(selected_path) for selected_path in selected_paths]


def main() -> None:
    batch_metadata = ask_batch_metadata()
    if batch_metadata is None:
        return

    image_paths = choose_image_paths()
    if not image_paths:
        return

    ocr_engine = PaddleOCREngine(language="en")
    entries: list[PhotoReportEntry] = []

    for index, image_path in enumerate(image_paths, start=1):
        photo_metadata = ask_photo_metadata(index)
        if photo_metadata is None:
            return

        result = process_single_image(
            image_path=image_path,
            crop_selector=lambda image, photo_index=index: select_crop_manually(
                f"Foto {photo_index}: crop angka tegangan - ENTER/SPACE confirm, C cancel",
                image,
            ),
            ocr_reader=ocr_engine.read_text,
            config=DEFAULT_PREPROCESSING_CONFIG,
        )

        result = verify_or_correct_result(index, result)
        entries.append(PhotoReportEntry(metadata=photo_metadata, result=result))

    show_final_report(batch_metadata, entries)


def verify_or_correct_result(
    photo_index: int,
    result: PhotoProcessingResult,
) -> PhotoProcessingResult:
    if result.status == PhotoStatus.SUCCESS:
        is_correct = messagebox.askyesno(
            f"Foto {photo_index} OCR",
            _format_result_message(result) +
            "\n\nApakah hasil OCR sudah benar?",
        )
        if is_correct:
            return result

    corrected_values = ask_manual_correction(photo_index, result)
    if corrected_values is None:
        return result

    return with_manual_correction(result, corrected_values)


def ask_manual_correction(
    photo_index: int,
    result: PhotoProcessingResult,
) -> list[str] | None:
    correction = simpledialog.askstring(
        f"Koreksi Foto {photo_index}",
        _format_result_message(result)
        + "\n\nMasukkan 3 nilai tegangan, pisahkan dengan spasi atau baris baru:",
    )
    if correction is None:
        return None

    parsed = parse_voltage_values(correction)
    if len(parsed.values) != 3:
        messagebox.showerror(
            "Koreksi tidak valid",
            "Koreksi harus berisi tepat 3 nilai tegangan.",
        )
        return None

    return parsed.values


def show_final_report(
    metadata: BatchReportMetadata,
    entries: list[PhotoReportEntry],
) -> None:
    report_text = generate_text_report(metadata=metadata, entries=entries)
    show_report_window(report_text)


def ask_batch_metadata() -> BatchReportMetadata | None:
    name = ask_required_text(
        title="Nama User",
        prompt="Masukkan nama user:",
    )
    if name is None:
        return None

    batch_datetime = datetime.now()
    return BatchReportMetadata(
        date=_format_report_date(batch_datetime),
        time=_format_report_time(batch_datetime),
        name=name,
    )


def ask_photo_metadata(photo_index: int) -> PhotoReportMetadata | None:
    room = ask_required_text(
        title=f"Ruangan Foto {photo_index}",
        prompt=f"Masukkan nama ruangan untuk foto {photo_index}:",
    )
    if room is None:
        return None

    lcd_type = ask_lcd_type(photo_index)
    if lcd_type is None:
        return None

    return PhotoReportMetadata(
        room=room,
        lcd_type=lcd_type,
    )


def ask_required_text(
    title: str,
    prompt: str,
    initialvalue: str | None = None,
) -> str | None:
    current_initial = initialvalue
    while True:
        value = simpledialog.askstring(
            title,
            prompt,
            initialvalue=current_initial,
        )
        if value is None:
            return None

        stripped = value.strip()
        if stripped:
            return stripped

        messagebox.showerror(title, "Input tidak boleh kosong.")
        current_initial = None


def ask_lcd_type(photo_index: int | None = None) -> str | None:
    title = "Jenis LCD" if photo_index is None else f"Jenis LCD Foto {photo_index}"
    prompt = (
        "Masukkan jenis LCD (V/I/U):"
        if photo_index is None
        else f"Masukkan jenis LCD untuk foto {photo_index} (V/I/U):"
    )
    while True:
        value = simpledialog.askstring(
            title,
            prompt,
        )
        if value is None:
            return None

        normalized = value.strip().upper()
        if normalized in {"V", "I", "U"}:
            return normalized

        messagebox.showerror(
            title, "Jenis LCD harus salah satu dari V, I, atau U.")


def show_report_window(report_text: str) -> None:
    root = Tk()
    root.title("Report Hasil PM5100")
    root.geometry("700x640")

    report_box = Text(root, wrap="word")
    report_box.pack(fill="both", expand=True, padx=12, pady=(12, 8))
    report_box.insert("1.0", report_text)

    copy_button = Button(
        root,
        text="[ Salin Hasil ]",
        command=lambda: copy_report_to_clipboard(root, report_box),
    )
    copy_button.pack(pady=(0, 12))

    root.mainloop()


def copy_report_to_clipboard(root: Tk, report_box: TextContentWidget) -> None:
    report_text = get_current_report_text(report_box)
    root.clipboard_clear()
    root.clipboard_append(report_text)
    root.update()
    messagebox.showinfo(
        "Salin Hasil", "Report berhasil disalin ke clipboard.", parent=root)


def get_current_report_text(report_box: TextContentWidget) -> str:
    return report_box.get("1.0", "end-1c")


def _format_report_date(value: datetime) -> str:
    months = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    month_name = months[value.month - 1]
    return f"{value.day} {month_name} {value.year}"


def _format_report_time(value: datetime) -> str:
    return value.strftime("%H:%M:%S")


def _format_result_message(result: PhotoProcessingResult) -> str:
    raw_text = result.ocr_result.raw_text if result.ocr_result else "-"
    values = ", ".join(result.final_values) if result.final_values else "-"
    error = f"\nError: {result.error_message}" if result.error_message else ""

    return (
        f"File: {result.image_path}\n"
        f"Status: {result.status.value}\n"
        f"Raw OCR:\n{raw_text}\n\n"
        f"Nilai: {values}"
        f"{error}"
    )


if __name__ == "__main__":
    main()
