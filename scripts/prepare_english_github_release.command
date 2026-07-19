#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
VERSION="$(<"$PROJECT_DIR/VERSION")"
QT_VERSION="$(<"$PROJECT_DIR/QT_VERSION")"
RELEASE_ROOT="$PROJECT_DIR/release"
ENGLISH_DIR="$RELEASE_ROOT/English"
SOURCE_DIR="$RELEASE_ROOT/Source-Code"
UPLOAD_DIR="$RELEASE_ROOT/GitHub-Upload-English"
DMG_NAME="Batch-Markdown-Converter-English-$VERSION-arm64.dmg"
PYSIDE_SOURCE="pyside-setup-everywhere-src-$QT_VERSION.tar.xz"
QTBASE_SOURCE="qtbase-everywhere-src-$QT_VERSION.tar.xz"
QTSVG_SOURCE="qtsvg-everywhere-src-$QT_VERSION.tar.xz"

REQUIRED_FILES=(
  "$ENGLISH_DIR/$DMG_NAME"
  "$ENGLISH_DIR/SHA256SUMS.txt"
  "$SOURCE_DIR/$PYSIDE_SOURCE"
  "$SOURCE_DIR/$QTBASE_SOURCE"
  "$SOURCE_DIR/$QTSVG_SOURCE"
  "$SOURCE_DIR/SHA256SUMS.txt"
)

for REQUIRED_FILE in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$REQUIRED_FILE" ]]; then
    echo "Missing release file: $REQUIRED_FILE" >&2
    echo "Build the release first with ./scripts/package_releases.command" >&2
    exit 1
  fi
done

echo "Running the complete Korean and English release verification..."
"$PROJECT_DIR/scripts/verify_releases.command"

# This is a generated, fully replaceable upload directory.
rm -rf -- "$UPLOAD_DIR"
mkdir -p "$UPLOAD_DIR"

copy_asset() {
  local SOURCE_FILE="$1"
  local DESTINATION_FILE="$2"

  # Hard links avoid duplicating large release files on the same volume. Fall back
  # to a normal copy when the filesystem does not support them.
  if ! ln "$SOURCE_FILE" "$DESTINATION_FILE" 2>/dev/null; then
    ditto "$SOURCE_FILE" "$DESTINATION_FILE"
  fi
}

copy_asset "$ENGLISH_DIR/$DMG_NAME" "$UPLOAD_DIR/$DMG_NAME"
copy_asset "$SOURCE_DIR/$PYSIDE_SOURCE" "$UPLOAD_DIR/$PYSIDE_SOURCE"
copy_asset "$SOURCE_DIR/$QTBASE_SOURCE" "$UPLOAD_DIR/$QTBASE_SOURCE"
copy_asset "$SOURCE_DIR/$QTSVG_SOURCE" "$UPLOAD_DIR/$QTSVG_SOURCE"

(
  cd "$UPLOAD_DIR"
  shasum -a 256 "$DMG_NAME" > "$DMG_NAME.sha256.txt"
  shasum -a 256 "$PYSIDE_SOURCE" "$QTBASE_SOURCE" "$QTSVG_SOURCE" \
    > LGPL-Sources-SHA256SUMS.txt
  shasum -a 256 -c "$DMG_NAME.sha256.txt"
  shasum -a 256 -c LGPL-Sources-SHA256SUMS.txt
)

echo
echo "English GitHub Release assets are ready:"
echo "$UPLOAD_DIR"
echo
find "$UPLOAD_DIR" -maxdepth 1 -type f -exec basename {} \; | sort
echo
echo "Upload every file shown above to the same GitHub Release."
