from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from .jobs import ScannedFile
from .i18n import tr


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".xml",
    ".epub",
    ".txt",
    ".rtf",
    ".msg",
    ".zip",
}

SKIPPED_PACKAGES = {
    ".app",
    ".framework",
    ".bundle",
    ".plugin",
    ".xcodeproj",
    ".xcworkspace",
}


class Scanner(QObject):
    batch_found = Signal(list)
    notice = Signal(str)
    finished = Signal()

    def __init__(
        self,
        paths: list[Path],
        *,
        max_files: int = 10_000,
        max_file_size_mb: int = 200,
        batch_size: int = 200,
    ) -> None:
        super().__init__()
        self.paths = paths
        self.max_files = max_files
        self.max_size = max_file_size_mb * 1024 * 1024
        self.batch_size = batch_size
        self._cancelled = False

    @Slot()
    def cancel(self) -> None:
        self._cancelled = True

    @Slot()
    def run(self) -> None:
        batch: list[ScannedFile] = []
        count = 0

        try:
            for dropped_path in self.paths:
                if self._cancelled or count >= self.max_files:
                    break

                for scanned in self._scan_dropped_path(dropped_path):
                    if self._cancelled:
                        break
                    batch.append(scanned)
                    count += 1

                    if len(batch) >= self.batch_size:
                        self.batch_found.emit(batch)
                        batch = []

                    if count >= self.max_files:
                        self.notice.emit(
                            tr(
                                f"파일 수 상한 {self.max_files:,}개에 도달해 스캔을 중단했습니다.",
                                f"Stopped scanning after reaching the {self.max_files:,}-file limit.",
                            )
                        )
                        break

            if batch:
                self.batch_found.emit(batch)
        finally:
            self.finished.emit()

    def _scan_dropped_path(self, path: Path):
        if not path.exists():
            yield ScannedFile(
                path,
                0,
                skip_reason=tr("파일을 찾을 수 없음", "File not found"),
            )
            return

        if path.is_file():
            yield self._inspect_file(path, None)
            return

        if path.suffix.lower() in SKIPPED_PACKAGES:
            yield ScannedFile(
                path,
                0,
                skip_reason=tr(
                    "macOS 패키지는 탐색하지 않음",
                    "macOS packages are not scanned",
                ),
            )
            return

        root = path

        def on_error(error: OSError) -> None:
            self.notice.emit(
                tr(
                    f"폴더를 읽을 수 없습니다: {error.filename or path}",
                    f"Cannot read folder: {error.filename or path}",
                )
            )

        for current, directories, filenames in os.walk(
            path, topdown=True, followlinks=False, onerror=on_error
        ):
            if self._cancelled:
                return

            directories[:] = [
                name
                for name in directories
                if not name.startswith(".")
                and Path(name).suffix.lower() not in SKIPPED_PACKAGES
                and not (Path(current) / name).is_symlink()
            ]

            for filename in filenames:
                if filename.startswith(".") or filename.startswith("._"):
                    continue
                file_path = Path(current) / filename
                yield self._inspect_file(file_path, root)

    def _inspect_file(self, path: Path, source_root: Path | None) -> ScannedFile:
        try:
            size = path.stat().st_size
        except OSError as error:
            return ScannedFile(
                path,
                0,
                source_root,
                tr(f"파일을 읽을 수 없음: {error}", f"Cannot read file: {error}"),
            )

        suffix = path.suffix.lower()
        if suffix == ".md":
            return ScannedFile(
                path,
                size,
                source_root,
                tr("Markdown 원본은 제외", "Markdown source files are excluded"),
            )
        if suffix not in SUPPORTED_EXTENSIONS:
            return ScannedFile(
                path,
                size,
                source_root,
                tr("지원하지 않는 형식", "Unsupported file type"),
            )
        if size == 0:
            return ScannedFile(
                path,
                size,
                source_root,
                tr("0바이트 파일", "Empty file"),
            )
        if size > self.max_size:
            return ScannedFile(
                path,
                size,
                source_root,
                tr(
                    f"파일 크기 상한 {self.max_size // 1024 // 1024}MB 초과",
                    f"Exceeds the {self.max_size // 1024 // 1024}MB file size limit",
                ),
            )
        return ScannedFile(path, size, source_root)
