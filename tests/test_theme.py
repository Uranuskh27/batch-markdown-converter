from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from ui.theme import apply_theme, status_foreground, theme_colors, theme_palette, theme_stylesheet


def contrast_ratio(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_theme_palette_defines_active_and_disabled_control_colors(theme: str) -> None:
    colors = theme_colors(theme)
    palette = theme_palette(theme)

    assert palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Window).name() == colors.window.lower()
    assert palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Base).name() == colors.input.lower()
    assert palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Text).name() == colors.text.lower()
    assert palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Button).name() == colors.surface.lower()
    assert palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base).name() == colors.disabled_background.lower()
    assert palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text).name() == colors.disabled_text.lower()
    assert palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText).name() == colors.disabled_text.lower()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_theme_stylesheet_covers_visible_control_states(theme: str) -> None:
    stylesheet = theme_stylesheet(theme)

    for selector in (
        "QPushButton:hover",
        "QPushButton:pressed",
        "QPushButton:disabled",
        "QComboBox, QSpinBox, QLineEdit",
        "QComboBox:disabled",
        "QCheckBox:disabled",
        "QTableView",
        "QHeaderView::section",
        "QProgressBar#dogProgress",
        "QScrollBar:vertical",
        "QStatusBar",
        "QToolTip",
    ):
        assert selector in stylesheet


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_theme_text_contrast_is_readable(theme: str) -> None:
    colors = theme_colors(theme)

    assert contrast_ratio(colors.text, colors.window) >= 7
    assert contrast_ratio(colors.text, colors.surface) >= 7
    assert contrast_ratio(colors.muted, colors.window) >= 4.5


def test_apply_theme_uses_fusion_and_replaces_the_complete_stylesheet() -> None:
    application = QApplication.instance() or QApplication([])

    apply_theme(application, "dark")
    assert application.property("batchMarkdownConverterBaseStyle") == "Fusion"
    assert theme_colors("dark").input in application.styleSheet()

    apply_theme(application, "light")
    assert theme_colors("light").input in application.styleSheet()
    assert theme_colors("dark").input not in application.styleSheet()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_skipped_status_uses_the_danger_color(theme: str) -> None:
    application = QApplication.instance() or QApplication([])
    apply_theme(application, theme)

    assert status_foreground("SKIPPED").name() == theme_colors(theme).danger.lower()
    assert status_foreground("CANCELLED").name() == theme_colors(theme).muted.lower()
