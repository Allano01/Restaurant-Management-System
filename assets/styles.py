# ── Global colour palette ─────────────────────────────────────
COLORS = {
    "bg_primary":    "#0f1724",   # deepest background
    "bg_secondary":  "#1a2540",   # card/panel background
    "bg_tertiary":   "#1e2d4f",   # hover / elevated
    "sidebar":       "#0d1526",   # sidebar background
    "accent":        "#2563eb",   # primary blue accent
    "accent_hover":  "#1d4ed8",   # accent hover
    "accent_light":  "#3b82f6",   # lighter accent
    "success":       "#10b981",   # green
    "warning":       "#f59e0b",   # amber
    "danger":        "#ef4444",   # red
    "text_primary":  "#f1f5f9",   # main text
    "text_secondary":"#94a3b8",   # muted text
    "text_muted":    "#475569",   # very muted
    "border":        "#1e3a5f",   # subtle border
    "card_shadow":   "#0a1120",   # shadow tone
}

# ── Typography ────────────────────────────────────────────────
FONT_FAMILY   = "Segoe UI"
FONT_MONO     = "Consolas"

# ── Reusable stylesheets ──────────────────────────────────────
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
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {c['bg_primary']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {c['text_primary']};
            font-family: {FONT_FAMILY};
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {c['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
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
            padding: 10px 12px;
            border-bottom: 1px solid {c['border']};
        }}
        QTableWidget::item:selected {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
        }}
        QHeaderView::section {{
            background-color: {c['bg_primary']};
            color: {c['text_secondary']};
            padding: 12px;
            border: none;
            border-bottom: 2px solid {c['border']};
            font-weight: bold;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: {FONT_FAMILY};
        }}
        QScrollBar:vertical {{
            background: {c['bg_primary']};
            width: 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {c['border']};
            border-radius: 3px;
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QMessageBox {{
            background-color: {c['bg_secondary']};
            color: {c['text_primary']};
        }}
        QToolTip {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }}
    """

def primary_button(color=None):
    c = COLORS
    bg = color or c['accent']
    return f"""
        QPushButton {{
            background-color: {bg};
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            font-family: {FONT_FAMILY};
            padding: 0 20px;
        }}
        QPushButton:hover {{
            background-color: {c['accent_hover']};
        }}
        QPushButton:pressed {{
            background-color: {c['accent_light']};
        }}
        QPushButton:disabled {{
            background-color: {c['text_muted']};
            color: {c['text_secondary']};
        }}
    """

def icon_button(color):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {color};
            border: 1px solid {color};
            border-radius: 6px;
            font-size: 15px;
            padding: 2px 6px;
        }}
        QPushButton:hover {{
            background-color: {color};
            color: white;
        }}
    """

def card_style():
    c = COLORS
    return f"""
        QFrame {{
            background-color: {c['bg_secondary']};
            border-radius: 12px;
            border: 1px solid {c['border']};
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
            padding: 10px 20px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            border-radius: 0;
        }}
        QPushButton:hover {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
        }}
        QPushButton:checked {{
            background-color: {c['accent']};
            color: white;
            border-left: 3px solid {c['accent_light']};
        }}
    """