from pathlib import Path
import os

import pytest

from core.output_writer import OutputCollisionError, OutputPlanner, atomic_write_text


def test_automatic_rename_reserves_batch_paths(tmp_path: Path) -> None:
    planner = OutputPlanner()
    first = tmp_path / "report.pdf"
    second = tmp_path / "report.docx"
    first.write_bytes(b"pdf")
    second.write_bytes(b"docx")

    first_output = planner.reserve(
        first,
        output_mode="source",
        output_directory=None,
        source_root=None,
        collision_policy="rename",
    )
    second_output = planner.reserve(
        second,
        output_mode="source",
        output_directory=None,
        source_root=None,
        collision_policy="rename",
    )

    assert first_output.name == "report.md"
    assert second_output.name == "report (1).md"


def test_skip_collision_policy(tmp_path: Path) -> None:
    source = tmp_path / "report.pdf"
    source.write_bytes(b"pdf")
    source.with_suffix(".md").write_text("existing", encoding="utf-8")
    planner = OutputPlanner()

    with pytest.raises(OutputCollisionError):
        planner.reserve(
            source,
            output_mode="source",
            output_directory=None,
            source_root=None,
            collision_policy="skip",
        )


def test_directory_mode_preserves_dropped_root(tmp_path: Path) -> None:
    planner = OutputPlanner()
    root = tmp_path / "documents"
    source = root / "nested" / "report.pdf"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"pdf")
    output_root = tmp_path / "markdown"

    output = planner.reserve(
        source,
        output_mode="directory",
        output_directory=output_root,
        source_root=root,
        collision_policy="rename",
    )

    assert output == output_root / "documents" / "nested" / "report.md"


def test_atomic_write_replaces_complete_file(tmp_path: Path) -> None:
    output = tmp_path / "result.md"
    output.write_text("old", encoding="utf-8")
    atomic_write_text(output, "새 결과\n")
    assert output.read_text(encoding="utf-8") == "새 결과\n"
    assert list(tmp_path.glob("*.tmp")) == []


def test_case_only_collisions_are_reserved(tmp_path: Path) -> None:
    planner = OutputPlanner()
    upper = tmp_path / "Report.pdf"
    lower = tmp_path / "report.docx"

    first = planner.reserve(
        upper,
        output_mode="source",
        output_directory=None,
        source_root=None,
        collision_policy="rename",
    )
    second = planner.reserve(
        lower,
        output_mode="source",
        output_directory=None,
        source_root=None,
        collision_policy="rename",
    )

    assert first.name == "Report.md"
    assert second.name == "report (1).md"


def test_atomic_write_removes_temporary_file_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "result.md"

    def fail_replace(_source, _destination):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="disk full"):
        atomic_write_text(output, "content")

    assert not output.exists()
    assert list(tmp_path.glob(".*.tmp")) == []
