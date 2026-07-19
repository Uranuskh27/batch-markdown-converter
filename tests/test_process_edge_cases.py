from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from core.jobs import JobStatus, ScannedFile
import core.process_manager as process_manager_module
from core.process_manager import JobManager


class MutableSettings:
    output_mode = "source"
    output_directory = None
    collision_policy = "rename"
    concurrency = 2
    timeout_seconds = 30
    max_file_size_mb = 200
    max_scan_files = 10_000


def wait_for(predicate, timeout_ms: int = 15_000) -> bool:
    if predicate():
        return True
    loop = QEventLoop()
    poll = QTimer()
    poll.setInterval(20)
    timeout = QTimer()
    timeout.setSingleShot(True)

    def check() -> None:
        if predicate():
            loop.quit()

    poll.timeout.connect(check)
    timeout.timeout.connect(loop.quit)
    poll.start()
    timeout.start(timeout_ms)
    loop.exec()
    poll.stop()
    timeout.stop()
    return bool(predicate())


def application() -> QApplication:
    return QApplication.instance() or QApplication([])


def fake_worker() -> Path:
    return Path(__file__).parent / "helpers" / "fake_worker.py"


def add_source(manager: JobManager, path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    manager.add_scanned([ScannedFile(path, path.stat().st_size)])


def test_failed_worker_does_not_stop_other_jobs(tmp_path: Path) -> None:
    _application = application()
    settings = MutableSettings()
    manager = JobManager(settings, fake_worker())
    add_source(manager, tmp_path / "bad.txt", "fail")
    add_source(manager, tmp_path / "good.txt", "success")

    manager.start_all()
    assert wait_for(lambda: not manager.is_processing)

    by_name = {job.src.name: job for job in manager.jobs}
    assert by_name["bad.txt"].status == JobStatus.FAILED
    assert by_name["bad.txt"].error == "의도된 Worker 실패"
    assert by_name["good.txt"].status == JobStatus.DONE


def test_timeout_kills_worker_and_records_reason(tmp_path: Path) -> None:
    _application = application()
    settings = MutableSettings()
    settings.timeout_seconds = 1
    settings.concurrency = 1
    manager = JobManager(settings, fake_worker())
    add_source(manager, tmp_path / "slow.txt", "sleep")

    manager.start_all()
    assert wait_for(lambda: not manager.is_processing, 5_000)

    job = manager.jobs[0]
    assert job.status == JobStatus.FAILED
    assert job.error == "1초 제한 시간을 초과했습니다."


def test_cancel_marks_running_and_queued_jobs(tmp_path: Path) -> None:
    _application = application()
    settings = MutableSettings()
    settings.concurrency = 1
    manager = JobManager(settings, fake_worker())
    add_source(manager, tmp_path / "running.txt", "sleep")
    add_source(manager, tmp_path / "queued.txt", "success")

    manager.start_all()
    QTimer.singleShot(100, manager.cancel_all)
    assert wait_for(lambda: all(job.status.finished for job in manager.jobs), 5_000)

    assert [job.status for job in manager.jobs] == [
        JobStatus.CANCELLED,
        JobStatus.CANCELLED,
    ]


def test_retry_failed_job_succeeds(tmp_path: Path) -> None:
    _application = application()
    settings = MutableSettings()
    manager = JobManager(settings, fake_worker())
    source = tmp_path / "retry.txt"
    add_source(manager, source, "fail")
    manager.start_all()
    assert wait_for(lambda: not manager.is_processing)
    assert manager.jobs[0].status == JobStatus.FAILED

    source.write_text("recovered", encoding="utf-8")
    manager.retry_failed()
    assert wait_for(lambda: not manager.is_processing)
    assert manager.jobs[0].status == JobStatus.DONE
    assert manager.jobs[0].dst.read_text(encoding="utf-8") == "recovered"


def test_worker_start_failure_is_cleaned_up(monkeypatch, tmp_path: Path) -> None:
    _application = application()
    settings = MutableSettings()
    manager = JobManager(settings, fake_worker())
    add_source(manager, tmp_path / "unstartable.txt", "success")
    monkeypatch.setattr(
        process_manager_module.sys,
        "executable",
        str(tmp_path / "missing-python-executable"),
    )

    manager.start_all()

    assert wait_for(lambda: not manager.is_processing, 5_000)
    assert manager.jobs[0].status == JobStatus.FAILED
    assert manager.jobs[0].error == "변환 Worker를 시작할 수 없습니다."
    assert manager._running == {}


def test_missing_output_directory_blocks_start(tmp_path: Path) -> None:
    _application = application()
    settings = MutableSettings()
    settings.output_mode = "directory"
    settings.output_directory = None
    manager = JobManager(settings, fake_worker())
    add_source(manager, tmp_path / "source.txt", "success")
    notices: list[str] = []
    manager.notice.connect(notices.append)

    manager.start_all()

    assert manager.jobs[0].status == JobStatus.QUEUED
    assert notices == ["결과 저장 폴더를 먼저 선택하세요."]


def test_nfc_and_nfd_paths_are_deduplicated(tmp_path: Path) -> None:
    _application = application()
    manager = JobManager(MutableSettings(), fake_worker())
    composed = tmp_path / "café.txt"
    decomposed = tmp_path / "cafe\u0301.txt"

    manager.add_scanned([ScannedFile(composed, 1), ScannedFile(decomposed, 1)])

    assert len(manager.jobs) == 1
