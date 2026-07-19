from __future__ import annotations

import json
from pathlib import Path
from zipfile import is_zipfile

from markitdown import MarkItDown

from .output_writer import atomic_write_text
from .i18n import tr


def convert_one(source: Path, destination: Path) -> None:
    source = source.resolve(strict=True)
    if not source.is_file():
        raise FileNotFoundError(
            tr(f"원본을 찾을 수 없습니다: {source}", f"Source file not found: {source}")
        )
    validate_source(source)

    converter = MarkItDown(enable_plugins=False)
    if hasattr(converter, "convert_local"):
        result = converter.convert_local(str(source))
    else:
        result = converter.convert(str(source))

    markdown = getattr(result, "markdown", None)
    if markdown is None:
        markdown = getattr(result, "text_content", None)
    if markdown is None:
        raise RuntimeError(
            tr(
                "MarkItDown이 변환 결과를 반환하지 않았습니다.",
                "MarkItDown did not return a conversion result.",
            )
        )

    atomic_write_text(destination, markdown)


def validate_source(source: Path) -> None:
    suffix = source.suffix.casefold()
    header = source.read_bytes()[:8]

    if suffix == ".pdf" and not header.startswith(b"%PDF-"):
        raise ValueError(
            tr(
                "올바른 PDF 파일이 아니거나 파일이 손상되었습니다.",
                "The PDF file is invalid or corrupted.",
            )
        )
    if suffix in {".docx", ".pptx", ".xlsx", ".epub", ".zip"} and not is_zipfile(source):
        file_type = suffix[1:].upper()
        raise ValueError(
            tr(
                f"올바른 {file_type} 파일이 아니거나 파일이 손상되었습니다.",
                f"The {file_type} file is invalid or corrupted.",
            )
        )
    if suffix in {".xls", ".msg"} and header != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        file_type = suffix[1:].upper()
        raise ValueError(
            tr(
                f"올바른 {file_type} 파일이 아니거나 파일이 손상되었습니다.",
                f"The {file_type} file is invalid or corrupted.",
            )
        )


def worker_main(source: str, destination: str) -> int:
    try:
        convert_one(Path(source), Path(destination))
    except Exception as error:
        print(
            json.dumps(
                {"ok": False, "error": friendly_error(error)},
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 1

    print(json.dumps({"ok": True, "output": destination}, ensure_ascii=False), flush=True)
    return 0


def friendly_error(error: Exception) -> str:
    message = str(error).strip()
    lowered = message.casefold()
    if "password" in lowered or "encrypted" in lowered:
        return tr(
            "암호로 보호된 문서는 변환할 수 없습니다.",
            "Password-protected documents cannot be converted.",
        )
    if isinstance(error, FileNotFoundError):
        return tr("원본 파일을 찾을 수 없습니다.", "The source file could not be found.")
    if isinstance(error, PermissionError):
        return tr(
            "파일을 읽거나 결과를 저장할 권한이 없습니다.",
            "Permission denied while reading the file or saving the result.",
        )
    return message or type(error).__name__
