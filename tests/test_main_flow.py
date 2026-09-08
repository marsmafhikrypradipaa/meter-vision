from pathlib import Path

import main
from app.models import OCRRawResult
from app.models import PhotoProcessingResult, PhotoStatus
from app.report.text_report import BatchReportMetadata, PhotoReportMetadata


def test_batch_name_is_requested_once_and_photo_metadata_per_image(monkeypatch) -> None:
    calls: list[str] = []
    batch_metadata = BatchReportMetadata(
        date="7 September 2026",
        time="10:30:15",
        name="Budi",
    )
    result = PhotoProcessingResult(
        image_path="foto1.jpg",
        ocr_result=None,
        final_values=["227.17", "228.50", "229.52"],
        status=PhotoStatus.SUCCESS,
    )

    monkeypatch.setattr(
        main,
        "choose_image_paths",
        lambda: [Path("foto1.jpg"), Path("foto2.jpg"), Path("foto3.jpg")],
    )

    def ask_batch_metadata() -> BatchReportMetadata:
        calls.append("batch_metadata")
        return batch_metadata

    def ask_photo_metadata(photo_index: int) -> PhotoReportMetadata:
        calls.append(f"photo_metadata_{photo_index}")
        return PhotoReportMetadata(room=f"Room {photo_index}", lcd_type="V")

    def process_image(**_kwargs) -> PhotoProcessingResult:
        calls.append("process")
        return result

    def show_report(_metadata, _results) -> None:
        calls.append("report")

    class FakeOCREngine:
        def __init__(self, language: str) -> None:
            self.language = language

        def read_text(self, _image) -> OCRRawResult:
            return OCRRawResult(raw_result=None, raw_text="", confidence=None)

    monkeypatch.setattr(main, "ask_batch_metadata", ask_batch_metadata)
    monkeypatch.setattr(main, "ask_photo_metadata", ask_photo_metadata)
    monkeypatch.setattr(main, "PaddleOCREngine", FakeOCREngine)
    monkeypatch.setattr(main, "process_single_image", process_image)
    monkeypatch.setattr(main, "verify_or_correct_result", lambda _index, photo_result: photo_result)
    monkeypatch.setattr(main, "show_final_report", show_report)

    main.main()

    assert calls == [
        "batch_metadata",
        "photo_metadata_1",
        "process",
        "photo_metadata_2",
        "process",
        "photo_metadata_3",
        "process",
        "report",
    ]


def test_copy_report_reads_edited_text(monkeypatch) -> None:
    copied: list[str] = []

    class FakeRoot:
        def clipboard_clear(self) -> None:
            copied.clear()

        def clipboard_append(self, text: str) -> None:
            copied.append(text)

        def update(self) -> None:
            pass

    class FakeReportBox:
        def get(self, index1: str, index2: str | None = None) -> str:
            assert index1 == "1.0"
            assert index2 == "end-1c"
            return "Result: 220.5"

    monkeypatch.setattr(main.messagebox, "showinfo", lambda *_args, **_kwargs: None)

    main.copy_report_to_clipboard(FakeRoot(), FakeReportBox())

    assert copied == ["Result: 220.5"]
