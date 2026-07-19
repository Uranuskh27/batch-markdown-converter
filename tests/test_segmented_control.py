from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from ui.segmented_control import SegmentedControl
from ui.theme import apply_theme


def test_segmented_control_exposes_both_choices_without_dropdown() -> None:
    control = SegmentedControl([("Next to Source", "source"), ("Choose Folder", "directory")])
    selected: list[str] = []
    control.selection_changed.connect(selected.append)

    assert control.current_data() == "source"
    control.button_for_data("directory").click()

    assert control.current_data() == "directory"
    assert selected == ["directory"]
    assert control.button_for_data("directory").isChecked()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_segmented_control_renders_in_both_themes(theme: str) -> None:
    application = QApplication.instance() or QApplication([])
    apply_theme(application, theme)
    control = SegmentedControl([("Source", "source"), ("Folder", "directory")])
    control.resize(control.sizeHint())

    rendered = control.grab().toImage()

    assert not rendered.isNull()
    assert control.button_for_data("source").isChecked()
