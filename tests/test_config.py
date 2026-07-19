from __future__ import annotations

import core.config as config_module
from core.config import AppSettings


class MemorySettings:
    def __init__(self, *_args) -> None:
        self.values: dict[str, object] = {}

    def value(self, key: str, default=None, type=None):
        value = self.values.get(key, default)
        return type(value) if type is not None else value

    def setValue(self, key: str, value: object) -> None:
        self.values[key] = value


def test_open_output_directory_defaults_off_and_persists(monkeypatch) -> None:
    monkeypatch.setattr(config_module, "QSettings", MemorySettings)
    settings = AppSettings()

    assert settings.open_output_directory is False

    settings.open_output_directory = True
    assert settings.open_output_directory is True

    settings.open_output_directory = False
    assert settings.open_output_directory is False
