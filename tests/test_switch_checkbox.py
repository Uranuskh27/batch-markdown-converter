from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QAbstractAnimation
from PySide6.QtWidgets import QApplication

from ui.switch_checkbox import SwitchCheckBox
from ui.theme import apply_theme, theme_colors


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_switch_checkbox_is_visible_and_changes_color(theme: str) -> None:
    application = QApplication.instance() or QApplication([])
    apply_theme(application, theme)
    switch = SwitchCheckBox("Open output folder")
    switch.resize(switch.sizeHint())

    unchecked = switch.grab().toImage().pixelColor(10, switch.height() // 2).name()
    switch.click()
    checked = switch.grab().toImage().pixelColor(10, switch.height() // 2).name()

    assert unchecked != checked
    assert checked == theme_colors(theme).accent.lower()
    switch.close()

    apply_theme(application, "light")


def test_visible_switch_animates_its_knob_between_modes() -> None:
    switch = SwitchCheckBox("Dark Mode")
    switch.resize(switch.sizeHint())
    switch.show()

    switch.click()

    assert switch.isChecked()
    assert switch._knob_animation.state() == QAbstractAnimation.State.Running
    assert switch._knob_animation.endValue() == pytest.approx(1.0)
    assert switch._knob_animation.duration() == 160
    switch.hide()
