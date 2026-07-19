from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QProcess, QThread, QTimer, Qt, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.config import AppSettings
from core.i18n import application_display_name, tr
from core.jobs import JobStatus
from core.process_manager import JobManager
from core.scanner import Scanner
from .drop_zone import DropZone
from .dog_progress_bar import BoneGoalIcon, DogProgressBar
from .file_table import FileTableModel
from .settings_dialog import SettingsDialog
from .theme_switch import ThemeSwitch
from .theme import apply_theme


def _open_finder_directory(directory: Path) -> bool:
    return QProcess.startDetached("/usr/bin/open", [str(directory)])


class MainWindow(QMainWindow):
    def __init__(self, manager: JobManager, settings: AppSettings) -> None:
        super().__init__()
        self.manager = manager
        self.settings = settings
        self._scanners: dict[QThread, Scanner] = {}

        self.setWindowTitle(application_display_name())
        self.resize(940, 680)
        self.setMinimumSize(720, 520)

        self.drop_zone = DropZone()
        self.drop_zone.paths_dropped.connect(self.add_paths)

        self.model = FileTableModel(manager.jobs)
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 260)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 100)
        self.table.doubleClicked.connect(self._reveal_result)

        # The app has one predictable output policy: every converted file is
        # written below the folder chosen by the user. Migrate settings saved by
        # older releases that still offered a "next to source" mode.
        self.settings.output_mode = "directory"

        self.output_label = QLabel()
        self.output_label.setObjectName("outputPath")
        self.output_label.setAccessibleName(tr("결과 저장 위치", "Output location"))
        self.output_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.choose_output_button = QPushButton(tr("폴더 선택…", "Choose Folder…"))
        self.choose_output_button.setAccessibleName(
            tr("결과 저장 폴더 선택", "Choose output folder")
        )
        self.choose_output_button.clicked.connect(self._choose_output_directory)

        self.add_button = QPushButton(tr("파일 추가", "Add Files"))
        self.add_button.clicked.connect(self._choose_inputs)
        self.theme_toggle_button = ThemeSwitch()
        self.theme_toggle_button.setAccessibleName(tr("테마 전환", "Theme switch"))
        self.theme_toggle_button.setChecked(
            getattr(self.settings, "theme", "light") == "dark"
        )
        self.theme_toggle_button.toggled.connect(self._theme_switch_changed)
        self._update_theme_toggle_switch()
        self.settings_button = QPushButton(tr("설정", "Settings"))
        self.settings_button.clicked.connect(self._show_settings)
        self.clear_button = QPushButton(tr("완료 항목 지우기", "Clear Finished"))
        self.clear_button.clicked.connect(self.manager.clear_finished)
        self.retry_button = QPushButton(tr("실패만 재시도", "Retry Failed"))
        self.retry_button.clicked.connect(self.manager.retry_failed)
        self.cancel_button = QPushButton(tr("취소", "Cancel"))
        self.cancel_button.clicked.connect(self.manager.cancel_all)
        self.start_button = QPushButton(tr("모두 변환", "Convert All"))
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.manager.start_all)

        self.progress = DogProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setAccessibleName(tr("변환 진행률", "Conversion progress"))
        self.progress.setToolTip(
            tr(
                "옆모습 강아지가 진행률에 따라 뼈다귀를 향해 달립니다.",
                "The side-profile dog runs toward the bone as conversion progresses.",
            )
        )
        self.progress_goal_icon = BoneGoalIcon()
        self.progress_goal_icon.setAccessibleName(tr("변환 완료 목표", "Conversion goal"))
        self.progress_goal_icon.setToolTip(tr("변환 완료 목표", "Conversion goal"))
        self.summary_label = QLabel(tr("준비됨", "Ready"))

        top_buttons = QHBoxLayout()
        top_buttons.addWidget(QLabel("Batch Markdown Converter"))
        top_buttons.addStretch()
        top_buttons.addWidget(self.add_button)
        top_buttons.addSpacing(8)
        top_buttons.addWidget(self.theme_toggle_button)
        top_buttons.addWidget(self.settings_button)

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel(tr("결과 저장:", "Save results:")))
        output_row.addWidget(self.choose_output_button)
        output_row.addWidget(self.output_label, 1)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(8)
        progress_row.addWidget(self.progress, 1)
        progress_row.addWidget(self.progress_goal_icon)

        action_row = QHBoxLayout()
        action_row.addWidget(self.summary_label)
        action_row.addStretch()
        action_row.addWidget(self.clear_button)
        action_row.addWidget(self.retry_button)
        action_row.addWidget(self.cancel_button)
        action_row.addWidget(self.start_button)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)
        layout.addLayout(top_buttons)
        layout.addWidget(self.drop_zone)
        layout.addWidget(self.table, 1)
        layout.addLayout(output_row)
        layout.addLayout(progress_row)
        layout.addLayout(action_row)
        self.setCentralWidget(central)

        self.status_message_label = QLabel()
        self.status_message_label.setObjectName("statusMessage")
        self.status_message_label.setMinimumHeight(30)
        self.statusBar().addWidget(self.status_message_label, 1)
        self._status_clear_timer = QTimer(self)
        self._status_clear_timer.setSingleShot(True)
        self._status_clear_timer.timeout.connect(self.status_message_label.clear)
        self._set_status(tr("파일이나 폴더를 추가하세요.", "Add files or folders to begin."))
        self.manager.jobs_changed.connect(self.model.refresh)
        self.manager.summary_changed.connect(self._update_summary)
        self.manager.notice.connect(self._show_notice)
        self.manager.batch_finished.connect(self._batch_finished)

        self._update_output_controls()
        self._update_summary()

    @Slot(list)
    def add_paths(self, paths: list[Path]) -> None:
        if not paths:
            return

        thread = QThread(self)
        scanner = Scanner(
            paths,
            max_files=self.settings.max_scan_files,
            max_file_size_mb=self.settings.max_file_size_mb,
        )
        scanner.moveToThread(thread)
        thread.started.connect(scanner.run)
        scanner.batch_found.connect(self._scan_batch)
        scanner.notice.connect(self._show_notice)
        scanner.finished.connect(thread.quit)
        scanner.finished.connect(scanner.deleteLater)
        thread.finished.connect(self._scanner_thread_finished)
        self._scanners[thread] = scanner
        self._set_status(tr("파일을 찾는 중…", "Scanning for files…"))
        thread.start()

    @Slot(list)
    def _scan_batch(self, files: list) -> None:
        self.manager.add_scanned(files)

    @Slot()
    def _scanner_thread_finished(self) -> None:
        thread = self.sender()
        if not isinstance(thread, QThread):
            return
        self._scanners.pop(thread, None)
        if not self._scanners:
            self._set_status(
                tr(
                    f"{len(self.manager.jobs):,}개 항목을 찾았습니다.",
                    f"Found {len(self.manager.jobs):,} items.",
                ),
                5000,
            )
        thread.deleteLater()

    def _choose_inputs(self) -> None:
        dialog = QFileDialog(
            self,
            tr("변환할 파일 또는 폴더 선택", "Choose files or folders to convert"),
        )
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if dialog.exec():
            self.add_paths([Path(path) for path in dialog.selectedFiles()])

    def _choose_output_directory(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            tr("결과 저장 폴더 선택", "Choose an output folder"),
            str(self.settings.output_directory or Path.home()),
        )
        if selected:
            self.settings.output_directory = Path(selected)
            self.settings.output_mode = "directory"
            self._update_output_controls()

    def _update_output_controls(self) -> None:
        directory = self.settings.output_directory
        self.settings.output_mode = "directory"
        self.output_label.setProperty("needsSelection", not bool(directory))
        if directory:
            self.output_label.setText(str(directory))
            self.output_label.setToolTip(str(directory))
        else:
            self.output_label.setText(
                tr("저장할 폴더를 선택하세요", "Choose where converted files will be saved")
            )
            self.output_label.setToolTip("")
        self.output_label.style().unpolish(self.output_label)
        self.output_label.style().polish(self.output_label)

    def _show_settings(self) -> None:
        SettingsDialog(self.settings, self).exec()

    def _set_theme(self, theme: str) -> None:
        self.settings.theme = theme
        application = QApplication.instance()
        if application is not None:
            apply_theme(application, theme)
        self._update_theme_toggle_switch()

    @Slot(bool)
    def _theme_switch_changed(self, checked: bool) -> None:
        self._set_theme("dark" if checked else "light")

    def _update_theme_toggle_switch(self) -> None:
        current_theme = getattr(self.settings, "theme", "light")
        self.theme_toggle_button.setChecked(current_theme == "dark")
        if current_theme == "dark":
            self.theme_toggle_button.setToolTip(
                tr("일반 모드로 전환", "Switch to light mode")
            )
        else:
            self.theme_toggle_button.setToolTip(
                tr("다크 모드로 전환", "Switch to dark mode")
            )

    @Slot()
    def _update_summary(self) -> None:
        jobs = self.manager.jobs
        progressed = sum(
            job.status.finished and job.status != JobStatus.SKIPPED for job in jobs
        )
        done = sum(job.status == JobStatus.DONE for job in jobs)
        failed = sum(job.status == JobStatus.FAILED for job in jobs)
        running = sum(job.status == JobStatus.RUNNING for job in jobs)

        summary = tr(
            f"전체 {len(jobs)} · 완료 {done} · 실패 {failed}",
            f"Total {len(jobs)} · Completed {done} · Failed {failed}",
        )
        if running:
            summary += tr(f" · 변환 중 {running}", f" · Converting {running}")
        self.summary_label.setText(summary)
        self.progress.setMaximum(max(1, len(jobs)))
        self.progress.setValue(progressed)
        self.progress.setFormat(f"{progressed}/{len(jobs)} · %p%")
        self.cancel_button.setEnabled(self.manager.is_processing)
        self.start_button.setEnabled(any(job.status == JobStatus.QUEUED for job in jobs))
        self.retry_button.setEnabled(any(job.status == JobStatus.FAILED for job in jobs))

    @Slot(str)
    def _show_notice(self, message: str) -> None:
        self._set_status(message, 8000)

    @Slot(int, int)
    def _batch_finished(self, completed: int, failed: int) -> None:
        self._set_status(
            tr(
                f"변환 완료: 성공 {completed}개, 실패 {failed}개",
                f"Conversion finished: {completed} completed, {failed} failed",
            ),
            10000,
        )
        if completed > 0 and getattr(self.settings, "open_output_directory", False):
            for directory in self._completed_output_directories():
                _open_finder_directory(directory)

    def _set_status(self, message: str, timeout_ms: int = 0) -> None:
        self._status_clear_timer.stop()
        self.status_message_label.setText(message)
        if timeout_ms > 0:
            self._status_clear_timer.start(timeout_ms)

    def _align_status_message(self) -> None:
        summary_x = self.summary_label.mapTo(self, QPoint(0, 0)).x()
        label_x = self.status_message_label.mapTo(self, QPoint(0, 0)).x()
        self.status_message_label.setContentsMargins(
            max(0, summary_x - label_x), 4, 0, 4
        )

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._align_status_message()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "status_message_label"):
            self._align_status_message()

    def _completed_output_directories(self) -> list[Path]:
        if self.settings.output_mode == "directory" and self.settings.output_directory:
            directory = Path(self.settings.output_directory)
            return [directory] if directory.is_dir() else []

        directories = {
            job.dst.parent
            for job in self.manager.jobs
            if job.status == JobStatus.DONE and job.dst is not None and job.dst.exists()
        }
        return sorted(directories, key=lambda path: str(path).casefold())

    def _reveal_result(self, index) -> None:
        job = self.model.job_at(index.row())
        if job is None:
            return
        target = job.dst if job.dst and job.dst.exists() else job.src
        QProcess.startDetached("/usr/bin/open", ["-R", str(target)])

    def closeEvent(self, event) -> None:
        if self.manager.is_processing or self._scanners:
            answer = QMessageBox.question(
                self,
                tr("작업 중", "Work in progress"),
                tr(
                    "진행 중인 스캔과 변환을 취소하고 종료할까요?",
                    "Cancel the active scan and conversions, then quit?",
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.manager.cancel_all()
            scanners = list(self._scanners.items())
            for thread, scanner in scanners:
                scanner.cancel()
                thread.requestInterruption()
            for thread, _scanner in scanners:
                thread.quit()
                thread.wait(3000)
        event.accept()
