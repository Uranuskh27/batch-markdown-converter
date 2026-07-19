from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from core.i18n import tr


class DropZone(QFrame):
    paths_dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setMinimumHeight(150)

        layout = QVBoxLayout(self)
        title = QLabel(tr("파일 또는 폴더를 여기에 드래그하세요", "Drag files or folders here"))
        title.setObjectName("dropTitle")
        subtitle = QLabel(
            tr("여러 항목을 한 번에 추가할 수 있습니다", "You can add multiple items at once")
        )
        subtitle.setObjectName("dropSubtitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

    def dragEnterEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if urls and any(url.isLocalFile() for url in urls):
            event.acceptProposedAction()
            self.setProperty("active", True)
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._clear_active()
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        self._clear_active()
        if paths:
            self.paths_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _clear_active(self) -> None:
        self.setProperty("active", False)
        self.style().unpolish(self)
        self.style().polish(self)
