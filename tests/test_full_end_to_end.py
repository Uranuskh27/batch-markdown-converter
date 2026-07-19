from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from core.jobs import JobStatus
from core.process_manager import JobManager
from tests.test_process_edge_cases import wait_for
from ui.main_window import MainWindow


class EndToEndSettings:
    output_mode = "directory"
    output_directory: Path | None = None
    collision_policy = "rename"
    concurrency = 2
    timeout_seconds = 30
    max_file_size_mb = 200
    max_scan_files = 10_000
    open_output_directory = False


def test_gui_scanner_process_worker_and_output_pipeline(tmp_path: Path) -> None:
    application = QApplication.instance() or QApplication([])
    source_root = tmp_path / "input"
    nested = source_root / "nested"
    nested.mkdir(parents=True)
    (nested / "한글 문서.txt").write_text("E2E_TEXT_MARKER", encoding="utf-8")
    (source_root / "page.html").write_text(
        "<html><body><h1>E2E_HTML_MARKER</h1></body></html>", encoding="utf-8"
    )
    (source_root / "broken.pdf").write_bytes(b"not a PDF")
    (source_root / "empty.docx").touch()
    (source_root / "unsupported.bin").write_bytes(b"unsupported")
    (source_root / ".hidden.txt").write_text("hidden", encoding="utf-8")

    settings = EndToEndSettings()
    settings.output_directory = tmp_path / "output"
    manager = JobManager(settings, Path(__file__).parents[1] / "app.py")
    window = MainWindow(manager, settings)

    window.add_paths([source_root])
    assert wait_for(lambda: not window._scanners)
    assert len(manager.jobs) == 5

    window.start_button.click()
    assert wait_for(lambda: not manager.is_processing, 30_000)

    by_name = {job.src.name: job for job in manager.jobs}
    assert by_name["한글 문서.txt"].status == JobStatus.DONE
    assert by_name["page.html"].status == JobStatus.DONE
    assert by_name["broken.pdf"].status == JobStatus.FAILED
    assert "올바른 PDF" in by_name["broken.pdf"].error
    assert by_name["empty.docx"].status == JobStatus.SKIPPED
    assert by_name["unsupported.bin"].status == JobStatus.SKIPPED

    text_output = settings.output_directory / "input" / "nested" / "한글 문서.md"
    html_output = settings.output_directory / "input" / "page.md"
    assert "E2E_TEXT_MARKER" in text_output.read_text(encoding="utf-8")
    assert "E2E\\_HTML\\_MARKER" in html_output.read_text(encoding="utf-8")
    assert not (settings.output_directory / "input" / "broken.md").exists()

    assert window.progress.maximum() == len(manager.jobs)
    assert window.progress.value() == 3
    assert window.progress.format() == "3/5 · %p%"
    assert "완료 2" in window.summary_label.text()
    assert "실패 1" in window.summary_label.text()
    window.close()
    application.processEvents()
    assert application is not None
