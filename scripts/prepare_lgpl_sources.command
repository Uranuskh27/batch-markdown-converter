#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
SOURCE_DIR="$PROJECT_DIR/release/Source-Code"
QT_VERSION="$(<"$PROJECT_DIR/QT_VERSION")"
INSTALLED_PYSIDE_VERSION="$("$PROJECT_DIR/.venv/bin/python" -c 'from importlib.metadata import version; print(version("PySide6"))')"

if [[ "$INSTALLED_PYSIDE_VERSION" != "$QT_VERSION" ]]; then
  echo "PySide6 $INSTALLED_PYSIDE_VERSION does not match QT_VERSION $QT_VERSION." >&2
  echo "Update QT_VERSION and the LGPL source/compliance documents before packaging." >&2
  exit 1
fi

mkdir -p "$SOURCE_DIR"

download_source() {
  local name="$1"
  local url="$2"
  local destination="$SOURCE_DIR/$name"

  if [[ ! -f "$destination" ]]; then
    local temporary="$destination.partial"
    curl --fail --location --retry 3 --output "$temporary" "$url"
    mv "$temporary" "$destination"
  fi
  tar -tf "$destination" >/dev/null
}

download_source \
  "pyside-setup-everywhere-src-$QT_VERSION.tar.xz" \
  "https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-$QT_VERSION-src/pyside-setup-everywhere-src-$QT_VERSION.tar.xz"
download_source \
  "qtbase-everywhere-src-$QT_VERSION.tar.xz" \
  "https://download.qt.io/official_releases/qt/6.11/$QT_VERSION/submodules/qtbase-everywhere-src-$QT_VERSION.tar.xz"
download_source \
  "qtsvg-everywhere-src-$QT_VERSION.tar.xz" \
  "https://download.qt.io/official_releases/qt/6.11/$QT_VERSION/submodules/qtsvg-everywhere-src-$QT_VERSION.tar.xz"

ditto "$PROJECT_DIR/licenses/SOURCE_OFFER.md" "$SOURCE_DIR/README.md"
(
  cd "$SOURCE_DIR"
  shasum -a 256 ./*.tar.xz > SHA256SUMS.txt
  shasum -a 256 -c SHA256SUMS.txt
)

echo "LGPL corresponding source is ready: $SOURCE_DIR"
