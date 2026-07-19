from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch Markdown Converter")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("source", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("destination", nargs="?", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))

    if args.worker:
        if not args.source or not args.destination:
            return 2
        from core.worker_entry import worker_main

        return worker_main(args.source, args.destination)

    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication

    from core.config import AppSettings
    from core.i18n import application_display_name, application_settings_name
    from core.process_manager import JobManager
    from ui.main_window import MainWindow
    from ui.theme import apply_theme

    QCoreApplication.setOrganizationName("LocalTools")
    QCoreApplication.setApplicationName(application_settings_name())
    application = QApplication(sys.argv[:1])
    application.setApplicationDisplayName(application_display_name())

    settings = AppSettings()
    apply_theme(application, settings.theme)
    manager = JobManager(settings, Path(__file__).resolve())
    window = MainWindow(manager, settings)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
