#!/bin/zsh
set -euo pipefail
setopt null_glob

PROJECT_DIR="${0:A:h:h}"
VERSION="$(<"$PROJECT_DIR/VERSION")"
RELEASE_ROOT="$PROJECT_DIR/release"
KOREAN_DIR="$RELEASE_ROOT/Korean"
ENGLISH_DIR="$RELEASE_ROOT/English"
KOREAN_APP="$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"
ENGLISH_APP="$PROJECT_DIR/build/dist/Batch Markdown Converter English.app"
SIGNING_IDENTITY="${SIGNING_IDENTITY:--}"
NOTARY_PROFILE="${NOTARY_PROFILE:-}"
export SIGNING_IDENTITY

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
  "$PROJECT_DIR/scripts/build_app.command"
  "$PROJECT_DIR/scripts/build_english_app.command"
fi

if [[ "${PREPARE_LGPL_SOURCES:-1}" == "1" ]]; then
  "$PROJECT_DIR/scripts/prepare_lgpl_sources.command"
fi
if [[ ! -f "$RELEASE_ROOT/Source-Code/SHA256SUMS.txt" ]]; then
  echo "Missing LGPL corresponding source. Run scripts/prepare_lgpl_sources.command." >&2
  exit 1
fi

for app in "$KOREAN_APP" "$ENGLISH_APP"; do
  if [[ ! -d "$app" ]]; then
    echo "Missing app bundle: $app" >&2
    exit 1
  fi
  codesign --verify --deep --strict "$app"
  APP_VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$app/Contents/Info.plist")"
  if [[ "$APP_VERSION" != "$VERSION" ]]; then
    echo "App version $APP_VERSION does not match VERSION $VERSION: $app" >&2
    exit 1
  fi
done

mkdir -p "$KOREAN_DIR" "$ENGLISH_DIR" "$PROJECT_DIR/.build"
STAGING_ROOT="$(mktemp -d "$PROJECT_DIR/.build/release.XXXXXX")"
trap 'rm -rf "$STAGING_ROOT"' EXIT

package_one() {
  local app="$1"
  local release_dir="$2"
  local dmg_name="$3"
  local volume_name="$4"
  local readme="$5"
  local stage="$STAGING_ROOT/$volume_name"
  local dmg="$release_dir/$dmg_name"

  mkdir -p "$stage"
  ditto "$app" "$stage/${app:t}"
  ln -s /Applications "$stage/Applications"
  ditto "$readme" "$stage/README.txt"
  ditto "$PROJECT_DIR/LICENSE" "$stage/LICENSE.txt"
  ditto "$PROJECT_DIR/THIRD_PARTY_NOTICES.md" "$stage/THIRD_PARTY_NOTICES.md"
  ditto "$PROJECT_DIR/COMPLIANCE.md" "$stage/COMPLIANCE.md"
  ditto "$PROJECT_DIR/BUILD_AND_RELINK.md" "$stage/BUILD_AND_RELINK.md"
  ditto "$PROJECT_DIR/licenses/SOURCE_OFFER.md" "$stage/SOURCE_OFFER.md"
  ditto "$RELEASE_ROOT/Source-Code/SHA256SUMS.txt" "$stage/LGPL_SOURCE_SHA256SUMS.txt"
  "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/scripts/generate_license_bundle.py" \
    "$stage/Third-Party-Licenses"

  hdiutil create -ov -fs HFS+ -format UDZO -imagekey zlib-level=9 \
    -volname "$volume_name" -srcfolder "$stage" "$dmg"

  if [[ "$SIGNING_IDENTITY" != "-" ]]; then
    codesign --force --timestamp --sign "$SIGNING_IDENTITY" "$dmg"
  fi
}

KOREAN_DMG="Batch-Markdown-Converter-Korean-$VERSION-arm64.dmg"
ENGLISH_DMG="Batch-Markdown-Converter-English-$VERSION-arm64.dmg"

package_one "$KOREAN_APP" "$KOREAN_DIR" "$KOREAN_DMG" \
  "Batch Markdown Converter Korean $VERSION" "$KOREAN_DIR/README.txt"
package_one "$ENGLISH_APP" "$ENGLISH_DIR" "$ENGLISH_DMG" \
  "Batch Markdown Converter English $VERSION" "$ENGLISH_DIR/README.txt"

if [[ -n "$NOTARY_PROFILE" ]]; then
  if [[ "$SIGNING_IDENTITY" == "-" ]]; then
    echo "NOTARY_PROFILE requires a Developer ID SIGNING_IDENTITY." >&2
    exit 1
  fi
  for dmg in "$KOREAN_DIR/$KOREAN_DMG" "$ENGLISH_DIR/$ENGLISH_DMG"; do
    xcrun notarytool submit "$dmg" --keychain-profile "$NOTARY_PROFILE" --wait
    xcrun stapler staple "$dmg"
    xcrun stapler validate "$dmg"
  done
fi

(
  cd "$KOREAN_DIR"
  shasum -a 256 "$KOREAN_DMG" > SHA256SUMS.txt
)
(
  cd "$ENGLISH_DIR"
  shasum -a 256 "$ENGLISH_DMG" > SHA256SUMS.txt
)

echo
echo "Korean release: $KOREAN_DIR"
echo "English release: $ENGLISH_DIR"
if [[ "$SIGNING_IDENTITY" == "-" ]]; then
  echo "Status: ad-hoc signed and not notarized (local/test distribution)"
elif [[ -z "$NOTARY_PROFILE" ]]; then
  echo "Status: Developer ID signed but not notarized"
else
  echo "Status: Developer ID signed and notarized"
fi
echo "LGPL source: $RELEASE_ROOT/Source-Code (upload every file with the DMGs)"
