import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette

from core.process_manager import JobManager
from core.jobs import Job, JobStatus
import ui.main_window as main_window_module
from ui.main_window import MainWindow
from ui.dog_progress_bar import BoneGoalIcon, DogProgressBar
from ui.settings_dialog import SettingsDialog
from ui.segmented_control import SegmentedControl
from ui.theme_switch import ThemeSwitch


class TestSettings:
    output_mode = "source"
    output_directory = None
    collision_policy = "rename"
    concurrency = 2
    timeout_seconds = 30
    max_file_size_mb = 200
    max_scan_files = 10_000
    open_output_directory = False
    theme = "light"


def test_main_window_can_be_created() -> None:
    application = QApplication.instance() or QApplication([])
    settings = TestSettings()
    manager = JobManager(settings, Path(__file__).parents[1] / "app.py")
    window = MainWindow(manager, settings)
    assert window.windowTitle() == "Batch Markdown Converter Korean"
    assert not hasattr(window, "add_folder_button")
    assert window.start_button.isEnabled() is False
    window.show()
    application.processEvents()
    status_text_x = (
        window.status_message_label.mapTo(window, QPoint(0, 0)).x()
        + window.status_message_label.contentsMargins().left()
    )
    assert status_text_x == window.summary_label.mapTo(window, QPoint(0, 0)).x()
    assert isinstance(window.progress, DogProgressBar)
    assert window.progress.DOG_STYLE == "animated-cute-shiba-vector"
    assert isinstance(window.progress_goal_icon, BoneGoalIcon)
    assert "뼈다귀를 향해 달립니다" in window.progress.toolTip()
    assert "%p%" in window.progress.format()
    assert window.progress.width() >= window.centralWidget().width() * 0.8
    assert window.progress.mapTo(window, QPoint(0, 0)).y() < window.summary_label.mapTo(
        window, QPoint(0, 0)
    ).y()
    assert isinstance(window.output_mode, SegmentedControl)
    assert window.output_mode.current_data() == "source"
    assert window.output_mode.button_for_data("source").text() == "원본 옆"
    assert ".md로 저장" in window.output_label.text()
    assert not window.choose_output_button.isVisible()
    window.output_mode.button_for_data("directory").click()
    assert settings.output_mode == "directory"
    assert "선택하세요" in window.output_label.text()
    assert window.choose_output_button.isVisible()
    assert window.choose_output_button.text() == "폴더 선택…"
    window.output_mode.button_for_data("source").click()
    assert isinstance(window.theme_toggle_button, ThemeSwitch)
    assert window.theme_toggle_button.text() == ""
    assert not window.theme_toggle_button.isChecked()
    assert window.theme_toggle_button.toolTip() == "다크 모드로 전환"

    window.theme_toggle_button.click()
    assert settings.theme == "dark"
    assert window.theme_toggle_button.text() == ""
    assert window.theme_toggle_button.isChecked()
    assert window.theme_toggle_button.toolTip() == "일반 모드로 전환"
    assert application.palette().color(QPalette.ColorRole.Window).name() == "#171a1f"

    window.theme_toggle_button.click()
    assert settings.theme == "light"
    assert window.theme_toggle_button.text() == ""
    assert not window.theme_toggle_button.isChecked()
    assert application.palette().color(QPalette.ColorRole.Window).name() == "#f5f7fa"
    window.close()
    assert application is not None


def test_skipped_items_do_not_advance_korean_progress(tmp_path: Path) -> None:
    application = QApplication.instance() or QApplication([])
    settings = TestSettings()
    manager = JobManager(settings, Path(__file__).parents[1] / "app.py")
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


def test_open_output_directory_option_is_off_by_default_and_saved() -> None:
    application = QApplication.instance() or QApplication([])
    settings = TestSettings()
    dialog = SettingsDialog(settings)

    assert dialog.minimumWidth() == 460
    assert not dialog.open_output_directory.isChecked()
    dialog.open_output_directory.setChecked(True)
    dialog._save()

    assert settings.open_output_directory is True
    assert application is not None


def test_batch_finished_opens_successful_output_directories_when_enabled(
    tmp_path: Path, monkeypatch
) -> None:
    application = QApplication.instance() or QApplication([])
    settings = TestSettings()
    settings.open_output_directory = True
    manager = JobManager(settings, Path(__file__).parents[1] / "app.py")
    window = MainWindow(manager, settings)
    first_directory = tmp_path / "first"
    second_directory = tmp_path / "second"
    first_directory.mkdir()
    second_directory.mkdir()
    first_output = first_directory / "one.md"
    second_output = second_directory / "two.md"
    first_output.write_text("one", encoding="utf-8")
    second_output.write_text("two", encoding="utf-8")
    manager.jobs.extend(
        [
            Job(tmp_path / "one.txt", 3, status=JobStatus.DONE, dst=first_output),
            Job(tmp_path / "two.txt", 3, status=JobStatus.DONE, dst=second_output),
            Job(tmp_path / "three.txt", 3, status=JobStatus.FAILED),
        ]
    )
    opened: list[Path] = []
    monkeypatch.setattr(main_window_module, "_open_finder_directory", lambda path: opened.append(path) or True)

    window._batch_finished(2, 1)

    assert opened == [first_directory, second_directory]
    window.close()
    assert application is not None


def test_batch_finished_does_not_open_directory_when_option_is_disabled(
    tmp_path: Path, monkeypatch
) -> None:
    application = QApplication.instance() or QApplication([])
    settings = TestSettings()
    manager = JobManager(settings, Path(__file__).parents[1] / "app.py")
    window = MainWindow(manager, settings)
    output = tmp_path / "result.md"
    output.write_text("done", encoding="utf-8")
    manager.jobs.append(Job(tmp_path / "input.txt", 4, status=JobStatus.DONE, dst=output))
    opened: list[Path] = []
    monkeypatch.setattr(main_window_module, "_open_finder_directory", lambda path: opened.append(path) or True)

    window._batch_finished(1, 0)

    assert opened == []
    window.close()
    assert application is not None


def test_batch_finished_opens_configured_output_root(tmp_path: Path, monkeypatch) -> None:
    application = QApplication.instance() or QApplication([])
    settings = TestSettings()
    settings.output_mode = "directory"
    settings.output_directory = tmp_path / "output"
    settings.output_directory.mkdir()
    settings.open_output_directory = True
    manager = JobManager(settings, Path(__file__).parents[1] / "app.py")
    window = MainWindow(manager, settings)
    nested = settings.output_directory / "input" / "nested"
    nested.mkdir(parents=True)
    output = nested / "result.md"
    output.write_text("done", encoding="utf-8")
    manager.jobs.append(Job(tmp_path / "input.txt", 4, status=JobStatus.DONE, dst=output))
    opened: list[Path] = []
    monkeypatch.setattr(main_window_module, "_open_finder_directory", lambda path: opened.append(path) or True)

    window._batch_finished(1, 0)

    assert opened == [settings.output_directory]
    window.close()
    assert application is not None
