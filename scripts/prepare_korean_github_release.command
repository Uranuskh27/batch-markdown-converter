#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
VERSION="$(<"$PROJECT_DIR/VERSION")"
QT_VERSION="$(<"$PROJECT_DIR/QT_VERSION")"
RELEASE_ROOT="$PROJECT_DIR/release"
KOREAN_DIR="$RELEASE_ROOT/Korean"
SOURCE_DIR="$RELEASE_ROOT/Source-Code"
UPLOAD_DIR="$RELEASE_ROOT/GitHub-Upload-Korean"
DMG_NAME="Batch-Markdown-Converter-Korean-$VERSION-arm64.dmg"
PYSIDE_SOURCE="pyside-setup-everywhere-src-$QT_VERSION.tar.xz"
QTBASE_SOURCE="qtbase-everywhere-src-$QT_VERSION.tar.xz"
QTSVG_SOURCE="qtsvg-everywhere-src-$QT_VERSION.tar.xz"

REQUIRED_FILES=(
  "$KOREAN_DIR/$DMG_NAME"
  "$KOREAN_DIR/SHA256SUMS.txt"
  "$SOURCE_DIR/$PYSIDE_SOURCE"
  "$SOURCE_DIR/$QTBASE_SOURCE"
  "$SOURCE_DIR/$QTSVG_SOURCE"
  "$SOURCE_DIR/SHA256SUMS.txt"
)

for REQUIRED_FILE in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$REQUIRED_FILE" ]]; then
    echo "배포 파일이 없습니다: $REQUIRED_FILE" >&2
    echo "먼저 ./scripts/package_releases.command를 실행하세요." >&2
    exit 1
  fi
done

echo "한글판과 영문판의 전체 배포 검증을 실행합니다..."
"$PROJECT_DIR/scripts/verify_releases.command"

# 자동 생성되는 폴더이며 실행할 때마다 안전하게 새로 만듭니다.
rm -rf -- "$UPLOAD_DIR"
mkdir -p "$UPLOAD_DIR"

copy_asset() {
  local SOURCE_FILE="$1"
  local DESTINATION_FILE="$2"

  if ! ln "$SOURCE_FILE" "$DESTINATION_FILE" 2>/dev/null; then
    ditto "$SOURCE_FILE" "$DESTINATION_FILE"
  fi
}

copy_asset "$KOREAN_DIR/$DMG_NAME" "$UPLOAD_DIR/$DMG_NAME"
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
echo "한글판 GitHub Release 파일이 준비되었습니다:"
echo "$UPLOAD_DIR"
echo
find "$UPLOAD_DIR" -maxdepth 1 -type f -exec basename {} \; | sort
echo
echo "위 파일을 모두 동일한 GitHub Release에 업로드하세요."
