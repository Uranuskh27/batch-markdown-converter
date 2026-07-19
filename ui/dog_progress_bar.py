from __future__ import annotations

from math import ceil, pi, sin

from PySide6.QtCore import QPointF, Property, QEasingCurve, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QProgressBar, QWidget

from .theme import theme_colors


class BoneGoalIcon(QWidget):
    """A small original vector bone drawn without an image or emoji asset."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("progressEndpoint")
        self.setFixedSize(34, 44)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        painter.rotate(-32.0)

        bone = QPainterPath()
        bone.addRoundedRect(QRectF(-10.0, -3.5, 20.0, 7.0), 3.0, 3.0)
        for center_x in (-10.0, 10.0):
            bone.addEllipse(QRectF(center_x - 4.5, -8.0, 9.0, 9.0))
            bone.addEllipse(QRectF(center_x - 4.5, -1.0, 9.0, 9.0))

        painter.setPen(QPen(QColor("#8C7658"), 1.4))
        painter.setBrush(QColor("#F2DFC0"))
        painter.drawPath(bone.simplified())


class DogProgressBar(QProgressBar):
    """A progress bar with a side-profile dog that runs toward the goal."""

    DOG_STYLE = "animated-cute-shiba-vector"
    _DOG_WIDTH = 46.0
    _TRACK_HEIGHT = 16.0

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dogProgress")
        self.setTextVisible(True)
        self.setFixedHeight(44)
        self.setMinimumWidth(120)

        self._dog_position = 0.0
        self._animation = QPropertyAnimation(self, b"dogPosition", self)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._gait_phase = 0.0
        self._gait_animation = QPropertyAnimation(self, b"gaitPhase", self)
        self._gait_animation.setEasingCurve(QEasingCurve.Type.Linear)

    def _get_dog_position(self) -> float:
        return self._dog_position

    def _set_dog_position(self, position: float) -> None:
        self._dog_position = min(1.0, max(0.0, float(position)))
        self.update()

    dogPosition = Property(float, _get_dog_position, _set_dog_position)

    def _get_gait_phase(self) -> float:
        return self._gait_phase

    def _set_gait_phase(self, phase: float) -> None:
        self._gait_phase = float(phase)
        self.update()

    gaitPhase = Property(float, _get_gait_phase, _set_gait_phase)

    def dog_position(self) -> float:
        """Return the dog's normalized position for tests and accessibility."""

        return self._dog_position

    def leg_swing(self) -> float:
        """Return the current signed leg swing for animation verification."""

        return sin(self._gait_phase) * 3.5

    def setValue(self, value: int) -> None:  # noqa: N802 - Qt API override
        super().setValue(value)
        target = self._normalized_value(value)
        self._animation.stop()
        self._gait_animation.stop()

        # Hidden widgets and resets should be deterministic. Visible forward
        # progress gets a short run animation proportional to the distance.
        if self.isVisible() and target > self._dog_position:
            distance = target - self._dog_position
            self._animation.setDuration(max(220, min(700, int(220 + 600 * distance))))
            self._animation.setStartValue(self._dog_position)
            self._animation.setEndValue(target)
            cycles = max(1, ceil(distance * 12))
            next_cycle = ceil(self._gait_phase / (2 * pi)) + cycles
            self._gait_animation.setDuration(self._animation.duration())
            self._gait_animation.setStartValue(self._gait_phase)
            self._gait_animation.setEndValue(next_cycle * 2 * pi)
            self._animation.start()
            self._gait_animation.start()
        else:
            self._set_dog_position(target)
            self._set_gait_phase(0.0)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API override
        del event
        application = QApplication.instance()
        theme = (
            str(application.property("batchMarkdownConverterTheme"))
            if application is not None
            else "light"
        )
        colors = theme_colors(theme)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        track_y = self.height() - self._TRACK_HEIGHT - 2.0
        track = QRectF(1.0, track_y, self.width() - 2.0, self._TRACK_HEIGHT)
        radius = self._TRACK_HEIGHT / 2.0

        painter.setPen(QColor(colors.border))
        painter.setBrush(QColor(colors.progress_track))
        painter.drawRoundedRect(track, radius, radius)

        if self._dog_position > 0:
            fill = QRectF(track)
            fill.setWidth(max(self._TRACK_HEIGHT, track.width() * self._dog_position))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(colors.accent))
            painter.drawRoundedRect(fill, radius, radius)

        text = self._display_text()
        text_font = QFont(self.font())
        text_font.setPointSizeF(max(9.0, text_font.pointSizeF() - 1.0))
        text_font.setBold(True)
        painter.setFont(text_font)
        painter.setPen(QColor(colors.text))
        painter.drawText(track, Qt.AlignmentFlag.AlignCenter, text)

        dog_x = (self.width() - self._DOG_WIDTH) * self._dog_position
        self._paint_running_dog(painter, dog_x, colors.accent)

    def _paint_running_dog(self, painter: QPainter, dog_x: float, accent: str) -> None:
        swing = self.leg_swing()
        bounce = -abs(sin(self._gait_phase * 2.0)) * 1.5
        fur = QColor("#E58A35")
        fur_light = QColor("#FFD9A0")
        fur_dark = QColor("#A95725")
        outline = QColor("#713817")

        painter.save()
        painter.translate(dog_x, bounce)

        tail = QPainterPath(QPointF(11.0, 16.0))
        tail.cubicTo(4.0, 16.0, 2.0, 8.0, 7.0, 5.0)
        tail.cubicTo(11.0, 2.5, 14.0, 6.0, 10.0, 8.5)
        tail_pen = QPen(outline, 6.0)
        tail_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(tail_pen)
        painter.drawPath(tail)
        tail_pen.setColor(fur)
        tail_pen.setWidthF(3.8)
        painter.setPen(tail_pen)
        painter.drawPath(tail)

        self._draw_leg(painter, 13.0, -swing, fur_dark)
        self._draw_leg(painter, 27.0, swing, fur_dark)

        back_ear = QPainterPath(QPointF(30.0, 7.0))
        back_ear.lineTo(31.5, 1.0)
        back_ear.lineTo(36.0, 6.5)
        back_ear.closeSubpath()
        painter.setPen(QPen(outline, 1.2))
        painter.setBrush(fur_dark)
        painter.drawPath(back_ear)

        front_ear = QPainterPath(QPointF(34.0, 6.0))
        front_ear.lineTo(37.5, 0.5)
        front_ear.lineTo(40.5, 7.0)
        front_ear.closeSubpath()
        painter.setBrush(fur)
        painter.drawPath(front_ear)

        painter.setPen(QPen(outline, 1.2))
        painter.setBrush(fur)
        painter.drawRoundedRect(QRectF(9.0, 9.0, 26.0, 16.0), 7.0, 7.0)
        painter.drawEllipse(QRectF(28.0, 4.0, 15.0, 17.0))
        painter.setBrush(fur_light)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(14.0, 18.0, 16.0, 6.0), 3.0, 3.0)
        painter.drawEllipse(QRectF(36.0, 10.0, 9.0, 7.0))

        self._draw_leg(painter, 16.0, swing, fur)
        self._draw_leg(painter, 30.0, -swing, fur)

        collar_pen = QPen(QColor(accent), 2.0)
        painter.setPen(collar_pen)
        painter.drawLine(QPointF(29.8, 7.5), QPointF(31.2, 19.0))
        painter.setBrush(QColor(accent))
        painter.drawEllipse(QRectF(30.0, 17.5, 3.0, 3.0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#24160F"))
        painter.drawEllipse(QRectF(35.0, 7.8, 2.4, 2.4))
        painter.drawEllipse(QRectF(43.0, 11.8, 2.8, 2.5))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QRectF(35.5, 8.1, 0.8, 0.8))
        painter.setBrush(QColor("#F59A9A"))
        painter.drawEllipse(QRectF(37.0, 12.4, 3.0, 2.2))

        smile_pen = QPen(outline, 1.0)
        smile_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(smile_pen)
        smile = QPainterPath(QPointF(42.5, 15.2))
        smile.quadTo(41.5, 17.0, 40.2, 15.7)
        painter.drawPath(smile)
        painter.restore()

    @staticmethod
    def _draw_leg(painter: QPainter, hip_x: float, swing: float, color: QColor) -> None:
        knee_x = hip_x + swing * 0.45
        foot_x = hip_x + swing
        leg_pen = QPen(color, 2.8)
        leg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(leg_pen)
        painter.drawLine(QPointF(hip_x, 21.0), QPointF(knee_x, 27.0))
        painter.drawLine(QPointF(knee_x, 27.0), QPointF(foot_x, 33.0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(QRectF(foot_x - 1.7, 31.5, 4.0, 2.8))

    def _normalized_value(self, value: int) -> float:
        span = self.maximum() - self.minimum()
        if span <= 0:
            return 0.0
        return min(1.0, max(0.0, (value - self.minimum()) / span))

    def _display_text(self) -> str:
        percentage = round(self._normalized_value(self.value()) * 100)
        return (
            self.format()
            .replace("%p%", f"{percentage}%")
            .replace("%v", str(self.value()))
            .replace("%m", str(self.maximum()))
        )
