# Batch Markdown Converter 0.1.0

Initial public release of the English macOS app.

## Highlights

- Batch-convert files and folders to Markdown by drag and drop.
- Keep each conversion isolated so one problematic file does not stop the queue.
- Choose one output folder and see the exact save location in the main window.
- Handle filename collisions by renaming, skipping, or overwriting.
- Switch between light and dark themes.
- Optionally open completed output folders in Finder.
- Track progress with the animated running-dog progress bar.

## Compatibility

- macOS 13 Ventura or later
- Apple Silicon (arm64)

## Installation

Download the English DMG, verify its SHA-256 checksum, open it, and drag
`Batch Markdown Converter English.app` into Applications.

This build is ad-hoc signed and is not notarized by Apple. macOS may show a Gatekeeper warning on
first launch. If the checksum matches the official Release asset, Control-click the installed app in
Finder and choose **Open**.

## Open-source notice

This independent project is not an official Microsoft product. The Release includes the exact
LGPL-covered PySide6/Qt corresponding-source archives and their checksums alongside the application.
