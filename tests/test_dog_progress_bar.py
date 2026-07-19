from __future__ import annotations

import pytest
from PySide6.QtCore import QAbstractAnimation
from PySide6.QtWidgets import QApplication

from ui.dog_progress_bar import BoneGoalIcon, DogProgressBar
from ui.theme import apply_theme


def test_hidden_dog_tracks_progress_position_exactly() -> None:
    progress = DogProgressBar()
    progress.setRange(0, 100)

    progress.setValue(0)
    assert progress.dog_position() == pytest.approx(0.0)
    progress.setValue(37)
    assert progress.dog_position() == pytest.approx(0.37)
    progress.setValue(100)
    assert progress.dog_position() == pytest.approx(1.0)
    progress.setValue(0)
    assert progress.dog_position() == pytest.approx(0.0)


def test_visible_forward_progress_starts_running_animation() -> None:
    progress = DogProgressBar()
    progress.setRange(0, 100)
    progress.setValue(0)
    progress.show()

    progress.setValue(60)

    assert progress._animation.state() == QAbstractAnimation.State.Running
    assert progress._gait_animation.state() == QAbstractAnimation.State.Running
    assert progress._animation.endValue() == pytest.approx(0.6)
    assert 220 <= progress._animation.duration() <= 700
    gait_cycles = round(progress._gait_animation.endValue() / (2 * 3.141592653589793))
    progress._gait_animation.setCurrentTime(
        max(1, progress._gait_animation.duration() // (gait_cycles * 4))
    )
    assert abs(progress.leg_swing()) >= 3.3
    progress.hide()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_dog_progress_renders_in_both_themes(theme: str) -> None:
    application = QApplication.instance() or QApplication([])
    apply_theme(application, theme)
    progress = DogProgressBar()
    progress.resize(360, 36)
    progress.setRange(0, 100)
    progress.setFormat("1/2 · %p%")
    progress.setValue(50)

    rendered = progress.grab().toImage()

    assert not rendered.isNull()
    assert rendered.width() == 360
    assert progress._display_text() == "1/2 · 50%"


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_original_vector_bone_renders_without_an_image_asset(theme: str) -> None:
    application = QApplication.instance() or QApplication([])
    apply_theme(application, theme)
    bone = BoneGoalIcon()

    rendered = bone.grab().toImage()

    assert not rendered.isNull()
    assert rendered.width() == 34
    assert rendered.height() == 44
