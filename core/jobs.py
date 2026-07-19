from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4


class JobStatus(str, Enum):
    QUEUED = "대기 중"
    RUNNING = "변환 중"
    DONE = "완료"
    FAILED = "실패"
    SKIPPED = "건너뜀"
    CANCELLED = "취소됨"

    @property
    def finished(self) -> bool:
        return self in {
            JobStatus.DONE,
            JobStatus.FAILED,
            JobStatus.SKIPPED,
            JobStatus.CANCELLED,
        }


@dataclass(slots=True)
class Job:
    src: Path
    size: int
    source_root: Path | None = None
    status: JobStatus = JobStatus.QUEUED
    dst: Path | None = None
    error: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)

    @property
    def display_name(self) -> str:
        return unicodedata.normalize("NFC", self.src.name)

    @property
    def dedupe_key(self) -> str:
        resolved = str(self.src.resolve(strict=False))
        return unicodedata.normalize("NFC", resolved).casefold()


@dataclass(frozen=True, slots=True)
class ScannedFile:
    src: Path
    size: int
    source_root: Path | None = None
    skip_reason: str | None = None
