from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QSize, Qt, Slot
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QApplication, QCheckBox

from .theme import theme_colors


class SwitchCheckBox(QCheckBox):
    TRACK_WIDTH = 38
    TRACK_HEIGHT = 20
    KNOB_SIZE = 16
    TEXT_GAP = 8

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._knob_position = 1.0 if self.isChecked() else 0.0
        self._knob_animation = QPropertyAnimation(self, b"knobPosition", self)
        self._knob_animation.setDuration(160)
        self._knob_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate_knob)

    def _get_knob_position(self) -> float:
        return self._knob_position

    def _set_knob_position(self, position: float) -> None:
        self._knob_position = min(1.0, max(0.0, float(position)))
        self.update()

    knobPosition = Property(float, _get_knob_position, _set_knob_position)

    def knob_position(self) -> float:
        return self._knob_position

    @Slot(bool)
    def _animate_knob(self, checked: bool) -> None:
        target = 1.0 if checked else 0.0
        self._knob_animation.stop()
        if self.isVisible():
            self._knob_animation.setStartValue(self._knob_position)
            self._knob_animation.setEndValue(target)
            self._knob_animation.start()
        else:
            self._set_knob_position(target)

    def sizeHint(self) -> QSize:
        base = super().sizeHint()
        text_width = self.fontMetrics().horizontalAdvance(self.text())
        return QSize(
            max(base.width(), self.TRACK_WIDTH + self.TEXT_GAP + text_width),
            max(base.height(), self.TRACK_HEIGHT + 4),
        )

    def paintEvent(self, _event: QPaintEvent) -> None:
        application = QApplication.instance()
        theme = application.property("batchMarkdownConverterTheme") if application is not None else "light"
        colors = theme_colors("dark" if theme == "dark" else "light")
        enabled = self.isEnabled()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track_y = (self.height() - self.TRACK_HEIGHT) // 2
        track_color = (
            colors.accent
            if self.isChecked() and enabled
            else colors.disabled_background
            if not enabled
            else colors.surface_alt
        )
        border_color = colors.accent if self.isChecked() and enabled else colors.border
        painter.setPen(QPen(QColor(border_color), 1))
        painter.setBrush(QColor(track_color))
        painter.drawRoundedRect(
            0,
            track_y,
            self.TRACK_WIDTH,
            self.TRACK_HEIGHT,
            self.TRACK_HEIGHT / 2,
            self.TRACK_HEIGHT / 2,
        )

        knob_travel = self.TRACK_WIDTH - self.KNOB_SIZE - 4
        knob_x = 2 + round(knob_travel * self._knob_position)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FFFFFF" if enabled else colors.disabled_text))
        painter.drawEllipse(knob_x, track_y + 2, self.KNOB_SIZE, self.KNOB_SIZE)

        text_color = colors.text if enabled else colors.disabled_text
        painter.setPen(QColor(text_color))
        text_x = self.TRACK_WIDTH + self.TEXT_GAP
        painter.drawText(
            text_x,
            0,
            max(0, self.width() - text_x),
            self.height(),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.text(),
        )

        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(colors.accent), 1, Qt.PenStyle.DotLine))
            painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 4, 4)
