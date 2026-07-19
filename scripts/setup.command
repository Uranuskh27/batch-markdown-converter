#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h:h}"
PYTHON_BIN="/opt/homebrew/bin/python3.12"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python 3.12를 찾을 수 없습니다: $PYTHON_BIN"
  exit 1
fi

cd "$PROJECT_DIR"
"$PYTHON_BIN" -m venv .venv
"$PROJECT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$PROJECT_DIR/.venv/bin/python" -m pip install -e '.[test,build]'

echo
echo "설치 완료. scripts/run.command를 실행하세요."
if [[ -t 0 ]]; then
  read -k 1 "?이 창을 닫으려면 아무 키나 누르세요."
fi
