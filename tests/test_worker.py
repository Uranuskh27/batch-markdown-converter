from pathlib import Path

from core.worker_entry import convert_one


def test_worker_converts_text_file(tmp_path: Path) -> None:
    source = tmp_path / "한글 문서.txt"
    destination = tmp_path / "한글 문서.md"
    source.write_text("제목\n\n- 항목 하나\n", encoding="utf-8")

    convert_one(source, destination)

    assert destination.exists()
    assert "항목 하나" in destination.read_text(encoding="utf-8")
