# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

APP_VERSION = Path("../VERSION").read_text(encoding="utf-8").strip()

datas = []
binaries = []
hiddenimports = []
for package in ("markitdown", "magika", "pdfminer", "mammoth", "openpyxl", "pptx"):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

analysis = Analysis(
    ["../app_en.py"],
    pathex=[".."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["pytest", "py", "Pygments"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="Batch-Markdown-Converter-English",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=False,
    target_arch="arm64",
)
collection = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="Batch-Markdown-Converter-English",
)
app = BUNDLE(
    collection,
    name="Batch Markdown Converter English.app",
    icon=None,
    bundle_identifier="io.github.batchmarkdownconverter.english",
    info_plist={
        "CFBundleDisplayName": "Batch Markdown Converter English",
        "CFBundleName": "Batch Markdown Converter English",
        "LSMinimumSystemVersion": "13.0",
        "CFBundleShortVersionString": APP_VERSION,
        "CFBundleVersion": APP_VERSION,
        "NSHumanReadableCopyright": "Copyright © 2026 Batch Markdown Converter contributors",
    },
)
