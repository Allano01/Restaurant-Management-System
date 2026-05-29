from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QGraphicsDropShadowEffect, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from services.menu_service import get_dashboard_stats
from assets.styles import COLORS, app_stylesheet, primary_button, sidebar_button_style


class StatCard(QFrame):
    def __init__(self, title, value, subtitle, icon, accent_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {accent_color};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        top_row = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 18))
        icon_label.setStyleSheet(f"color: {accent_color}; background: transparent; border: none;")

        title_label = QLabel(title.upper())
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; "
            f"border: none; letter-spacing: 1px;"
        )
        top_row.addWidget(icon_label)
        top_row.addWidget(title_label)
        top_row.addStretch()

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        value_label.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent; border: none;"
        )

        sub_label = QLabel(subtitle)
        sub_label.setFont(QFont("Segoe UI", 10))
        sub_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; background: transparent; border: none;"
        )

        layout.addLayout(top_row)
        layout.addWidget(value_label)
        layout.addWidget(sub_label)


class DashboardHome(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(60000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()
        left_header = QVBoxLayout()

        page_title = QLabel("Dashboard")
        page_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        page_title.setStyleSheet(f"color: {COLORS['text_primary']};")

        import datetime
        date_str = datetime.datetime.now().strftime("%A, %d %B %Y")
        date_label = QLabel(date_str)
        date_label.setFont(QFont("Segoe UI", 11))
        date_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        left_header.addWidget(page_title)
        left_header.addWidget(date_label)

        welcome_badge = QLabel(
            f"👤  {self.user['full_name']}  •  {self.user['role']}"
        )
        welcome_badge.setFont(QFont("Segoe UI", 11))
        welcome_badge.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 20px;
            padding: 6px 16px;
        """)

        header.addLayout(left_header)
        header.addStretch()
        header.addWidget(welcome_badge)

        overview_label = QLabel("OVERVIEW")
        overview_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        overview_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; letter-spacing: 2px;"
        )

        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(16)
        self.load_stats()

        actions_label = QLabel("QUICK ACTIONS")
        actions_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        actions_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; letter-spacing: 2px;"
        )

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        for label, color, tooltip in [
            ("🛒  New Order",     COLORS['accent'],   "Start a new customer order"),
            ("🍽  View Menu",     COLORS['success'],  "Browse and manage menu"),
            ("📊  Sales Report",  "#8b5cf6",          "View today's performance"),
            ("👥  Manage Users",  COLORS['warning'],  "User and role management"),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(48)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: bold;
                    font-family: Segoe UI;
                    padding: 0 20px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    border-color: {color};
                    color: white;
                }}
            """)
            actions_row.addWidget(btn)

        activity_label = QLabel("SYSTEM STATUS")
        activity_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        activity_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; letter-spacing: 2px;"
        )

        status_card = QFrame()
        status_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(20, 16, 20, 16)
        status_layout.setSpacing(32)

        for icon, label, value, color in [
            ("🟢", "Database", "Connected",               COLORS['success']),
            ("🟢", "System",   "Online",                  COLORS['success']),
            ("📅", "Session",  f"{self.user['role']} active", COLORS['accent']),
        ]:
            item_layout = QVBoxLayout()
            top = QLabel(f"{icon}  {label}")
            top.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            top.setStyleSheet(
                f"color: {COLORS['text_secondary']}; background: transparent;"
            )
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 12))
            val.setStyleSheet(f"color: {color}; background: transparent;")
            item_layout.addWidget(top)
            item_layout.addWidget(val)
            status_layout.addLayout(item_layout)

        status_layout.addStretch()

        layout.addLayout(header)
        layout.addWidget(overview_label)
        layout.addLayout(self.cards_row)
        layout.addWidget(actions_label)
        layout.addLayout(actions_row)
        layout.addWidget(activity_label)
        layout.addWidget(status_card)
        layout.addStretch()

    def load_stats(self):
        while self.cards_row.count():
            item = self.cards_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stats = get_dashboard_stats()
        for title, value, subtitle, icon, color in [
            ("Sales Today",  f"${stats['sales_today']:.2f}", "Total revenue",     "💰", COLORS['accent']),
            ("Orders Today", str(stats['orders_today']),     "Completed orders",  "🛒", COLORS['success']),
            ("Menu Items",   str(stats['active_items']),     "Available items",   "🍽", "#8b5cf6"),
            ("Categories",   str(stats['active_categories']),"Active categories", "📂", COLORS['warning']),
        ]:
            self.cards_row.addWidget(StatCard(title, value, subtitle, icon, color))
        self.cards_row.addStretch()

    def refresh_stats(self):
        self.load_stats()
class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Restaurant Management System")
        self.setMinimumSize(1200, 720)
        self.setStyleSheet(app_stylesheet())
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(
            f"background-color: {COLORS['sidebar']};"
            f"border-right: 1px solid {COLORS['border']};"
        )
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand header
        brand_frame = QFrame()
        brand_frame.setFixedHeight(72)
        brand_frame.setStyleSheet(
            f"background-color: {COLORS['sidebar']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 0, 20, 0)

        brand_icon = QLabel("🍽")
        brand_icon.setFont(QFont("Segoe UI", 22))
        brand_icon.setStyleSheet("background: transparent; border: none;")

        brand_text_layout = QVBoxLayout()
        brand_name = QLabel("RestaurantPro")
        brand_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        brand_name.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent; border: none;"
        )
        brand_ver = QLabel("v1.0  •  Enterprise")
        brand_ver.setFont(QFont("Segoe UI", 9))
        brand_ver.setStyleSheet(
            f"color: {COLORS['text_muted']}; background: transparent; border: none;"
        )
        brand_text_layout.addWidget(brand_name)
        brand_text_layout.addWidget(brand_ver)

        brand_layout.addWidget(brand_icon)
        brand_layout.addLayout(brand_text_layout)
        sidebar_layout.addWidget(brand_frame)

        # Section label helper
        def section_label(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setStyleSheet(
                f"color: {COLORS['text_muted']}; padding: 16px 20px 6px 20px;"
                f"letter-spacing: 1px; background: transparent;"
            )
            return lbl

        sidebar_layout.addWidget(section_label("MAIN MENU"))

        self.nav_buttons = []
        for icon, label, index in [
            ("🏠", "Dashboard",       0),
            ("🍽", "Menu Management", 1),
            ("🛒", "Point of Sale",   2),
            ("🪑", "Table Manager",   3),
            ("👨‍🍳", "Kitchen Display", 4),
            ("📦", "Inventory",       5),
        ]:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setFixedHeight(46)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(sidebar_button_style())
            btn.clicked.connect(lambda _, i=index: self.navigate(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addWidget(section_label("MANAGEMENT"))

        for icon, label, index in [
            ("📊", "Reports",  6),
            ("⚙️",  "Settings", 7),
        ]:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setFixedHeight(46)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(sidebar_button_style())
            btn.clicked.connect(lambda _, i=index: self.navigate(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # User profile at bottom
        profile_card = QFrame()
        profile_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setContentsMargins(16, 12, 16, 12)
        profile_layout.setSpacing(6)

        profile_top = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setFont(QFont("Segoe UI", 20))
        avatar.setStyleSheet("background: transparent; border: none;")
        avatar.setFixedSize(36, 36)

        profile_text = QVBoxLayout()
        name_lbl = QLabel(self.user['full_name'])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        name_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent; border: none;"
        )
        role_lbl = QLabel(self.user['role'])
        role_lbl.setFont(QFont("Segoe UI", 9))
        role_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; background: transparent; border: none;"
        )
        profile_text.addWidget(name_lbl)
        profile_text.addWidget(role_lbl)

        profile_top.addWidget(avatar)
        profile_top.addLayout(profile_text)
        profile_top.addStretch()

        logout_btn = QPushButton("⏻  Logout")
        logout_btn.setFixedHeight(34)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['danger']};
                border: 1px solid {COLORS['danger']};
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: white;
            }}
        """)
        logout_btn.clicked.connect(self.logout)

        profile_layout.addLayout(profile_top)
        profile_layout.addWidget(logout_btn)
        sidebar_layout.addWidget(profile_card)

        # ── Content stack ─────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLORS['bg_primary']};")

        # Page 0 — Dashboard
        self.stack.addWidget(DashboardHome(self.user))

        # Page 1 — Menu Management
        from ui.menu_management import MenuManagementWidget
        self.stack.addWidget(MenuManagementWidget(self.user))

        # Pages 2-7 — Placeholders
        for name in ["Point of Sale", "Table Manager", "Kitchen Display",
                     "Inventory", "Reports", "Settings"]:
            ph = QLabel(f"{name}\n\nComing in next phase")
            ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ph.setFont(QFont("Segoe UI", 16))
            ph.setStyleSheet(f"color: {COLORS['text_muted']};")
            self.stack.addWidget(ph)

        root.addWidget(sidebar)
        root.addWidget(self.stack)

        self.navigate(0)

    def navigate(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from ui.login_window import LoginWindow
            self.login = LoginWindow()
            self.login.show()
            self.close()