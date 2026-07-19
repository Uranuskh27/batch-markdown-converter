#!/usr/bin/env python3
from __future__ import annotations

import argparse
import platform
import re
import shutil
import sys
from importlib import metadata
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOTS = (
    ("PySide6", set()),
    ("markitdown", {"pdf", "docx", "pptx", "xlsx", "xls", "outlook"}),
)
MANUAL_LICENSES = {
    "cobble": ("cobble-BSD-2-Clause.txt",),
    "et-xmlfile": ("openpyxl-MIT.txt",),
    "flatbuffers": ("Apache-2.0.txt",),
    "magika": ("Apache-2.0.txt",),
    "markitdown": ("Microsoft-MarkItDown-MIT.txt",),
    "openpyxl": ("openpyxl-MIT.txt",),
    "pyside6": ("Qt-PySide-NOTICE.txt", "LGPL-3.0.txt", "GPL-3.0.txt"),
    "pyside6-addons": ("Qt-PySide-NOTICE.txt", "LGPL-3.0.txt", "GPL-3.0.txt"),
    "pyside6-essentials": ("Qt-PySide-NOTICE.txt", "LGPL-3.0.txt", "GPL-3.0.txt"),
    "shiboken6": ("Qt-PySide-NOTICE.txt", "LGPL-3.0.txt", "GPL-3.0.txt"),
}
LEGAL_TEXT_SUFFIXES = {"", ".html", ".htm", ".license", ".md", ".rst", ".rtf", ".txt"}


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def runtime_distributions() -> list[metadata.Distribution]:
    environment = default_environment()
    queue = list(ROOTS)
    found: dict[str, metadata.Distribution] = {}

    while queue:
        name, extras = queue.pop(0)
        key = canonical(name)
        if key in found:
            continue
        dist = metadata.distribution(name)
        found[key] = dist

        for raw_requirement in dist.requires or ():
            requirement = Requirement(raw_requirement)
            active_extras = extras or {""}
            if requirement.marker and not any(
                requirement.marker.evaluate({**environment, "extra": extra})
                for extra in active_extras
            ):
                continue
            queue.append((requirement.name, set(requirement.extras)))

    return [found[key] for key in sorted(found)]


def is_license_path(path: Path) -> bool:
    lowered = [part.lower() for part in path.parts]
    name = path.name.lower()
    if path.suffix.lower() not in LEGAL_TEXT_SUFFIXES:
        return False
    return (
        name.startswith(("license", "licence", "copying", "notice", "copyright"))
        or "licenses" in lowered
        or "licences" in lowered
    )


def copy_distribution_licenses(dist: metadata.Distribution, destination: Path) -> int:
    copied = 0
    used_names: set[str] = set()
    for relative in dist.files or ():
        relative_path = Path(str(relative))
        if not is_license_path(relative_path):
            continue
        source = Path(dist.locate_file(relative))
        if not source.is_file():
            continue
        target_name = source.name
        if target_name in used_names:
            target_name = f"{copied:03d}-{target_name}"
        used_names.add(target_name)
        shutil.copy2(source, destination / target_name)
        copied += 1
    return copied


def metadata_value(dist: metadata.Distribution, key: str) -> str:
    value = dist.metadata.get(key, "").strip()
    return " ".join(value.split())


def find_python_license() -> Path:
    base_executable = Path(getattr(sys, "_base_executable", sys.executable)).resolve()
    candidates = [parent / "LICENSE" for parent in base_executable.parents]
    candidates.extend((Path(sys.base_prefix) / "LICENSE", Path(sys.prefix) / "LICENSE"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError("Could not locate the bundled Python runtime license")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    rows: list[tuple[str, str, str, str]] = []
    for dist in runtime_distributions():
        name = dist.metadata["Name"]
        key = canonical(name)
        component_dir = output / f"{key}-{dist.version}"
        component_dir.mkdir()

        copied = copy_distribution_licenses(dist, component_dir)
        for license_name in MANUAL_LICENSES.get(key, ()):
            shutil.copy2(PROJECT_ROOT / "licenses" / license_name, component_dir / license_name)
            copied += 1
        if copied == 0:
            raise RuntimeError(f"No license material found for runtime component: {name} {dist.version}")

        license_name = (
            metadata_value(dist, "License-Expression")
            or metadata_value(dist, "License")
            or "See included license files"
        )
        homepage = metadata_value(dist, "Home-page")
        if not homepage:
            urls = dist.metadata.get_all("Project-URL") or []
            homepage = urls[0].split(",", 1)[-1].strip() if urls else ""
        rows.append((name, dist.version, license_name, homepage))

    python_version = platform.python_version()
    python_dir = output / f"python-{python_version}"
    python_dir.mkdir()
    shutil.copy2(find_python_license(), python_dir / "PYTHON-LICENSE.txt")
    rows.append(
        (
            "Python",
            python_version,
            "Python Software Foundation License Version 2",
            f"https://docs.python.org/{platform.python_version_tuple()[0]}.{platform.python_version_tuple()[1]}/license.html",
        )
    )

    pyinstaller = metadata.distribution("pyinstaller")
    pyinstaller_dir = output / f"pyinstaller-{pyinstaller.version}"
    pyinstaller_dir.mkdir()
    if copy_distribution_licenses(pyinstaller, pyinstaller_dir) == 0:
        raise RuntimeError(f"No license material found for PyInstaller {pyinstaller.version}")
    rows.append(
        (
            "PyInstaller bootloader",
            pyinstaller.version,
            "GPL-2.0-or-later WITH Bootloader-exception; runtime hooks Apache-2.0",
            "https://github.com/pyinstaller/pyinstaller",
        )
    )

    shutil.copy2(PROJECT_ROOT / "licenses" / "Qt-PySide-NOTICE.txt", output / "Qt-PySide-NOTICE.txt")
    shutil.copy2(PROJECT_ROOT / "licenses" / "LGPL-3.0.txt", output / "LGPL-3.0.txt")
    shutil.copy2(PROJECT_ROOT / "licenses" / "GPL-3.0.txt", output / "GPL-3.0.txt")
    shutil.copy2(
        PROJECT_ROOT / "licenses" / "Microsoft-MarkItDown-MIT.txt",
        output / "Microsoft-MarkItDown-MIT.txt",
    )

    lines = [
        "# Distributed third-party components",
        "",
        "Generated from the locked environment used to build this release. The inventory includes",
        "the bundled Python runtime and PyInstaller bootloader in addition to Python packages.",
        "",
        "| Component | Version | Declared license | Project |",
        "| --- | --- | --- | --- |",
    ]
    for name, version, license_name, homepage in rows:
        project = f"[link]({homepage})" if homepage else "—"
        lines.append(f"| {name} | {version} | {license_name.replace('|', '/')} | {project} |")
    lines.extend(
        [
            "",
            "Qt/PySide corresponding source and replacement instructions are provided separately.",
            "The original application source is available in the public GitHub repository.",
            "",
        ]
    )
    (output / "COMPONENTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Collected licenses for {len(rows)} distributed components: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
