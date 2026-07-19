from __future__ import annotations

import json
import sys
import time
from pathlib import Path


def main() -> int:
    source = Path(sys.argv[-2])
    destination = Path(sys.argv[-1])
    command = source.read_text(encoding="utf-8")
    if command.startswith("sleep"):
        time.sleep(10)
    if command.startswith("fail"):
        print(json.dumps({"ok": False, "error": "의도된 Worker 실패"}, ensure_ascii=False))
        return 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(command, encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(destination)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
