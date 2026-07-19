from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget


class SegmentedControl(QWidget):
    """An exclusive, always-visible alternative to a two-item dropdown."""

    selection_changed = Signal(str)

    def __init__(
        self,
        items: Iterable[tuple[str, str]],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("segmentedControl")
        self._buttons: dict[str, QPushButton] = {}
        self._data_by_id: dict[int, str] = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        materialized = list(items)
        for index, (label, data) in enumerate(materialized):
            button = QPushButton(label, self)
            button.setCheckable(True)
            button.setProperty("segmented", True)
            button.setProperty(
                "segmentPosition",
                "left" if index == 0 else "right" if index == len(materialized) - 1 else "middle",
            )
            self._buttons[data] = button
            self._data_by_id[index] = data
            self._group.addButton(button, index)
            layout.addWidget(button)

        self._group.idClicked.connect(self._clicked)
        if materialized:
            self._buttons[materialized[0][1]].setChecked(True)

    def current_data(self) -> str | None:
        return self._data_by_id.get(self._group.checkedId())

    def set_current_data(self, data: str) -> None:
        button = self._buttons.get(data)
        if button is None or button.isChecked():
            return
        button.setChecked(True)
        self.selection_changed.emit(data)

    def button_for_data(self, data: str) -> QPushButton:
        return self._buttons[data]

    def _clicked(self, button_id: int) -> None:
        data = self._data_by_id.get(button_id)
        if data is not None:
            self.selection_changed.emit(data)
