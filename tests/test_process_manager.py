import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from core.jobs import JobStatus, ScannedFile
from core.process_manager import JobManager


class TestSettings:
    output_mode = "source"
    output_directory = None
    collision_policy = "rename"
    concurrency = 2
    timeout_seconds = 30


def test_process_manager_runs_isolated_worker(tmp_path: Path) -> None:
    application = QApplication.instance() or QApplication([])
    source = tmp_path / "프로세스 테스트.txt"
    source.write_text("격리된 Worker 변환", encoding="utf-8")
    app_script = Path(__file__).parents[1] / "app.py"
    manager = JobManager(TestSettings(), app_script)
    manager.add_scanned([ScannedFile(source, source.stat().st_size)])

    loop = QEventLoop()
    manager.batch_finished.connect(lambda _done, _failed: loop.quit())
    QTimer.singleShot(60_000, loop.quit)
    manager.start_all()
    loop.exec()

    assert len(manager.jobs) == 1
    assert manager.jobs[0].status == JobStatus.DONE
    assert manager.jobs[0].dst is not None
    assert manager.jobs[0].dst.exists()
    assert "격리된 Worker" in manager.jobs[0].dst.read_text(encoding="utf-8")
    assert application is not None
