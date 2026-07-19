from __future__ import annotations

import os
import re
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QLabel, QPushButton

from core.i18n import application_settings_name
from core.jobs import Job, JobStatus
from core.process_manager import JobManager
from core.scanner import Scanner
from core.worker_entry import validate_source
from tests.test_process_edge_cases import wait_for
from ui.main_window import MainWindow
from ui.dog_progress_bar import BoneGoalIcon, DogProgressBar
from ui.settings_dialog import SettingsDialog
from ui.theme_switch import ThemeSwitch


class EnglishSettings:
    output_mode = "source"
    output_directory = None
    collision_policy = "rename"
    concurrency = 2
    timeout_seconds = 30
    max_file_size_mb = 200
    max_scan_files = 10_000
    open_output_directory = False
    theme = "light"


def test_english_app_uses_separate_settings_name(monkeypatch) -> None:
    monkeypatch.delenv("BATCH_MARKDOWN_CONVERTER_LANGUAGE", raising=False)
    assert application_settings_name() == "BatchMarkdownConverterKorean"

    monkeypatch.setenv("BATCH_MARKDOWN_CONVERTER_LANGUAGE", "en")
    assert application_settings_name() == "BatchMarkdownConverterEnglish"


def test_english_main_window_and_settings_have_no_korean_ui_text(monkeypatch) -> None:
    monkeypatch.setenv("BATCH_MARKDOWN_CONVERTER_LANGUAGE", "en")
    application = QApplication.instance() or QApplication([])
    settings = EnglishSettings()
    manager = JobManager(settings, Path(__file__).parents[1] / "app_en.py")
    window = MainWindow(manager, settings)
    dialog = SettingsDialog(settings, window)

    assert window.windowTitle() == "Batch Markdown Converter English"
    window.show()
    application.processEvents()
    status_text_x = (
        window.status_message_label.mapTo(window, QPoint(0, 0)).x()
        + window.status_message_label.contentsMargins().left()
    )
    assert status_text_x == window.summary_label.mapTo(window, QPoint(0, 0)).x()
    assert window.status_message_label.contentsMargins().top() == 4
    assert window.status_message_label.contentsMargins().bottom() == 4
    assert window.add_button.text() == "Add Files"
    assert not hasattr(window, "add_folder_button")
    assert isinstance(window.progress, DogProgressBar)
    assert window.progress.DOG_STYLE == "animated-cute-shiba-vector"
    assert isinstance(window.progress_goal_icon, BoneGoalIcon)
    assert window.progress.toolTip().startswith("The side-profile dog runs")
    assert window.progress_goal_icon.toolTip() == "Conversion goal"
    assert window.progress.width() >= window.centralWidget().width() * 0.8
    assert window.progress.mapTo(window, QPoint(0, 0)).y() < window.summary_label.mapTo(
        window, QPoint(0, 0)
    ).y()
    assert settings.output_mode == "directory"
    assert not hasattr(window, "output_mode")
    assert window.output_label.text() == "Choose where converted files will be saved"
    assert window.choose_output_button.text() == "Choose Folder…"
    assert isinstance(window.theme_toggle_button, ThemeSwitch)
    assert window.theme_toggle_button.text() == ""
    assert not window.theme_toggle_button.isChecked()
    window.theme_toggle_button.click()
    assert settings.theme == "dark"
    assert window.theme_toggle_button.text() == ""
    assert window.theme_toggle_button.isChecked()
    window.theme_toggle_button.click()
    assert settings.theme == "light"
    assert not window.theme_toggle_button.isChecked()
    assert window.start_button.text() == "Convert All"
    assert window.model.headerData(0, Qt.Orientation.Horizontal) == "File Name"
    assert window.model.headerData(2, Qt.Orientation.Horizontal) == "Status"
    assert dialog.windowTitle() == "Settings"
    assert dialog.minimumWidth() == 620
    assert dialog.open_output_directory.text().startswith("Open the output folder")

    visible_texts = [
        widget.text()
        for widget in [
            *window.findChildren(QLabel),
            *window.findChildren(QPushButton),
            *dialog.findChildren(QLabel),
            *dialog.findChildren(QPushButton),
            *dialog.findChildren(QCheckBox),
        ]
    ]
    for combo in [*window.findChildren(QComboBox), *dialog.findChildren(QComboBox)]:
        visible_texts.extend(combo.itemText(index) for index in range(combo.count()))
    assert not any(re.search(r"[가-힣]", text) for text in visible_texts)

    dialog.close()
    window.close()
    assert application is not None


def test_skipped_items_do_not_advance_english_progress(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BATCH_MARKDOWN_CONVERTER_LANGUAGE", "en")
    application = QApplication.instance() or QApplication([])
    settings = EnglishSettings()
    manager = JobManager(settings, Path(__file__).parents[1] / "app_en.py")
    window = MainWindow(manager, settings)
    manager.jobs.extend(
        [
            Job(tmp_path / "unsupported-one.bin", 1, status=JobStatus.SKIPPED),
            Job(tmp_path / "unsupported-two.bin", 1, status=JobStatus.SKIPPED),
        ]
    )

    window._update_summary()

    assert window.progress.maximum() == 2
    assert window.progress.value() == 0
    assert window.progress.format() == "0/2 · %p%"
    assert window.progress.dog_position() == 0.0
    window.close()
    assert application is not None


def test_english_status_scanner_and_validation_messages(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BATCH_MARKDOWN_CONVERTER_LANGUAGE", "en")
    settings = EnglishSettings()
    manager = JobManager(settings, Path(__file__).parents[1] / "app_en.py")
    job = Job(tmp_path / "queued.txt", 1, status=JobStatus.QUEUED)
    manager.jobs.append(job)
    from ui.file_table import FileTableModel

    model = FileTableModel(manager.jobs)
    assert model.data(model.index(0, 2)) == "Queued"

    missing = tmp_path / "missing.pdf"
    found = []
    scanner = Scanner([missing])
    scanner.batch_found.connect(found.extend)
    scanner.run()
    assert found[0].skip_reason == "File not found"

    invalid_pdf = tmp_path / "broken.pdf"
    invalid_pdf.write_bytes(b"not a PDF")
    with pytest.raises(ValueError, match="invalid or corrupted"):
        validate_source(invalid_pdf)


def test_english_gui_worker_and_output_pipeline(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BATCH_MARKDOWN_CONVERTER_LANGUAGE", "en")
    application = QApplication.instance() or QApplication([])
    source_root = tmp_path / "input"
    source_root.mkdir()
    (source_root / "document.txt").write_text("ENGLISH_E2E_MARKER", encoding="utf-8")
    (source_root / "broken.pdf").write_bytes(b"not a PDF")

    settings = EnglishSettings()
    settings.output_mode = "directory"
    settings.output_directory = tmp_path / "output"
    manager = JobManager(settings, Path(__file__).parents[1] / "app_en.py")
    window = MainWindow(manager, settings)

    window.add_paths([source_root])
    assert wait_for(lambda: not window._scanners)
    window.start_button.click()
    assert wait_for(lambda: not manager.is_processing, 30_000)

    by_name = {job.src.name: job for job in manager.jobs}
    assert by_name["document.txt"].status == JobStatus.DONE
    assert by_name["broken.pdf"].status == JobStatus.FAILED
    assert by_name["broken.pdf"].error == "The PDF file is invalid or corrupted."
    assert "Completed 1" in window.summary_label.text()
    assert "Failed 1" in window.summary_label.text()
    output = settings.output_directory / "input" / "document.md"
    assert "ENGLISH_E2E_MARKER" in output.read_text(encoding="utf-8")

    window.close()
    application.processEvents()
    assert application is not None
