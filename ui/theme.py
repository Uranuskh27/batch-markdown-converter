from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory


@dataclass(frozen=True, slots=True)
class ThemeColors:
    window: str
    surface: str
    surface_alt: str
    input: str
    text: str
    muted: str
    border: str
    accent: str
    accent_hover: str
    accent_pressed: str
    selection: str
    disabled_background: str
    disabled_text: str
    hover: str
    pressed: str
    progress_track: str
    danger: str
    success: str


LIGHT_COLORS = ThemeColors(
    window="#F5F7FA",
    surface="#FFFFFF",
    surface_alt="#EEF2F6",
    input="#FFFFFF",
    text="#182230",
    muted="#667085",
    border="#C7D0DB",
    accent="#1677FF",
    accent_hover="#0B66E4",
    accent_pressed="#0958C7",
    selection="#D9E9FF",
    disabled_background="#E6E9EE",
    disabled_text="#98A2B3",
    hover="#EAF2FF",
    pressed="#D8E8FF",
    progress_track="#DFE5EC",
    danger="#D92D20",
    success="#067647",
)

DARK_COLORS = ThemeColors(
    window="#171A1F",
    surface="#20242B",
    surface_alt="#292E37",
    input="#252A32",
    text="#F2F4F7",
    muted="#AEB7C4",
    border="#46505D",
    accent="#4C91FF",
    accent_hover="#6AA4FF",
    accent_pressed="#3279E6",
    selection="#244B78",
    disabled_background="#2A2F37",
    disabled_text="#727C89",
    hover="#303844",
    pressed="#394555",
    progress_track="#303640",
    danger="#FF6B5E",
    success="#47CD89",
)


def theme_colors(theme: str) -> ThemeColors:
    return DARK_COLORS if theme == "dark" else LIGHT_COLORS


def theme_palette(theme: str) -> QPalette:
    colors = theme_colors(theme)
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: colors.window,
        QPalette.ColorRole.WindowText: colors.text,
        QPalette.ColorRole.Base: colors.input,
        QPalette.ColorRole.AlternateBase: colors.surface_alt,
        QPalette.ColorRole.ToolTipBase: colors.surface_alt,
        QPalette.ColorRole.ToolTipText: colors.text,
        QPalette.ColorRole.Text: colors.text,
        QPalette.ColorRole.Button: colors.surface,
        QPalette.ColorRole.ButtonText: colors.text,
        QPalette.ColorRole.BrightText: colors.danger,
        QPalette.ColorRole.Link: colors.accent,
        QPalette.ColorRole.Highlight: colors.accent,
        QPalette.ColorRole.HighlightedText: "#FFFFFF",
        QPalette.ColorRole.PlaceholderText: colors.muted,
        QPalette.ColorRole.Mid: colors.border,
        QPalette.ColorRole.Dark: colors.border,
        QPalette.ColorRole.Light: colors.surface_alt,
        QPalette.ColorRole.Midlight: colors.surface_alt,
        QPalette.ColorRole.Shadow: "#000000",
    }
    for role, color in roles.items():
        palette.setColor(QPalette.ColorGroup.Active, role, QColor(color))
        palette.setColor(QPalette.ColorGroup.Inactive, role, QColor(color))

    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        palette.setColor(group, QPalette.ColorRole.LinkVisited, QColor(colors.accent))

    disabled_roles = {
        QPalette.ColorRole.Window: colors.window,
        QPalette.ColorRole.WindowText: colors.disabled_text,
        QPalette.ColorRole.Base: colors.disabled_background,
        QPalette.ColorRole.AlternateBase: colors.disabled_background,
        QPalette.ColorRole.Text: colors.disabled_text,
        QPalette.ColorRole.Button: colors.disabled_background,
        QPalette.ColorRole.ButtonText: colors.disabled_text,
        QPalette.ColorRole.PlaceholderText: colors.disabled_text,
        QPalette.ColorRole.Highlight: colors.border,
        QPalette.ColorRole.HighlightedText: colors.disabled_text,
    }
    for role, color in disabled_roles.items():
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(color))
    return palette


def theme_stylesheet(theme: str) -> str:
    c = theme_colors(theme)
    return f"""
        QWidget {{
            color: {c.text};
            selection-background-color: {c.accent};
            selection-color: #FFFFFF;
        }}
        QMainWindow, QDialog {{
            background-color: {c.window};
        }}
        QLabel {{
            background-color: transparent;
        }}
        QLabel#dropTitle {{
            font-size: 18px;
            font-weight: 600;
            color: {c.text};
        }}
        QLabel#dropSubtitle {{
            color: {c.muted};
        }}
        QLabel#outputPath {{
            min-height: 20px;
            padding: 4px 8px;
            color: {c.muted};
            background-color: {c.surface_alt};
            border: 1px solid {c.border};
            border-radius: 6px;
        }}
        QLabel#outputPath[needsSelection="true"] {{
            color: {c.text};
            border-color: {c.accent};
            background-color: {c.hover};
        }}
        QLabel#progressEndpoint {{
            font-size: 22px;
            padding: 0 2px;
            min-width: 24px;
        }}
        QFrame#dropZone {{
            border: 2px dashed {c.border};
            border-radius: 12px;
            background-color: {c.surface};
        }}
        QFrame#dropZone[active="true"] {{
            border-color: {c.accent};
            background-color: {c.selection};
        }}
        QPushButton {{
            min-height: 22px;
            padding: 5px 10px;
            color: {c.text};
            background-color: {c.surface};
            border: 1px solid {c.border};
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background-color: {c.hover};
            border-color: {c.accent};
        }}
        QPushButton:pressed {{
            background-color: {c.pressed};
            border-color: {c.accent_pressed};
        }}
        QPushButton:focus {{
            border: 2px solid {c.accent};
        }}
        QPushButton:disabled {{
            color: {c.disabled_text};
            background-color: {c.disabled_background};
            border-color: {c.border};
        }}
        QPushButton#primaryButton {{
            color: #FFFFFF;
            background-color: {c.accent};
            border-color: {c.accent};
            padding: 6px 14px;
            font-weight: 600;
        }}
        QPushButton#primaryButton:hover {{
            background-color: {c.accent_hover};
            border-color: {c.accent_hover};
        }}
        QPushButton#primaryButton:pressed {{
            background-color: {c.accent_pressed};
            border-color: {c.accent_pressed};
        }}
        QPushButton#primaryButton:disabled {{
            color: {c.disabled_text};
            background-color: {c.disabled_background};
            border-color: {c.border};
        }}
        QComboBox, QSpinBox, QLineEdit {{
            min-height: 24px;
            padding: 3px 8px;
            color: {c.text};
            background-color: {c.input};
            border: 1px solid {c.border};
            border-radius: 5px;
        }}
        QComboBox:hover, QSpinBox:hover, QLineEdit:hover {{
            border-color: {c.accent};
        }}
        QComboBox:focus, QSpinBox:focus, QLineEdit:focus {{
            border: 2px solid {c.accent};
        }}
        QComboBox:disabled, QSpinBox:disabled, QLineEdit:disabled {{
            color: {c.disabled_text};
            background-color: {c.disabled_background};
        }}
        QComboBox QAbstractItemView {{
            color: {c.text};
            background-color: {c.surface};
            border: 1px solid {c.border};
            selection-background-color: {c.accent};
            selection-color: #FFFFFF;
            outline: none;
        }}
        QCheckBox {{
            spacing: 7px;
            color: {c.text};
            background-color: transparent;
        }}
        QCheckBox:disabled {{
            color: {c.disabled_text};
        }}
        QTableView {{
            color: {c.text};
            background-color: {c.surface};
            alternate-background-color: {c.surface_alt};
            gridline-color: {c.border};
            border: 1px solid {c.border};
            selection-background-color: {c.selection};
            selection-color: {c.text};
            outline: none;
        }}
        QHeaderView::section {{
            color: {c.text};
            background-color: {c.surface_alt};
            border: none;
            border-right: 1px solid {c.border};
            border-bottom: 1px solid {c.border};
            padding: 5px 8px;
            font-weight: 600;
        }}
        QProgressBar#dogProgress {{
            min-height: 44px;
            max-height: 44px;
            color: {c.text};
            background-color: transparent;
            border: none;
        }}
        QScrollBar:vertical {{
            width: 12px;
            margin: 0;
            background-color: {c.surface_alt};
            border: none;
        }}
        QScrollBar:horizontal {{
            height: 12px;
            margin: 0;
            background-color: {c.surface_alt};
            border: none;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            min-height: 24px;
            min-width: 24px;
            background-color: {c.border};
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
            background-color: {c.accent};
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            width: 0;
            height: 0;
            border: none;
        }}
        QStatusBar {{
            color: {c.text};
            background-color: {c.window};
            border-top: 1px solid {c.border};
        }}
        QStatusBar::item {{
            border: none;
        }}
        QToolTip {{
            color: {c.text};
            background-color: {c.surface_alt};
            border: 1px solid {c.border};
            padding: 4px;
        }}
    """


def apply_theme(application: QApplication, theme: str) -> None:
    if application.property("batchMarkdownConverterBaseStyle") != "Fusion":
        fusion = QStyleFactory.create("Fusion")
        if fusion is not None:
            application.setStyle(fusion)
            application.setProperty("batchMarkdownConverterBaseStyle", "Fusion")
    application.setProperty("batchMarkdownConverterTheme", "dark" if theme == "dark" else "light")
    application.setPalette(theme_palette(theme))
    application.setStyleSheet(theme_stylesheet(theme))


def status_foreground(status_name: str) -> QColor:
    application = QApplication.instance()
    theme = application.property("batchMarkdownConverterTheme") if application is not None else "light"
    colors = theme_colors("dark" if theme == "dark" else "light")
    if status_name == "DONE":
        return QColor(colors.success)
    if status_name in {"FAILED", "SKIPPED"}:
        return QColor(colors.danger)
    return QColor(colors.muted)
