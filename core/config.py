from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QSettings

from .i18n import application_settings_name


class AppSettings:
    def __init__(self) -> None:
        self._settings = QSettings("LocalTools", application_settings_name())

    @property
    def output_mode(self) -> str:
        return str(self._settings.value("output/mode", "source"))

    @output_mode.setter
    def output_mode(self, value: str) -> None:
        self._settings.setValue("output/mode", value)

    @property
    def output_directory(self) -> Path | None:
        value = str(self._settings.value("output/directory", ""))
        return Path(value) if value else None

    @output_directory.setter
    def output_directory(self, value: Path | None) -> None:
        self._settings.setValue("output/directory", str(value) if value else "")

    @property
    def collision_policy(self) -> str:
        return str(self._settings.value("output/collision", "rename"))

    @collision_policy.setter
    def collision_policy(self, value: str) -> None:
        self._settings.setValue("output/collision", value)

    @property
    def open_output_directory(self) -> bool:
        return bool(self._settings.value("output/open_when_finished", False, type=bool))

    @open_output_directory.setter
    def open_output_directory(self, value: bool) -> None:
        self._settings.setValue("output/open_when_finished", bool(value))

    @property
    def concurrency(self) -> int:
        default = min(2, os.cpu_count() or 1)
        return max(1, min(4, int(self._settings.value("jobs/concurrency", default))))

    @concurrency.setter
    def concurrency(self, value: int) -> None:
        self._settings.setValue("jobs/concurrency", max(1, min(4, value)))

    @property
    def timeout_seconds(self) -> int:
        return max(10, int(self._settings.value("jobs/timeout", 120)))

    @timeout_seconds.setter
    def timeout_seconds(self, value: int) -> None:
        self._settings.setValue("jobs/timeout", max(10, value))

    @property
    def max_file_size_mb(self) -> int:
        return max(1, int(self._settings.value("limits/file_size_mb", 200)))

    @property
    def max_scan_files(self) -> int:
        return max(1, int(self._settings.value("limits/scan_files", 10_000)))

    @property
    def theme(self) -> str:
        value = str(self._settings.value("appearance/theme", "light"))
        return value if value in {"light", "dark"} else "light"

    @theme.setter
    def theme(self, value: str) -> None:
        self._settings.setValue("appearance/theme", value if value in {"light", "dark"} else "light")
