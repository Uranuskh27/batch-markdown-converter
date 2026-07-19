from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
)

from core.config import AppSettings
from core.i18n import language, tr
from .switch_checkbox import SwitchCheckBox


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle(tr("설정", "Settings"))
        self.setMinimumWidth(620 if language() == "en" else 460)

        self.concurrency = QSpinBox()
        self.concurrency.setRange(1, 4)
        self.concurrency.setValue(settings.concurrency)

        self.timeout = QSpinBox()
        self.timeout.setRange(10, 3600)
        self.timeout.setSuffix(tr("초", " sec"))
        self.timeout.setValue(settings.timeout_seconds)

        self.collision = QComboBox()
        self.collision.addItem(tr("자동으로 이름 변경", "Rename automatically"), "rename")
        self.collision.addItem(tr("기존 파일 건너뛰기", "Skip existing file"), "skip")
        self.collision.addItem(tr("기존 파일 덮어쓰기", "Overwrite existing file"), "overwrite")
        self.collision.setCurrentIndex(max(0, self.collision.findData(settings.collision_policy)))

        self.open_output_directory = SwitchCheckBox(
            tr(
                "변환이 끝나면 Finder에서 출력 폴더 열기",
                "Open the output folder in Finder when conversion finishes",
            )
        )
        self.open_output_directory.setChecked(settings.open_output_directory)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("저장", "Save"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("취소", "Cancel"))
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow(tr("동시 변환 수", "Concurrent conversions"), self.concurrency)
        layout.addRow(tr("파일당 제한 시간", "Time limit per file"), self.timeout)
        layout.addRow(tr("파일명 충돌", "File name conflicts"), self.collision)
        layout.addRow(tr("완료 동작", "When finished"), self.open_output_directory)
        layout.addRow(buttons)

    def _save(self) -> None:
        self.settings.concurrency = self.concurrency.value()
        self.settings.timeout_seconds = self.timeout.value()
        self.settings.collision_policy = str(self.collision.currentData())
        self.settings.open_output_directory = self.open_output_directory.isChecked()
        self.accept()
