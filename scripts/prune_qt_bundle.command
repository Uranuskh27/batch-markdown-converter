#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
APP_PATH="${1:-}"

if [[ -z "$APP_PATH" ]]; then
  echo "Usage: $0 /path/to/App.app" >&2
  exit 2
fi

APP_PATH="${APP_PATH:A}"
if [[ "$APP_PATH" != "$PROJECT_DIR/build/dist/"*.app || ! -d "$APP_PATH" ]]; then
  echo "Refusing to prune outside build/dist: $APP_PATH" >&2
  exit 2
fi

PYSIDE_ROOT="$APP_PATH/Contents/Frameworks/PySide6"
QT_ROOT="$PYSIDE_ROOT/Qt"

required=(
  "$PYSIDE_ROOT/QtCore.abi3.so"
  "$PYSIDE_ROOT/QtGui.abi3.so"
  "$PYSIDE_ROOT/QtWidgets.abi3.so"
  "$QT_ROOT/lib/QtCore.framework"
  "$QT_ROOT/lib/QtGui.framework"
  "$QT_ROOT/lib/QtWidgets.framework"
)
for required_path in "${required[@]}"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Required Qt component is missing: $required_path" >&2
    exit 1
  fi
done

# These modules are pulled in by generic PyInstaller Qt hooks but are not used
# by this Widgets application. Qt Virtual Keyboard is GPL-only for community
# users, so keeping an unused copy would add unnecessary distribution terms.
targets=(
  "$PYSIDE_ROOT/QtNetwork.abi3.so"
  "$QT_ROOT/lib/QtNetwork.framework"
  "$QT_ROOT/lib/QtOpenGL.framework"
  "$QT_ROOT/lib/QtPdf.framework"
  "$QT_ROOT/lib/QtQml.framework"
  "$QT_ROOT/lib/QtQmlMeta.framework"
  "$QT_ROOT/lib/QtQmlModels.framework"
  "$QT_ROOT/lib/QtQmlWorkerScript.framework"
  "$QT_ROOT/lib/QtQuick.framework"
  "$QT_ROOT/lib/QtVirtualKeyboard.framework"
  "$QT_ROOT/lib/QtVirtualKeyboardQml.framework"
  "$QT_ROOT/plugins/generic"
  "$QT_ROOT/plugins/networkinformation"
  "$QT_ROOT/plugins/platforminputcontexts"
  "$QT_ROOT/plugins/tls"
  "$QT_ROOT/plugins/imageformats/libqpdf.dylib"
  "$QT_ROOT/qml"
)

for linked_name in \
  QtNetwork QtOpenGL QtPdf QtQml QtQmlMeta QtQmlModels QtQmlWorkerScript \
  QtQuick QtVirtualKeyboard QtVirtualKeyboardQml; do
  targets+=(
    "$APP_PATH/Contents/Frameworks/$linked_name"
    "$APP_PATH/Contents/Resources/$linked_name"
  )
done
targets+=("$APP_PATH/Contents/Resources/PySide6/QtNetwork.abi3.so")

rm -rf -- "${targets[@]}"

if find "$PYSIDE_ROOT" -iname '*VirtualKeyboard*' -o -iname '*QtPdf*' | grep -q .; then
  echo "Unused Qt Virtual Keyboard/PDF components remain after pruning." >&2
  exit 1
fi
if find -L "$APP_PATH" -type l | grep -q .; then
  echo "Broken symlinks remain after Qt pruning:" >&2
  find -L "$APP_PATH" -type l -print >&2
  exit 1
fi

echo "Pruned unused Qt modules from: $APP_PATH"
