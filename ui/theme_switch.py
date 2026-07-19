from __future__ import annotations

from PySide6.QtCore import QPointF, Property, QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, Slot
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QAbstractButton, QApplication

from .theme import theme_colors


class ThemeSwitch(QAbstractButton):
    """Compact theme switch with vector sun and moon icons inside the track."""

    TRACK_WIDTH = 60
    TRACK_HEIGHT = 30
    KNOB_SIZE = 24
    MARGIN = 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(self.TRACK_WIDTH, self.TRACK_HEIGHT)
        self._knob_position = 0.0
        self._animation = QPropertyAnimation(self, b"knobPosition", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate_knob)

    def sizeHint(self) -> QSize:
        return QSize(self.TRACK_WIDTH, self.TRACK_HEIGHT)

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
        self._animation.stop()
        if self.isVisible():
            self._animation.setStartValue(self._knob_position)
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self._set_knob_position(target)

    def paintEvent(self, _event: QPaintEvent) -> None:
        application = QApplication.instance()
        theme = application.property("batchMarkdownConverterTheme") if application is not None else "light"
        colors = theme_colors("dark" if theme == "dark" else "light")
        enabled = self.isEnabled()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(0.5, 0.5, self.TRACK_WIDTH - 1.0, self.TRACK_HEIGHT - 1.0)
        track_color = colors.selection if not self.isChecked() else colors.selection
        if not enabled:
            track_color = colors.disabled_background
        painter.setPen(QPen(QColor(colors.border), 1.0))
        painter.setBrush(QColor(track_color))
        painter.drawRoundedRect(track, self.TRACK_HEIGHT / 2, self.TRACK_HEIGHT / 2)

        icon_muted = QColor(colors.muted if enabled else colors.disabled_text)
        if self.isChecked():
            self._draw_sun(painter, QPointF(15.0, 15.0), icon_muted)
        else:
            self._draw_moon(painter, QPointF(45.0, 15.0), icon_muted)

        travel = self.TRACK_WIDTH - self.KNOB_SIZE - self.MARGIN * 2
        knob_x = self.MARGIN + travel * self._knob_position
        knob = QRectF(knob_x, self.MARGIN, self.KNOB_SIZE, self.KNOB_SIZE)
        painter.setPen(QPen(QColor(colors.border), 0.8))
        painter.setBrush(QColor("#FFFFFF" if enabled else colors.disabled_background))
        painter.drawEllipse(knob)

        center = knob.center()
        if self.isChecked():
            self._draw_moon(painter, center, QColor("#415A77"))
        else:
            self._draw_sun(painter, center, QColor("#F59E0B"))

        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(colors.accent), 1.0, Qt.PenStyle.DotLine))
            painter.drawRoundedRect(track.adjusted(1.0, 1.0, -1.0, -1.0), 13.0, 13.0)

    @staticmethod
    def _draw_sun(painter: QPainter, center: QPointF, color: QColor) -> None:
        pen = QPen(color, 1.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawEllipse(center, 3.2, 3.2)
        for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0), (-5, -5), (5, 5), (-5, 5), (5, -5)):
            length = (dx * dx + dy * dy) ** 0.5
            inner = QPointF(center.x() + dx * 0.72, center.y() + dy * 0.72)
            outer = QPointF(center.x() + dx, center.y() + dy)
            if length:
                painter.drawLine(inner, outer)

    @staticmethod
    def _draw_moon(painter: QPainter, center: QPointF, color: QColor) -> None:
        moon = QPainterPath()
        moon.addEllipse(center, 6.0, 6.0)
        cutout = QPainterPath()
        cutout.addEllipse(QPointF(center.x() + 3.0, center.y() - 2.0), 5.7, 5.7)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPath(moon.subtracted(cutout))
