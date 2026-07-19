#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
VERSION="$(<"$PROJECT_DIR/VERSION")"
QT_VERSION="$(<"$PROJECT_DIR/QT_VERSION")"
UPLOAD_DIR="$PROJECT_DIR/release/GitHub-Upload-English"
TAG="${RELEASE_TAG:-v$VERSION}"
DMG_NAME="Batch-Markdown-Converter-English-$VERSION-arm64.dmg"
PYSIDE_SOURCE="pyside-setup-everywhere-src-$QT_VERSION.tar.xz"
QTBASE_SOURCE="qtbase-everywhere-src-$QT_VERSION.tar.xz"
QTSVG_SOURCE="qtsvg-everywhere-src-$QT_VERSION.tar.xz"
GH_REPO_ARGS=()

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is required. Install it with: brew install gh" >&2
  echo "Then sign in with: gh auth login" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not signed in. Run: gh auth login" >&2
  exit 1
fi

if [[ "$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || true)" != "$PROJECT_DIR" ]]; then
  echo "This project is not an independent Git repository." >&2
  exit 1
fi

if ! git -C "$PROJECT_DIR" rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "Commit and push the public source before publishing a Release." >&2
  exit 1
fi

if [[ -n "$(git -C "$PROJECT_DIR" status --porcelain)" ]]; then
  echo "The Git working tree has uncommitted changes. Commit them before publishing." >&2
  exit 1
fi

if [[ -n "${GITHUB_REPOSITORY:-}" ]]; then
  GH_REPO_ARGS=(--repo "$GITHUB_REPOSITORY")
elif ! git -C "$PROJECT_DIR" remote get-url origin >/dev/null 2>&1; then
  echo "No origin is configured. Set GITHUB_REPOSITORY=owner/repository." >&2
  exit 1
fi

if (cd "$PROJECT_DIR"; gh release view "$TAG" "${GH_REPO_ARGS[@]}" >/dev/null 2>&1); then
  echo "GitHub Release $TAG already exists. No files were uploaded." >&2
  exit 1
fi

"$PROJECT_DIR/scripts/prepare_english_github_release.command"

ASSETS=(
  "$UPLOAD_DIR/$DMG_NAME"
  "$UPLOAD_DIR/$DMG_NAME.sha256.txt"
  "$UPLOAD_DIR/$PYSIDE_SOURCE"
  "$UPLOAD_DIR/$QTBASE_SOURCE"
  "$UPLOAD_DIR/$QTSVG_SOURCE"
  "$UPLOAD_DIR/LGPL-Sources-SHA256SUMS.txt"
)

CURRENT_BRANCH="$(git -C "$PROJECT_DIR" branch --show-current)"
if [[ -z "$CURRENT_BRANCH" ]]; then
  echo "Publish from a named Git branch, not a detached HEAD." >&2
  exit 1
fi

(
  cd "$PROJECT_DIR"
  gh release create "$TAG" "${ASSETS[@]}" "${GH_REPO_ARGS[@]}" \
    --target "$CURRENT_BRANCH" \
    --title "Batch Markdown Converter $VERSION" \
    --notes-file "$PROJECT_DIR/RELEASE_NOTES.md"
)

echo "Published GitHub Release $TAG with every required English binary and LGPL source asset."
