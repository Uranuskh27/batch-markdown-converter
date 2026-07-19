# Open-source distribution compliance

This repository and its release process are intended for a free, open-source
portfolio project. This document records the distribution choices; it is not
legal advice.

## Application code

The original Batch Markdown Converter code in this repository is released under the MIT
License in `LICENSE`.

## Microsoft MarkItDown

Microsoft MarkItDown 0.1.6 is used as an unmodified conversion dependency and
is licensed under the MIT License. Its Microsoft copyright notice and full
license are stored in `licenses/Microsoft-MarkItDown-MIT.txt` and copied into
every DMG.

This project is independent and is not an official Microsoft product. No
Microsoft logo is used. The name describes compatibility with the upstream
engine and must not imply Microsoft sponsorship.

## Qt for Python

PySide6 and Shiboken6 6.11.1 are used under LGPL version 3. The build removes
unused Qt Virtual Keyboard components. The application keeps the remaining Qt
frameworks dynamically replaceable inside the `.app` bundle.

Every DMG includes:

- the full LGPL version 3 and GPL version 3 texts;
- a prominent Qt/PySide notice;
- a runtime component and license inventory;
- corresponding-source and replacement instructions;
- license files exposed by every runtime Python distribution.

Exact PySide6, Qt Base, and Qt SVG source archives are generated under
`release/Source-Code/` and must be attached to the same GitHub Release as the
DMGs. See `BUILD_AND_RELINK.md` and `licenses/SOURCE_OFFER.md`.

## Python and PyInstaller

The app bundle contains the unmodified Python 3.12 interpreter. Its exact
version, Python Software Foundation License Version 2 text, and upstream
license URL are included in each DMG's generated component inventory.

PyInstaller 6.21.0 is the packaging tool. The final executable contains its
bootloader and run-time hooks. Each DMG includes PyInstaller's complete
`COPYING.txt`, identifies the GPL-2.0-or-later Bootloader Exception, and notes
the Apache-2.0 license for embedded run-time hooks. No PyInstaller source is
modified by this project.

## Release rule

Do not publish a DMG unless `scripts/verify_releases.command` passes. Run the
matching `scripts/prepare_korean_github_release.command` or
`scripts/prepare_english_github_release.command` and upload every file created
under the corresponding `release/GitHub-Upload-Korean/` or
`release/GitHub-Upload-English/` directory to that language's GitHub Release.
Each directory includes one language DMG, its checksum, all three corresponding-
source archives, and their checksum. Review the generated component inventory
whenever a dependency version changes.
