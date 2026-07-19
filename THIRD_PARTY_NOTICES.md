# Third-party notices

This application bundles third-party open-source software. Each component remains subject to its
own license terms. A versioned component inventory and the license material supplied by each Python
distribution are generated into the DMG's `Third-Party-Licenses` directory.

## Microsoft MarkItDown

Microsoft MarkItDown is distributed under the MIT License.

- Project: https://github.com/microsoft/markitdown
- Copyright: Microsoft Corporation
- License: https://github.com/microsoft/markitdown/blob/main/LICENSE

The complete Microsoft copyright and MIT text is included as
`Third-Party-Licenses/Microsoft-MarkItDown-MIT.txt`.

## Qt for Python

PySide6 and Shiboken6 6.11.1 are used under LGPL version 3. The DMG includes the complete LGPL and
GPL texts, a Qt/PySide notice, corresponding-source information, and instructions for replacing and
locally re-signing modified Qt/PySide libraries. Unused Qt Virtual Keyboard components are removed
from the application bundle.

- Project: https://doc.qt.io/qtforpython-6/
- LGPL obligations: https://www.qt.io/development/open-source-lgpl-obligations

## Python runtime

The application bundles Python 3.12 under the Python Software Foundation License Version 2. The
exact runtime version and complete license text are included in the generated component inventory
and its `python-<version>/PYTHON-LICENSE.txt` file.

- Project: https://www.python.org/
- License: https://docs.python.org/3.12/license.html

## PyInstaller bootloader

PyInstaller 6.21.0 is used to package the application. Its compiled bootloader and related files
are distributed under GPL-2.0-or-later with the PyInstaller Bootloader Exception, which permits
embedding and distributing the bootloader with this application. Embedded run-time hooks are under
Apache-2.0. The complete upstream `COPYING.txt` is included in the generated component inventory.

- Project: https://github.com/pyinstaller/pyinstaller
- License: https://github.com/pyinstaller/pyinstaller/blob/v6.21.0/COPYING.txt

Maintainers must run `scripts/verify_releases.command` and review the generated component inventory
whenever dependencies change. This notice is informational and is not legal advice.
