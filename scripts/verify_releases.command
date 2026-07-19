#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
VERSION="$(<"$PROJECT_DIR/VERSION")"
KOREAN_DIR="$PROJECT_DIR/release/Korean"
ENGLISH_DIR="$PROJECT_DIR/release/English"
KOREAN_DMG="$KOREAN_DIR/Batch-Markdown-Converter-Korean-$VERSION-arm64.dmg"
ENGLISH_DMG="$ENGLISH_DIR/Batch-Markdown-Converter-English-$VERSION-arm64.dmg"
SOURCE_DIR="$PROJECT_DIR/release/Source-Code"

(
  cd "$KOREAN_DIR"
  shasum -a 256 -c SHA256SUMS.txt
)
(
  cd "$ENGLISH_DIR"
  shasum -a 256 -c SHA256SUMS.txt
)
(
  cd "$SOURCE_DIR"
  shasum -a 256 -c SHA256SUMS.txt
)

hdiutil verify "$KOREAN_DMG"
hdiutil verify "$ENGLISH_DMG"

verify_mounted_dmg() {
  local dmg="$1"
  local app_name="$2"
  local expected_identifier="$3"
  local mount_point
  mount_point="$(mktemp -d /private/tmp/batch-markdown-converter-release.XXXXXX)"

  hdiutil attach -readonly -nobrowse -mountpoint "$mount_point" "$dmg" >/dev/null
  if [[ ! -d "$mount_point/$app_name" ]]; then
    echo "Missing app in DMG: $app_name" >&2
    hdiutil detach "$mount_point" >/dev/null
    rmdir "$mount_point"
    return 1
  fi

  codesign --verify --deep --strict "$mount_point/$app_name"
  [[ -L "$mount_point/Applications" ]]
  [[ -f "$mount_point/README.txt" ]]
  [[ -f "$mount_point/LICENSE.txt" ]]
  [[ -f "$mount_point/THIRD_PARTY_NOTICES.md" ]]
  [[ -f "$mount_point/COMPLIANCE.md" ]]
  [[ -f "$mount_point/BUILD_AND_RELINK.md" ]]
  [[ -f "$mount_point/SOURCE_OFFER.md" ]]
  [[ -f "$mount_point/LGPL_SOURCE_SHA256SUMS.txt" ]]
  [[ -d "$mount_point/Third-Party-Licenses" ]]
  [[ -s "$mount_point/Third-Party-Licenses/COMPONENTS.md" ]]
  [[ -s "$mount_point/Third-Party-Licenses/LGPL-3.0.txt" ]]
  [[ -s "$mount_point/Third-Party-Licenses/GPL-3.0.txt" ]]
  [[ -s "$mount_point/Third-Party-Licenses/Qt-PySide-NOTICE.txt" ]]
  [[ -s "$mount_point/Third-Party-Licenses/Microsoft-MarkItDown-MIT.txt" ]]
  grep -q 'PySide6' "$mount_point/Third-Party-Licenses/COMPONENTS.md"
  grep -q 'markitdown' "$mount_point/Third-Party-Licenses/COMPONENTS.md"
  grep -q '| Python |' "$mount_point/Third-Party-Licenses/COMPONENTS.md"
  grep -q '| PyInstaller bootloader |' "$mount_point/Third-Party-Licenses/COMPONENTS.md"
  find "$mount_point/Third-Party-Licenses" -path '*/python-*/PYTHON-LICENSE.txt' -type f | grep -q .
  find "$mount_point/Third-Party-Licenses" -path '*/pyinstaller-*/COPYING.txt' -type f | grep -q .

  local pyside_root="$mount_point/$app_name/Contents/Frameworks/PySide6"
  [[ -d "$pyside_root/Qt/lib/QtCore.framework" ]]
  [[ -d "$pyside_root/Qt/lib/QtGui.framework" ]]
  [[ -d "$pyside_root/Qt/lib/QtWidgets.framework" ]]
  if find "$pyside_root" \( -iname '*VirtualKeyboard*' -o -iname '*QtPdf*' \) | grep -q .; then
    echo "Unused Qt Virtual Keyboard/PDF component found in DMG: $app_name" >&2
    hdiutil detach "$mount_point" >/dev/null
    rmdir "$mount_point"
    return 1
  fi

  local plist="$mount_point/$app_name/Contents/Info.plist"
  [[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$plist")" == "$VERSION" ]]
  [[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist")" == "$expected_identifier" ]]

  hdiutil detach "$mount_point" >/dev/null
  rmdir "$mount_point"
}

verify_mounted_dmg "$KOREAN_DMG" "Batch Markdown Converter Korean.app" \
  "io.github.batchmarkdownconverter.korean"
verify_mounted_dmg "$ENGLISH_DMG" "Batch Markdown Converter English.app" \
  "io.github.batchmarkdownconverter.english"

echo "Release verification passed for Korean and English DMGs."
echo "Runtime, bootloader, and build-tool license bundle plus LGPL corresponding source verification passed."
