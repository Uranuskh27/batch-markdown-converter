from __future__ import annotations

import pytest
from PySide6.QtCore import QAbstractAnimation
from PySide6.QtWidgets import QApplication

from ui.theme import apply_theme
from ui.theme_switch import ThemeSwitch


@pytest.mark.parametrize("theme, checked", [("light", False), ("dark", True)])
def test_theme_switch_renders_icons_without_text(theme: str, checked: bool) -> None:
    application = QApplication.instance() or QApplication([])
    apply_theme(application, theme)
    switch = ThemeSwitch()
    switch.setChecked(checked)

    rendered = switch.grab().toImage()

    assert switch.text() == ""
    assert switch.size().width() == 60
    assert not rendered.isNull()
    assert switch.knob_position() == pytest.approx(1.0 if checked else 0.0)


def test_visible_theme_switch_slides_between_sun_and_moon() -> None:
    switch = ThemeSwitch()
    switch.show()

    switch.click()

    assert switch.isChecked()
    assert switch._animation.state() == QAbstractAnimation.State.Running
    assert switch._animation.endValue() == pytest.approx(1.0)
    assert switch._animation.duration() == 180
    switch.hide()
