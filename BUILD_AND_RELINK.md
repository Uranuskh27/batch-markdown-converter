# Qt/PySide source, replacement, and re-signing

Batch Markdown Converter uses the unmodified Qt/PySide shared frameworks that ship in
the PySide6 6.11.1 wheel. The application code is not statically linked to Qt.

## Corresponding source

Download the three archives and `SHA256SUMS.txt` from the `Source-Code` folder
of the same GitHub Release as the DMG. They contain the exact PySide6,
Shiboken6, Qt Base, and Qt SVG sources corresponding to the bundled libraries.

## Build tools

Building replacements requires an Apple Silicon Mac, Xcode Command Line Tools,
CMake, Ninja, Python 3.12, and a C/C++ toolchain compatible with the target
macOS release. Follow the upstream instructions:

- Qt: https://doc.qt.io/qt-6/macos-building.html
- Qt for Python: https://doc.qt.io/qtforpython-6/building_from_source/index.html

Use version 6.11.1 for Qt, PySide6, and Shiboken6. This project does not apply
patches to those components.

## Replace the libraries

Make a copy of the application before experimenting. The LGPL-covered
libraries are inside these directories:

```text
Batch Markdown Converter Korean.app/Contents/Frameworks/PySide6/
Batch Markdown Converter Korean.app/Contents/Frameworks/shiboken6/
```

Replace the matching Qt frameworks, PySide extension modules, and PySide/
Shiboken dylibs with compatible arm64 builds. Preserve their relative paths
and install names. The same locations apply to `Batch Markdown Converter English.app`.

Changing a library invalidates the original code signature. Remove the old
signature and apply a local ad-hoc signature after replacement:

```sh
codesign --remove-signature "/path/to/Batch Markdown Converter English.app"
codesign --force --deep --sign - "/path/to/Batch Markdown Converter English.app"
codesign --verify --deep --strict "/path/to/Batch Markdown Converter English.app"
```

This information is provided so recipients can modify, replace, debug, and
run the LGPL-covered libraries on a general-purpose Mac.
