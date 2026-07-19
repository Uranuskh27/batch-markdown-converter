from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.jobs import Job, JobStatus
from core.i18n import status_text, tr
from .theme import status_foreground


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


class FileTableModel(QAbstractTableModel):
    def __init__(self, jobs: list[Job]) -> None:
        super().__init__()
        self.jobs = jobs
        self.headers = [
            tr("파일명", "File Name"),
            tr("크기", "Size"),
            tr("상태", "Status"),
            tr("결과 / 사유", "Result / Reason"),
        ]

    def refresh(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.jobs)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.jobs)):
            return None
        job = self.jobs[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return job.display_name
            if index.column() == 1:
                return format_size(job.size)
            if index.column() == 2:
                return status_text(job.status)
            if index.column() == 3:
                if job.error:
                    return job.error
                if job.dst:
                    return str(job.dst)
                return ""

        if role == Qt.ItemDataRole.ToolTipRole:
            return str(job.src) if index.column() == 0 else job.error

        if role == Qt.ItemDataRole.ForegroundRole:
            if job.status == JobStatus.DONE:
                return status_foreground("DONE")
            if job.status == JobStatus.FAILED:
                return status_foreground("FAILED")
            if job.status in {JobStatus.SKIPPED, JobStatus.CANCELLED}:
                return status_foreground(job.status.name)

        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() in {1, 2}:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def job_at(self, row: int) -> Job | None:
        return self.jobs[row] if 0 <= row < len(self.jobs) else None
