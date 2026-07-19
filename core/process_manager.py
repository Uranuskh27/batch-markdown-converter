from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from .config import AppSettings
from .jobs import Job, JobStatus, ScannedFile
from .i18n import tr
from .output_writer import OutputCollisionError, OutputPlanner


@dataclass(slots=True)
class RunningProcess:
    process: QProcess
    timer: QTimer


class JobManager(QObject):
    jobs_changed = Signal()
    summary_changed = Signal()
    notice = Signal(str)
    batch_finished = Signal(int, int)

    def __init__(self, settings: AppSettings, app_script: Path) -> None:
        super().__init__()
        self.settings = settings
        self.app_script = app_script
        self.jobs: list[Job] = []
        self._running: dict[object, RunningProcess] = {}
        self._cancel_requested: set[object] = set()
        self._planner = OutputPlanner()
        self._processing = False

    @property
    def is_processing(self) -> bool:
        return self._processing or bool(self._running)

    def add_scanned(self, scanned_files: list[ScannedFile]) -> None:
        by_key = {job.dedupe_key: job for job in self.jobs}
        changed = False

        for scanned in scanned_files:
            incoming = Job(
                src=scanned.src,
                size=scanned.size,
                source_root=scanned.source_root,
                status=JobStatus.SKIPPED if scanned.skip_reason else JobStatus.QUEUED,
                error=scanned.skip_reason,
            )
            existing = by_key.get(incoming.dedupe_key)

            if existing is None:
                self.jobs.append(incoming)
                by_key[incoming.dedupe_key] = incoming
                changed = True
                continue

            if existing.status.finished and scanned.skip_reason is None:
                self._planner.release(existing.dst)
                existing.status = JobStatus.QUEUED
                existing.dst = None
                existing.error = None
                existing.started_at = None
                existing.ended_at = None
                changed = True

        if changed:
            self.jobs_changed.emit()
            self.summary_changed.emit()
            if self._processing:
                self._dispatch()

    def start_all(self) -> None:
        if not any(job.status == JobStatus.QUEUED for job in self.jobs):
            self.notice.emit(
                tr("변환할 대기 파일이 없습니다.", "There are no queued files to convert.")
            )
            return

        if not self._prepare_output_directory():
            return

        self._processing = True
        self._dispatch()

    def cancel_all(self) -> None:
        for job in self.jobs:
            if job.status == JobStatus.QUEUED:
                job.status = JobStatus.CANCELLED
                job.ended_at = datetime.now()

        for job_id, running in list(self._running.items()):
            self._cancel_requested.add(job_id)
            running.process.kill()

        self._processing = False
        self.jobs_changed.emit()
        self.summary_changed.emit()

    def retry_failed(self) -> None:
        retried = False
        for job in self.jobs:
            if job.status in {JobStatus.FAILED, JobStatus.CANCELLED}:
                self._planner.release(job.dst)
                job.status = JobStatus.QUEUED
                job.dst = None
                job.error = None
                job.started_at = None
                job.ended_at = None
                retried = True

        if retried:
            self.jobs_changed.emit()
            self.summary_changed.emit()
            self.start_all()
        else:
            self.notice.emit(
                tr("재시도할 실패 항목이 없습니다.", "There are no failed items to retry.")
            )

    def clear_finished(self) -> None:
        if self.is_processing:
            removable = {JobStatus.DONE, JobStatus.FAILED, JobStatus.SKIPPED, JobStatus.CANCELLED}
            self.jobs[:] = [job for job in self.jobs if job.status not in removable]
        else:
            self.jobs.clear()
            self._planner.clear()
        self.jobs_changed.emit()
        self.summary_changed.emit()

    def _dispatch(self) -> None:
        while len(self._running) < self.settings.concurrency:
            job = next((item for item in self.jobs if item.status == JobStatus.QUEUED), None)
            if job is None:
                break
            self._start_job(job)

        if self._processing and not self._running and not any(
            job.status == JobStatus.QUEUED for job in self.jobs
        ):
            self._processing = False
            completed = sum(job.status == JobStatus.DONE for job in self.jobs)
            failed = sum(job.status == JobStatus.FAILED for job in self.jobs)
            self.batch_finished.emit(completed, failed)

    def _start_job(self, job: Job) -> None:
        try:
            job.dst = self._planner.reserve(
                job.src,
                output_mode=self.settings.output_mode,
                output_directory=self.settings.output_directory,
                source_root=job.source_root,
                collision_policy=self.settings.collision_policy,
            )
        except OutputCollisionError as error:
            job.status = JobStatus.SKIPPED
            job.error = str(error)
            job.ended_at = datetime.now()
            self.jobs_changed.emit()
            self.summary_changed.emit()
            return

        job.status = JobStatus.RUNNING
        job.error = None
        job.started_at = datetime.now()

        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        timer = QTimer(process)
        timer.setSingleShot(True)

        if getattr(sys, "frozen", False):
            program = sys.executable
            arguments = ["--worker", str(job.src), str(job.dst)]
        else:
            program = sys.executable
            arguments = [str(self.app_script), "--worker", str(job.src), str(job.dst)]

        job_id = job.id
        process.finished.connect(
            lambda exit_code, exit_status, current_id=job_id: self._process_finished(
                current_id, exit_code, exit_status
            )
        )
        process.errorOccurred.connect(
            lambda error, current_id=job_id: self._process_error(current_id, error)
        )
        timer.timeout.connect(lambda current_id=job_id: self._process_timeout(current_id))

        self._running[job_id] = RunningProcess(process, timer)
        process.start(program, arguments)
        timer.start(self.settings.timeout_seconds * 1000)
        self.jobs_changed.emit()
        self.summary_changed.emit()

    def _process_finished(
        self,
        job_id: object,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:
        running = self._running.pop(job_id, None)
        job = self._job_by_id(job_id)
        if running is None or job is None:
            return

        running.timer.stop()
        output = bytes(running.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        payload = self._last_json_object(output)

        if job_id in self._cancel_requested:
            self._cancel_requested.discard(job_id)
            job.status = JobStatus.CANCELLED
            job.error = tr(
                "사용자가 변환을 취소했습니다.",
                "Conversion was cancelled by the user.",
            )
            self._planner.release(job.dst)
        elif exit_code == 0 and job.dst is not None and job.dst.exists():
            job.status = JobStatus.DONE
            job.error = None
        else:
            job.status = JobStatus.FAILED
            job.error = str(
                payload.get("error")
                or job.error
                or output.strip()
                or tr("변환 프로세스 실패", "Conversion process failed")
            )
            self._planner.release(job.dst)

        job.ended_at = datetime.now()
        running.process.deleteLater()
        self.jobs_changed.emit()
        self.summary_changed.emit()
        QTimer.singleShot(0, self._dispatch)

    def _process_error(self, job_id: object, error: QProcess.ProcessError) -> None:
        if error != QProcess.ProcessError.FailedToStart:
            return
        running = self._running.pop(job_id, None)
        job = self._job_by_id(job_id)
        if running is None or job is None:
            return

        running.timer.stop()
        job.status = JobStatus.FAILED
        job.error = tr(
            "변환 Worker를 시작할 수 없습니다.",
            "Could not start the conversion worker.",
        )
        job.ended_at = datetime.now()
        self._planner.release(job.dst)
        running.process.deleteLater()
        self.jobs_changed.emit()
        self.summary_changed.emit()
        QTimer.singleShot(0, self._dispatch)

    def _process_timeout(self, job_id: object) -> None:
        running = self._running.get(job_id)
        job = self._job_by_id(job_id)
        if running is None or job is None:
            return
        job.error = tr(
            f"{self.settings.timeout_seconds}초 제한 시간을 초과했습니다.",
            f"Exceeded the {self.settings.timeout_seconds}-second time limit.",
        )
        running.process.kill()

    def _prepare_output_directory(self) -> bool:
        if self.settings.output_mode != "directory":
            return True
        directory = self.settings.output_directory
        if directory is None:
            self.notice.emit(
                tr("결과 저장 폴더를 먼저 선택하세요.", "Choose an output folder first.")
            )
            return False
        try:
            directory.mkdir(parents=True, exist_ok=True)
            probe = directory / f".batch-markdown-converter-write-test-{os.getpid()}"
            probe.write_text("test", encoding="utf-8")
            probe.unlink()
        except OSError as error:
            self.notice.emit(
                tr(
                    f"결과 폴더에 쓸 수 없습니다: {error}",
                    f"Cannot write to the output folder: {error}",
                )
            )
            return False
        return True

    def _job_by_id(self, job_id: object) -> Job | None:
        return next((job for job in self.jobs if job.id == job_id), None)

    @staticmethod
    def _last_json_object(output: str) -> dict[str, object]:
        for line in reversed(output.splitlines()):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
        return {}
