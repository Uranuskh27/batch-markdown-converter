# Batch Markdown Converter for macOS

[한국어 문서](README.ko.md)

An English macOS desktop app that batch-converts documents and folders to Markdown with drag and
drop. It uses Microsoft's open-source
[MarkItDown](https://github.com/microsoft/markitdown) project as its conversion engine.

> This is an independent open-source GUI project and is not an official Microsoft product.

## Features

- Add multiple files and folders at once, including recursive folder scanning
- Run each conversion in an isolated process so one file cannot freeze the app
- See queued, converting, completed, failed, skipped, and cancelled states per file
- Retry only failed files or cancel queued and running work
- Choose one output folder and always show exactly where Markdown will be saved
- Rename, skip, or overwrite when an output filename already exists
- Switch between light and dark themes with an animated sun-and-moon control
- Follow conversion progress with an animated running dog
- Optionally open output folders in Finder when conversion finishes
- Process documents locally on your Mac

## Supported formats

PDF, DOCX, PPTX, XLSX, XLS, HTML, CSV, JSON, XML, EPUB, TXT, RTF, MSG, and ZIP

The current version does not support image OCR, standalone images, audio, URLs, or cloud document
conversion.

## Requirements

- macOS 13 Ventura or later
- An Apple Silicon Mac
- The current DMG is arm64-only

## Installation

1. Download the latest `Batch-Markdown-Converter-English-*-arm64.dmg` from this repository's **Releases** page.
2. Open the DMG and drag `Batch Markdown Converter English.app` into the `Applications` folder.
3. Launch **Batch Markdown Converter English** from Applications.

The current test build is ad-hoc signed and has not been notarized by Apple. Make sure the file came
from the official Release and verify it against the included `*.sha256.txt` file. If macOS blocks
the first launch, Control-click the app in Finder and choose **Open**.

## Usage

1. Select files with **Add Files**, or drag files and folders into the drop area.
2. Select **Choose Folder…** and confirm the displayed output location.
3. If needed, open Settings to change concurrency, per-file timeout, filename collision behavior,
   and whether Finder opens after conversion.
4. Select **Convert All**.

A failed file does not stop the rest of the queue. Source files are never modified.

## Run from source

Python 3.12 is recommended.

```sh
git clone <this repository URL>
cd <repository directory>
./scripts/setup.command
./scripts/run_english.command
```

## Test and build

```sh
.venv/bin/pytest
./scripts/build_english_app.command
./scripts/package_releases.command
./scripts/verify_releases.command
./scripts/prepare_english_github_release.command
```

`package_releases.command` creates both the Korean and English DMGs. For this English repository,
`prepare_english_github_release.command` fully verifies both language builds and creates the exact six
assets to upload under `release/GitHub-Upload-English/`. Upload every file in that folder to the same
GitHub Release. See `DISTRIBUTION.md` for the optional one-command publisher, Developer ID signing,
and Apple notarization instructions.

## Privacy

Added documents are handled by local conversion processes. This GUI does not upload documents to an
external server. Results are written only to the output location selected by the user.

## Open-source foundations and attribution

- [Microsoft MarkItDown 0.1.6](https://github.com/microsoft/markitdown) — unmodified document
  conversion engine, MIT License.
- [Qt for Python / PySide6 and Shiboken6 6.11.1](https://doc.qt.io/qtforpython-6/) — GUI
  runtime, used unmodified under LGPLv3.
- [Python 3.12](https://docs.python.org/3.12/license.html) — bundled interpreter runtime,
  Python Software Foundation License Version 2.
- [PyInstaller 6.21.0](https://github.com/pyinstaller/pyinstaller) — application packager and
  embedded bootloader, GPL-2.0-or-later with the PyInstaller Bootloader Exception; embedded
  run-time hooks are Apache-2.0.

The DMG's `Third-Party-Licenses/COMPONENTS.md` contains the version, declared license, project
link, and supplied license files for every distributed component. The running dog, bone, sun,
and moon are original QPainter vector drawings created for this project; no third-party image or
font asset is bundled for them.

## Contributing

Bug reports and improvements are welcome. When filing an issue, include your macOS version, Mac model,
input format, reproduction steps, and the displayed error. Do not attach private source documents to
public issues.

Run the full test suite before submitting a code change:

```sh
.venv/bin/pytest
```

## License

This GUI project is released under the [MIT License](LICENSE). Microsoft MarkItDown is also provided
under the MIT License. Complete notices for bundled libraries and build components are available in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
Qt/PySide is used under LGPLv3; corresponding source and replacement instructions are documented in
`COMPLIANCE.md` and `BUILD_AND_RELINK.md`. This project is not an official Microsoft product.
