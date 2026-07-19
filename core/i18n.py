from __future__ import annotations

import os
from enum import Enum


def language() -> str:
    value = os.environ.get("BATCH_MARKDOWN_CONVERTER_LANGUAGE", "ko").strip().casefold()
    return "en" if value.startswith("en") else "ko"


def tr(korean: str, english: str) -> str:
    return english if language() == "en" else korean


def application_settings_name() -> str:
    return (
        "BatchMarkdownConverterEnglish"
        if language() == "en"
        else "BatchMarkdownConverterKorean"
    )


def application_display_name() -> str:
    return (
        "Batch Markdown Converter English"
        if language() == "en"
        else "Batch Markdown Converter Korean"
    )


def status_text(status: Enum) -> str:
    if language() != "en":
        return str(status.value)
    return {
        "QUEUED": "Queued",
        "RUNNING": "Converting",
        "DONE": "Completed",
        "FAILED": "Failed",
        "SKIPPED": "Skipped",
        "CANCELLED": "Cancelled",
    }.get(status.name, str(status.value))
