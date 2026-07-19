#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
export PYINSTALLER_CONFIG_DIR="$PROJECT_DIR/.pyinstaller-cache"
mkdir -p "$PYINSTALLER_CONFIG_DIR"
cd "$PROJECT_DIR/build"
"$PROJECT_DIR/.venv/bin/pyinstaller" --noconfirm --clean batch-markdown-converter.spec
"$PROJECT_DIR/scripts/prune_qt_bundle.command" "$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"
codesign --remove-signature "$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app" 2>/dev/null || true
SIGNING_IDENTITY="${SIGNING_IDENTITY:--}"
if [[ "$SIGNING_IDENTITY" == "-" ]]; then
  codesign --force --deep --sign - "$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"
else
  codesign --force --deep --options runtime --timestamp \
    --sign "$SIGNING_IDENTITY" "$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"
fi
codesign --verify --deep --strict "$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"

echo
echo "앱 생성 완료: $PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"
if [[ -t 0 ]]; then
  open -R "$PROJECT_DIR/build/dist/Batch Markdown Converter Korean.app"
fi
