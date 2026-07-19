from __future__ import annotations

import os
import tomllib
from pathlib import Path

from scripts.generate_license_bundle import is_license_path


PROJECT_ROOT = Path(__file__).parents[1]


def test_release_version_is_consistent_with_project_metadata() -> None:
    version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    metadata = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert version == metadata["project"]["version"]
    for spec_name in ("batch-markdown-converter.spec", "batch-markdown-converter-english.spec"):
        spec = (PROJECT_ROOT / "build" / spec_name).read_text(encoding="utf-8")
        assert 'Path("../VERSION")' in spec
        assert '"CFBundleShortVersionString": APP_VERSION' in spec


def test_batch_markdown_converter_release_names_are_consistent() -> None:
    korean_spec = (PROJECT_ROOT / "build" / "batch-markdown-converter.spec").read_text(
        encoding="utf-8"
    )
    english_spec = (
        PROJECT_ROOT / "build" / "batch-markdown-converter-english.spec"
    ).read_text(encoding="utf-8")
    package_script = (PROJECT_ROOT / "scripts" / "package_releases.command").read_text(
        encoding="utf-8"
    )
    verify_script = (PROJECT_ROOT / "scripts" / "verify_releases.command").read_text(
        encoding="utf-8"
    )

    assert 'name="Batch Markdown Converter Korean.app"' in korean_spec
    assert '"CFBundleDisplayName": "Batch Markdown Converter Korean"' in korean_spec
    assert 'bundle_identifier="io.github.batchmarkdownconverter.korean"' in korean_spec
    assert 'name="Batch Markdown Converter English.app"' in english_spec
    assert '"CFBundleDisplayName": "Batch Markdown Converter English"' in english_spec
    assert 'bundle_identifier="io.github.batchmarkdownconverter.english"' in english_spec

    for expected_name in (
        "Batch-Markdown-Converter-Korean-$VERSION-arm64.dmg",
        "Batch-Markdown-Converter-English-$VERSION-arm64.dmg",
    ):
        assert expected_name in package_script
        assert expected_name in verify_script


def test_language_release_directories_and_guides_are_separate() -> None:
    korean = PROJECT_ROOT / "release" / "Korean" / "README.txt"
    english = PROJECT_ROOT / "release" / "English" / "README.txt"

    assert korean.is_file()
    assert english.is_file()
    assert "한국어판" in korean.read_text(encoding="utf-8")
    assert "English" in english.read_text(encoding="utf-8")
    assert (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License")


def test_language_github_readmes_are_ready_for_separate_repositories() -> None:
    korean = PROJECT_ROOT / "github" / "Korean" / "README.md"
    english = PROJECT_ROOT / "github" / "English" / "README.md"

    assert korean.is_file()
    assert english.is_file()

    korean_text = korean.read_text(encoding="utf-8")
    english_text = english.read_text(encoding="utf-8")

    assert "Batch-Markdown-Converter-Korean-*-arm64.dmg" in korean_text
    assert "./scripts/run.command" in korean_text
    assert "Batch-Markdown-Converter-English-*-arm64.dmg" in english_text
    assert "./scripts/run_english.command" in english_text

    for readme in (korean_text, english_text):
        assert "Microsoft" in readme
        assert "MIT License" in readme
        assert "Python 3.12" in readme
        assert "PyInstaller 6.21.0" in readme
        assert "SHA256SUMS.txt" in readme
        assert "DISTRIBUTION.md" in readme


def test_root_readme_is_ready_for_the_english_public_repository() -> None:
    root_readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert root_readme.startswith("# Batch Markdown Converter for macOS")
    assert "An English macOS desktop app" in root_readme
    assert "Batch-Markdown-Converter-English-*-arm64.dmg" in root_readme
    assert "Batch Markdown Converter English.app" in root_readme
    assert "not an official Microsoft product" in root_readme
    assert "Python 3.12" in root_readme
    assert "PyInstaller 6.21.0" in root_readme
    assert (PROJECT_ROOT / "README.ko.md").is_file()


def test_public_source_has_no_local_user_identifier_or_home_path() -> None:
    private_home = str(Path.home())
    private_identifier = Path(private_home).name
    excluded_roots = {
        ".build",
        ".git",
        ".pyinstaller-cache",
        ".pytest_cache",
        ".venv",
        "build",
        "local-test-data",
        "release",
    }

    for path in PROJECT_ROOT.rglob("*"):
        relative_parts = path.relative_to(PROJECT_ROOT).parts
        if (
            not path.is_file()
            or relative_parts[0] in excluded_roots
            or "__pycache__" in relative_parts
            or path.suffix in {".pyc", ".pyo"}
        ):
            continue
        if path.stat().st_size > 2_000_000:
            continue
        content = path.read_bytes().lower()
        assert private_identifier.encode() not in content, path
        assert private_home.lower().encode() not in content, path


def test_release_commands_are_executable() -> None:
    for script_name in (
        "package_releases.command",
        "verify_releases.command",
        "prepare_lgpl_sources.command",
        "prepare_english_github_release.command",
        "prepare_korean_github_release.command",
        "publish_english_github_release.command",
        "publish_korean_github_release.command",
        "prune_qt_bundle.command",
    ):
        script = PROJECT_ROOT / "scripts" / script_name
        assert script.is_file()
        assert os.access(script, os.X_OK)


def test_open_source_compliance_material_is_complete() -> None:
    qt_version = (PROJECT_ROOT / "QT_VERSION").read_text(encoding="utf-8").strip()
    assert qt_version == "6.11.1"

    required = (
        "Microsoft-MarkItDown-MIT.txt",
        "Qt-PySide-NOTICE.txt",
        "LGPL-3.0.txt",
        "GPL-3.0.txt",
        "SOURCE_OFFER.md",
    )
    for name in required:
        path = PROJECT_ROOT / "licenses" / name
        assert path.is_file()
        assert path.stat().st_size > 200

    assert (PROJECT_ROOT / "COMPLIANCE.md").is_file()
    assert (PROJECT_ROOT / "BUILD_AND_RELINK.md").is_file()
    for document_name in ("COMPLIANCE.md", "BUILD_AND_RELINK.md"):
        assert qt_version in (PROJECT_ROOT / document_name).read_text(encoding="utf-8")
    assert qt_version in (PROJECT_ROOT / "licenses" / "SOURCE_OFFER.md").read_text(
        encoding="utf-8"
    )

    package_script = (PROJECT_ROOT / "scripts" / "package_releases.command").read_text(
        encoding="utf-8"
    )
    assert "prepare_lgpl_sources.command" in package_script
    assert "generate_license_bundle.py" in package_script

    license_generator = (PROJECT_ROOT / "scripts" / "generate_license_bundle.py").read_text(
        encoding="utf-8"
    )
    assert "PYTHON-LICENSE.txt" in license_generator
    assert "PyInstaller bootloader" in license_generator
    assert "Bootloader-exception" in license_generator

    for build_script_name in ("build_app.command", "build_english_app.command"):
        build_script = (PROJECT_ROOT / "scripts" / build_script_name).read_text(encoding="utf-8")
        assert "prune_qt_bundle.command" in build_script


def test_license_bundle_excludes_source_and_bytecode_from_license_directories() -> None:
    assert is_license_path(Path("package.dist-info/licenses/LICENSE"))
    assert is_license_path(Path("package.dist-info/LICENSE.txt"))
    assert not is_license_path(Path("packaging/licenses/_spdx.py"))
    assert not is_license_path(Path("packaging/licenses/_spdx.cpython-312.pyc"))
