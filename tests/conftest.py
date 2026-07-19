from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def keep_qapplication_alive() -> QApplication:
    application = QApplication.instance() or QApplication([])
    yield application
