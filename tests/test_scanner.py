from pathlib import Path

from core.scanner import Scanner


def run_scanner(paths: list[Path], **kwargs):
    found = []
    scanner = Scanner(paths, batch_size=2, **kwargs)
    scanner.batch_found.connect(found.extend)
    scanner.run()
    return found


def test_scanner_classifies_supported_and_skipped_files(tmp_path: Path) -> None:
    (tmp_path / "document.pdf").write_bytes(b"content")
    (tmp_path / "already.md").write_text("markdown", encoding="utf-8")
    (tmp_path / "empty.docx").touch()
    (tmp_path / "unknown.bin").write_bytes(b"content")
    (tmp_path / ".hidden.pdf").write_bytes(b"hidden")

    found = run_scanner([tmp_path])
    by_name = {item.src.name: item for item in found}

    assert by_name["document.pdf"].skip_reason is None
    assert by_name["already.md"].skip_reason == "Markdown 원본은 제외"
    assert by_name["empty.docx"].skip_reason == "0바이트 파일"
    assert by_name["unknown.bin"].skip_reason == "지원하지 않는 형식"
    assert ".hidden.pdf" not in by_name


def test_scanner_does_not_enter_macos_packages(tmp_path: Path) -> None:
    package = tmp_path / "Example.app"
    package.mkdir()
    (package / "inside.pdf").write_bytes(b"content")
    (tmp_path / "outside.pdf").write_bytes(b"content")

    found = run_scanner([tmp_path])
    names = {item.src.name for item in found}

    assert "outside.pdf" in names
    assert "inside.pdf" not in names


def test_scanner_skips_symlinked_directories(tmp_path: Path) -> None:
    external = tmp_path / "external"
    external.mkdir()
    (external / "linked.pdf").write_bytes(b"content")
    root = tmp_path / "root"
    root.mkdir()
    (root / "link").symlink_to(external, target_is_directory=True)
    (root / "normal.pdf").write_bytes(b"content")

    found = run_scanner([root])
    names = {item.src.name for item in found}

    assert names == {"normal.pdf"}


def test_scanner_applies_size_and_count_limits(tmp_path: Path) -> None:
    for number in range(5):
        (tmp_path / f"file-{number}.txt").write_bytes(b"x" * 32)

    found = run_scanner([tmp_path], max_files=3, max_file_size_mb=1)
    assert len(found) == 3

    oversized = tmp_path / "oversized.txt"
    oversized.write_bytes(b"x" * (1024 * 1024 + 1))
    result = run_scanner([oversized], max_file_size_mb=1)
    assert result[0].skip_reason == "파일 크기 상한 1MB 초과"


def test_scanner_reports_missing_input(tmp_path: Path) -> None:
    missing = tmp_path / "missing.pdf"
    result = run_scanner([missing])
    assert result[0].skip_reason == "파일을 찾을 수 없음"
