#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
VERSION="$(<"$PROJECT_DIR/VERSION")"
QT_VERSION="$(<"$PROJECT_DIR/QT_VERSION")"
UPLOAD_DIR="$PROJECT_DIR/release/GitHub-Upload-Korean"
TAG="${RELEASE_TAG:-v$VERSION}"
DMG_NAME="Batch-Markdown-Converter-Korean-$VERSION-arm64.dmg"
PYSIDE_SOURCE="pyside-setup-everywhere-src-$QT_VERSION.tar.xz"
QTBASE_SOURCE="qtbase-everywhere-src-$QT_VERSION.tar.xz"
QTSVG_SOURCE="qtsvg-everywhere-src-$QT_VERSION.tar.xz"
GH_REPO_ARGS=()

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI가 필요합니다. 설치: brew install gh" >&2
  echo "설치 후 로그인: gh auth login" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI에 로그인되지 않았습니다. gh auth login을 실행하세요." >&2
  exit 1
fi

if [[ "$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || true)" != "$PROJECT_DIR" ]]; then
  echo "이 프로젝트가 독립 Git 저장소가 아닙니다." >&2
  exit 1
fi

if ! git -C "$PROJECT_DIR" rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "Release 게시 전에 공개 소스를 커밋하고 푸시하세요." >&2
  exit 1
fi

if [[ -n "$(git -C "$PROJECT_DIR" status --porcelain)" ]]; then
  echo "커밋하지 않은 변경이 있습니다. 먼저 커밋하세요." >&2
  exit 1
fi

if [[ -n "${GITHUB_REPOSITORY:-}" ]]; then
  GH_REPO_ARGS=(--repo "$GITHUB_REPOSITORY")
elif ! git -C "$PROJECT_DIR" remote get-url origin >/dev/null 2>&1; then
  echo "origin이 없으면 GITHUB_REPOSITORY=소유자/저장소를 지정하세요." >&2
  exit 1
fi

if (cd "$PROJECT_DIR"; gh release view "$TAG" "${GH_REPO_ARGS[@]}" >/dev/null 2>&1); then
  echo "GitHub Release $TAG가 이미 존재합니다. 업로드하지 않았습니다." >&2
  exit 1
fi

"$PROJECT_DIR/scripts/prepare_korean_github_release.command"

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
  echo "detached HEAD가 아닌 이름이 있는 브랜치에서 게시하세요." >&2
  exit 1
fi

(
  cd "$PROJECT_DIR"
  gh release create "$TAG" "${ASSETS[@]}" "${GH_REPO_ARGS[@]}" \
    --target "$CURRENT_BRANCH" \
    --title "Batch Markdown Converter $VERSION 한국어판" \
    --notes-file "$PROJECT_DIR/RELEASE_NOTES.ko.md"
)

echo "한글판 바이너리와 LGPL 소스를 포함한 GitHub Release $TAG를 게시했습니다."
