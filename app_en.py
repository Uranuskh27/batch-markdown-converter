from __future__ import annotations

import os

os.environ["BATCH_MARKDOWN_CONVERTER_LANGUAGE"] = "en"

from app import main


if __name__ == "__main__":
    raise SystemExit(main())
