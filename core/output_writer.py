from __future__ import annotations

import os
import tempfile
import unicodedata
from pathlib import Path

from .i18n import tr


class OutputCollisionError(FileExistsError):
    pass


class OutputPlanner:
    def __init__(self) -> None:
        self._reserved: set[str] = set()

    def clear(self) -> None:
        self._reserved.clear()

    def release(self, path: Path | None) -> None:
        if path is not None:
            self._reserved.discard(self._key(path))

    def reserve(
        self,
        src: Path,
        *,
        output_mode: str,
        output_directory: Path | None,
        source_root: Path | None,
        collision_policy: str,
    ) -> Path:
        candidate = self._base_candidate(
            src,
            output_mode=output_mode,
            output_directory=output_directory,
            source_root=source_root,
        )

        if collision_policy == "overwrite":
            if self._key(candidate) in self._reserved:
                candidate = self._renamed_candidate(candidate)
        elif collision_policy == "skip":
            if candidate.exists() or self._key(candidate) in self._reserved:
                raise OutputCollisionError(
                    tr(
                        f"결과 파일이 이미 존재함: {candidate.name}",
                        f"Output file already exists: {candidate.name}",
                    )
                )
        else:
            if candidate.exists() or self._key(candidate) in self._reserved:
                candidate = self._renamed_candidate(candidate)

        self._reserved.add(self._key(candidate))
        return candidate

    def _base_candidate(
        self,
        src: Path,
        *,
        output_mode: str,
        output_directory: Path | None,
        source_root: Path | None,
    ) -> Path:
        if output_mode != "directory" or output_directory is None:
            return src.with_suffix(".md")

        if source_root is not None:
            try:
                relative = src.relative_to(source_root.parent)
            except ValueError:
                relative = Path(src.name)
            return (output_directory / relative).with_suffix(".md")

        return (output_directory / src.name).with_suffix(".md")

    def _renamed_candidate(self, candidate: Path) -> Path:
        number = 1
        while True:
            renamed = candidate.with_name(f"{candidate.stem} ({number}){candidate.suffix}")
            if not renamed.exists() and self._key(renamed) not in self._reserved:
                return renamed
            number += 1

    @staticmethod
    def _key(path: Path) -> str:
        resolved = os.path.normcase(str(path.resolve(strict=False)))
        return unicodedata.normalize("NFC", resolved).casefold()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            output.write(text)
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
