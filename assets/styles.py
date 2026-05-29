# ── Global colour palette ─────────────────────────────────────
COLORS = {
    "bg_primary":    "#f8fafc",
    "bg_secondary":  "#ffffff",
    "bg_tertiary":   "#f1f5f9",
    "sidebar":       "#ffffff",
    "sidebar_active":"#f0fdf4",
    "accent":        "#16a34a",
    "accent_hover":  "#15803d",
    "accent_light":  "#dcfce7",
    "accent_text":   "#166534",
    "purple":        "#7c3aed",
    "purple_light":  "#ede9fe",
    "blue":          "#2563eb",
    "blue_light":    "#dbeafe",
    "orange":        "#ea580c",
    "orange_light":  "#ffedd5",
    "success":       "#16a34a",
    "warning":       "#d97706",
    "danger":        "#dc2626",
    "danger_light":  "#fee2e2",
    "text_primary":  "#0f172a",
    "text_secondary":"#475569",
    "text_muted":    "#94a3b8",
    "border":        "#e2e8f0",
    "border_strong": "#cbd5e1",
    "white":         "#ffffff",
    "shadow":        "rgba(0,0,0,0.06)",
}

FONT_FAMILY = "Segoe UI"


def app_stylesheet():
    c = COLORS
    return f"""
        QMainWindow, QWidget {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
            font-family: {FONT_FAMILY};
        }}
        QDialog {{
            background-color: {c['bg_secondary']};
            color: {c['text_primary']};
            font-family: {FONT_FAMILY};
        }}
        QLabel {{
            color: {c['text_primary']};
            font-family: {FONT_FAMILY};
            background: transparent;
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {c['bg_secondary']};
            border: 1.5px solid {c['border']};
            border-radius: 8px;
            padding: 8px 12px;
            color: {c['text_primary']};
            font-family: {FONT_FAMILY};
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1.5px solid {c['accent']};
            outline: none;
        }}
        QLineEdit:hover, QComboBox:hover {{
            border: 1.5px solid {c['border_strong']};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['bg_secondary']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            selection-background-color: {c['accent_light']};
            selection-color: {c['accent_text']};
            padding: 4px;
        }}
        QTableWidget {{
            background-color: {c['bg_secondary']};
            color: {c['text_primary']};
            border: none;
            gridline-color: {c['border']};
            font-family: {FONT_FAMILY};
            font-size: 13px;
            outline: none;
        }}
        QTableWidget::item {{
            padding: 12px 14px;
            border-bottom: 1px solid {c['border']};
            color: {c['text_primary']};
        }}
        QTableWidget::item:selected {{
            background-color: {c['accent_light']};
            color: {c['accent_text']};
        }}
        QHeaderView::section {{
            background-color: {c['bg_tertiary']};
            color: {c['text_secondary']};
            padding: 12px 14px;
            border: none;
            border-bottom: 2px solid {c['border']};
            font-weight: bold;
            font-size: 11px;
            font-family: {FONT_FAMILY};
            letter-spacing: 0.5px;
        }}
        QScrollBar:vertical {{
            background: {c['bg_tertiary']};
            width: 6px;
            border-radius: 3px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {c['border_strong']};
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar:horizontal {{
            background: {c['bg_tertiary']};
            height: 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c['border_strong']};
            border-radius: 3px;
        }}
        QToolTip {{
            background-color: {c['text_primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
            font-family: {FONT_FAMILY};
        }}
        QMessageBox {{
            background-color: {c['bg_secondary']};
            color: {c['text_primary']};
        }}
        QMenuBar {{
            background-color: {c['bg_secondary']};
        }}
    """


def primary_button(color=None, text_color="white"):
    c = COLORS
    bg = color or c['accent']
    hover = c['accent_hover'] if bg == c['accent'] else bg
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text_color};
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
            padding: 0 20px;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
        QPushButton:pressed {{
            background-color: {bg};
            opacity: 0.9;
        }}
        QPushButton:disabled {{
            background-color: {c['border']};
            color: {c['text_muted']};
        }}
    """


def outline_button(color=None):
    c = COLORS
    col = color or c['accent']
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {col};
            border: 1.5px solid {col};
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
            padding: 0 16px;
        }}
        QPushButton:hover {{
            background-color: {c['accent_light']};
        }}
    """


def icon_button(color):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {color};
            border: none;
            border-radius: 6px;
            font-size: 16px;
            padding: 4px 8px;
            font-family: {FONT_FAMILY};
        }}
        QPushButton:hover {{
            background-color: rgba(0,0,0,0.06);
        }}
    """


def sidebar_button_style():
    c = COLORS
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {c['text_secondary']};
            border: none;
            text-align: left;
            padding: 10px 16px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            border-radius: 8px;
            margin: 1px 8px;
        }}
        QPushButton:hover {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
        }}
        QPushButton:checked {{
            background-color: {c['accent_light']};
            color: {c['accent_text']};
            font-weight: 600;
        }}
    """


def badge_style(bg, text_color):
    return f"""
        QLabel {{
            background-color: {bg};
            color: {text_color};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 11px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}
    """