from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
    QTabWidget, QMenu, QCheckBox, QFileDialog,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QCursor
from services.admin_service import (
    get_all_users, get_all_roles, create_user,
    update_user, reset_user_password,
    toggle_user_status, get_all_settings,
    save_setting, get_audit_logs, backup_database
)
from assets.styles import COLORS, primary_button, outline_button


# ── User dialog ───────────────────────────────────────────────
class UserDialog(QDialog):
    def __init__(self, parent=None,
                 user=None, roles=None):
        super().__init__(parent)
        self.user  = user
        self.roles = roles or []
        self.setWindowTitle(
            "Edit User" if user else "Create User"
        )
        self.setFixedSize(420, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text_primary']};
                font-family: Segoe UI;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel(
            "Edit User" if self.user else "Create New User"
        )
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        form = QFormLayout()
        form.setSpacing(12)

        input_style = f"""
            QLineEdit, QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.username_input  = QLineEdit()
        self.fullname_input  = QLineEdit()
        self.email_input     = QLineEdit()
        self.password_input  = QLineEdit()
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        for widget, placeholder in [
            (self.username_input, "e.g. jkamau"),
            (self.fullname_input, "e.g. John Kamau"),
            (self.email_input,    "e.g. john@restaurant.com"),
            (self.password_input, "Enter password"),
        ]:
            widget.setPlaceholderText(placeholder)
            widget.setFixedHeight(40)
            widget.setStyleSheet(input_style)

        self.role_combo = QComboBox()
        self.role_combo.setFixedHeight(40)
        self.role_combo.setStyleSheet(input_style)
        for role in self.roles:
            self.role_combo.addItem(role[1], role[0])

        fields = [
            ("Username *",  self.username_input),
            ("Full Name *", self.fullname_input),
            ("Email",       self.email_input),
            ("Role *",      self.role_combo),
        ]
        if not self.user:
            fields.append(("Password *", self.password_input))

        for lbl, widget in fields:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            form.addRow(l, widget)

        if self.user:
            self.username_input.setText(self.user[1])
            self.username_input.setReadOnly(True)
            self.username_input.setStyleSheet(
                input_style +
                f"QLineEdit {{ color: {COLORS['text_muted']}; }}"
            )
            self.fullname_input.setText(self.user[2])
            self.email_input.setText(self.user[3] or "")
            for i in range(self.role_combo.count()):
                if self.role_combo.itemData(i) == self.user[8]:
                    self.role_combo.setCurrentIndex(i)
                    break

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton(
            "Save Changes" if self.user else "Create User"
        )
        save_btn.setFixedHeight(42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(primary_button())
        save_btn.clicked.connect(self.save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        layout.addWidget(title)
        layout.addWidget(div)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def save(self):
        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        email    = self.email_input.text().strip()
        role_id  = self.role_combo.currentData()

        if not username or not fullname:
            QMessageBox.warning(
                self, "Validation",
                "Username and full name are required."
            )
            return

        if not self.user:
            password = self.password_input.text().strip()
            if not password:
                QMessageBox.warning(
                    self, "Validation",
                    "Password is required."
                )
                return
            self.result_data = {
                "username": username,
                "full_name": fullname,
                "email": email,
                "password": password,
                "role_id": role_id,
            }
        else:
            self.result_data = {
                "full_name": fullname,
                "email": email,
                "role_id": role_id,
            }
        self.accept()


# ── Reset password dialog ─────────────────────────────────────
class ResetPasswordDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"Reset Password — {user[2]}")
        self.setFixedSize(380, 240)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text_primary']};
                font-family: Segoe UI;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel(f"Reset Password")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        sub = QLabel(f"Setting new password for: {self.user[2]}")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {COLORS['text_secondary']};")

        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("New password")
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass.setFixedHeight(40)
        self.new_pass.setStyleSheet(input_style)

        self.confirm_pass = QLineEdit()
        self.confirm_pass.setPlaceholderText("Confirm password")
        self.confirm_pass.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.confirm_pass.setFixedHeight(40)
        self.confirm_pass.setStyleSheet(input_style)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        reset_btn = QPushButton("Reset Password")
        reset_btn.setFixedHeight(40)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(
            primary_button(COLORS['danger'])
        )
        reset_btn.clicked.connect(self.reset)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(reset_btn)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(self.new_pass)
        layout.addWidget(self.confirm_pass)
        layout.addLayout(btn_row)

    def reset(self):
        new  = self.new_pass.text().strip()
        conf = self.confirm_pass.text().strip()
        if not new:
            QMessageBox.warning(
                self, "Validation",
                "Please enter a new password."
            )
            return
        if new != conf:
            QMessageBox.warning(
                self, "Mismatch",
                "Passwords do not match."
            )
            return
        self.new_password = new
        self.accept()


# ── Main settings widget ──────────────────────────────────────
class SettingsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user  = user
        self.users = []
        self.roles = []
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Administration & Settings")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Manage users, settings, branding and system"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_data)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(refresh_btn)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background-color: {COLORS['bg_secondary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: 600;
                font-family: Segoe UI;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['accent']};
                border-bottom: 2px solid {COLORS['accent']};
            }}
        """)

        # Tab 1 — Users
        self.users_tab = QWidget()
        self.users_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_users_tab()
        self.tabs.addTab(self.users_tab, "👥  Users")

        # Tab 2 — Settings
        self.settings_tab = QWidget()
        self.settings_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_settings_tab()
        self.tabs.addTab(
            self.settings_tab, "⚙️  System Settings"
        )

        # Tab 3 — Audit Logs
        self.audit_tab = QWidget()
        self.audit_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_audit_tab()
        self.tabs.addTab(self.audit_tab, "📋  Audit Logs")

        # Tab 4 — Backup
        self.backup_tab = QWidget()
        self.backup_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_backup_tab()
        self.tabs.addTab(self.backup_tab, "💾  Backup")

        layout.addLayout(header_row)
        layout.addWidget(self.tabs)

    def setup_users_tab(self):
        layout = QVBoxLayout(self.users_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("⊕  Add User")
        add_btn.setFixedHeight(36)
        add_btn.setFixedWidth(130)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(primary_button())
        add_btn.clicked.connect(self.add_user)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "USERNAME", "FULL NAME",
            "ROLE", "STATUS", "LAST LOGIN", "ACTIONS"
        ])
        self.users_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: none;
                gridline-color: transparent;
                font-family: Segoe UI;
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 0px 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['accent_light']};
                color: {COLORS['accent_text']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: bold;
                font-size: 11px;
                font-family: Segoe UI;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_tertiary']};
                width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_strong']};
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self.users_table.setColumnWidth(0, 50)
        self.users_table.setColumnWidth(4, 90)
        self.users_table.setColumnWidth(5, 140)
        self.users_table.setColumnWidth(6, 80)
        self.users_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.users_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.users_table.setShowGrid(False)
        self.users_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addLayout(toolbar)
        layout.addWidget(self.users_table)

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        def section(title):
            lbl = QLabel(title)
            lbl.setFont(
                QFont("Segoe UI", 13, QFont.Weight.Bold)
            )
            lbl.setStyleSheet(
                f"color: {COLORS['text_primary']};"
            )
            div = QFrame()
            div.setFixedHeight(1)
            div.setStyleSheet(
                f"background: {COLORS['border']}; border: none;"
            )
            col = QVBoxLayout()
            col.setSpacing(4)
            col.addWidget(lbl)
            col.addWidget(div)
            return col

        def field(label, key, placeholder=""):
            row  = QHBoxLayout()
            lbl  = QLabel(label)
            lbl.setFixedWidth(200)
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            inp  = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(38)
            inp.setStyleSheet(input_style)
            inp.setObjectName(key)
            row.addWidget(lbl)
            row.addWidget(inp)
            return row, inp

        # Restaurant section
        layout.addLayout(section("🏢  Restaurant Information"))
        self.s_fields = {}
        for label, key, ph in [
            ("Restaurant Name",    "restaurant_name",    "e.g. Quick Eats"),
            ("Address",            "restaurant_address", "e.g. 123 Main Street"),
            ("Phone",              "restaurant_phone",   "e.g. +254 700 000 000"),
            ("Receipt Footer",     "receipt_footer",     "e.g. Thank you for dining with us!"),
        ]:
            row, inp = field(label, key, ph)
            layout.addLayout(row)
            self.s_fields[key] = inp

        layout.addLayout(section("💰  Financial Settings"))
        for label, key, ph in [
            ("Currency Symbol", "currency", "e.g. $"),
            ("Tax Rate (%)", "tax_rate", "e.g. 16"),
            ("Loyalty Points Rate", "loyalty_points_per_dollar", "e.g. 1"),
        ]:
            row, inp = field(label, key, ph)
            layout.addLayout(row)
            self.s_fields[key] = inp

        layout.addLayout(section("🎨  Branding"))

        # Primary colour
        color_row = QHBoxLayout()
        color_lbl = QLabel("Primary Colour")
        color_lbl.setFixedWidth(200)
        color_lbl.setFont(QFont("Segoe UI", 11))
        color_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("e.g. #16a34a")
        self.color_input.setFixedHeight(38)
        self.color_input.setStyleSheet(input_style)
        self.color_input.setObjectName("primary_color")
        self.color_input.textChanged.connect(
            self.preview_colour
        )
        self.s_fields["primary_color"] = self.color_input

        self.color_preview = QFrame()
        self.color_preview.setFixedSize(38, 38)
        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        color_row.addWidget(color_lbl)
        color_row.addWidget(self.color_input)
        color_row.addWidget(self.color_preview)
        layout.addLayout(color_row)

        # Colour presets
        preset_row = QHBoxLayout()
        preset_lbl = QLabel("Colour Presets")
        preset_lbl.setFixedWidth(200)
        preset_lbl.setFont(QFont("Segoe UI", 11))
        preset_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        preset_row.addWidget(preset_lbl)

        presets = [
            ("#16a34a", "Green"),
            ("#2563eb", "Blue"),
            ("#dc2626", "Red"),
            ("#d97706", "Amber"),
            ("#7c3aed", "Purple"),
            ("#0f172a", "Dark"),
        ]
        for color, name in presets:
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setToolTip(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 16px;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    border: 2px solid {COLORS['border_strong']};
                }}
            """)
            btn.clicked.connect(
                lambda _, c=color: self.select_preset(c)
            )
            preset_row.addWidget(btn)

        preset_row.addStretch()
        layout.addLayout(preset_row)

        # Logo upload
        logo_row = QHBoxLayout()
        logo_lbl = QLabel("Restaurant Logo")
        logo_lbl.setFixedWidth(200)
        logo_lbl.setFont(QFont("Segoe UI", 11))
        logo_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText(
            "Path to logo image file"
        )
        self.logo_path_input.setFixedHeight(38)
        self.logo_path_input.setStyleSheet(input_style)
        self.logo_path_input.setObjectName("logo_path")
        self.s_fields["logo_path"] = self.logo_path_input

        browse_btn = QPushButton("📁  Browse")
        browse_btn.setFixedHeight(38)
        browse_btn.setFixedWidth(90)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet(outline_button())
        browse_btn.clicked.connect(self.browse_logo)

        logo_row.addWidget(logo_lbl)
        logo_row.addWidget(self.logo_path_input)
        logo_row.addWidget(browse_btn)
        layout.addLayout(logo_row)

        # Logo preview
        self.logo_preview = QLabel("No logo selected")
        self.logo_preview.setFixedHeight(80)
        self.logo_preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.logo_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px dashed {COLORS['border_strong']};
                border-radius: 8px;
                color: {COLORS['text_muted']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.logo_preview)

        save_btn = QPushButton("💾  Save All Settings")
        save_btn.setFixedHeight(44)
        save_btn.setFixedWidth(200)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(primary_button())
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        layout.addStretch()

    def setup_audit_tab(self):
        layout = QVBoxLayout(self.audit_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(5)
        self.audit_table.setHorizontalHeaderLabels([
            "TIME", "USER", "ACTION",
            "TABLE", "RECORD ID"
        ])
        self.audit_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: none;
                gridline-color: transparent;
                font-family: Segoe UI;
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 0px 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: bold;
                font-size: 11px;
                font-family: Segoe UI;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_tertiary']};
                width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_strong']};
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self.audit_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.audit_table.verticalHeader().setVisible(False)
        self.audit_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.audit_table.setShowGrid(False)
        layout.addWidget(self.audit_table)

    def setup_backup_tab(self):
        layout = QVBoxLayout(self.backup_tab)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Database Backup")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        desc = QLabel(
            "Create a backup of the restaurant database.\n"
            "This saves all orders, customers, inventory "
            "and settings to a backup file on the server.\n\n"
            "It is recommended to perform a backup daily."
        )
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet(f"color: {COLORS['text_secondary']};")
        desc.setWordWrap(True)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        backup_btn = QPushButton("💾  Create Database Backup")
        backup_btn.setFixedHeight(46)
        backup_btn.setFixedWidth(240)
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.setStyleSheet(primary_button())
        backup_btn.clicked.connect(self.do_backup)

        export_btn = QPushButton("📤  Export Data to CSV")
        export_btn.setFixedHeight(46)
        export_btn.setFixedWidth(240)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(outline_button())
        export_btn.clicked.connect(self.export_data)

        self.backup_status = QLabel("")
        self.backup_status.setFont(QFont("Segoe UI", 11))
        self.backup_status.setStyleSheet(
            f"color: {COLORS['accent']};"
        )

        layout.addWidget(title)
        layout.addWidget(div)
        layout.addWidget(desc)
        layout.addWidget(backup_btn)
        layout.addWidget(export_btn)
        layout.addWidget(self.backup_status)

    # ── Data loading ──────────────────────────────────────────
    def load_data(self):
        self.roles = get_all_roles()
        self.users = get_all_users()
        self.populate_users()
        self.load_settings()
        self.load_audit_logs()

    def populate_users(self):
        self.users_table.setRowCount(0)
        self.users_table.setRowCount(len(self.users))

        for idx, u in enumerate(self.users):
            self.users_table.setRowHeight(idx, 52)

            id_item = QTableWidgetItem(str(u[0]))
            id_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            id_item.setForeground(QColor(COLORS['text_muted']))
            self.users_table.setItem(idx, 0, id_item)

            uname_item = QTableWidgetItem(u[1])
            uname_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            uname_item.setForeground(QColor(COLORS['accent']))
            self.users_table.setItem(idx, 1, uname_item)

            self.users_table.setItem(
                idx, 2, QTableWidgetItem(u[2])
            )
            self.users_table.setItem(
                idx, 3, QTableWidgetItem(u[7] or "—")
            )

            # Status badge
            is_active    = u[4]
            badge_widget = QWidget()
            badge_widget.setStyleSheet("background: transparent;")
            badge_layout = QHBoxLayout(badge_widget)
            badge_layout.setContentsMargins(6, 0, 6, 0)
            badge_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            badge = QLabel("Active" if is_active else "Locked")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(24)
            badge.setFont(
                QFont("Segoe UI", 10, QFont.Weight.Bold)
            )
            badge.setStyleSheet(f"""
                color: {COLORS['accent'] if is_active else COLORS['danger']};
                background-color: {COLORS['accent_light'] if is_active else COLORS['danger_light']};
                border-radius: 10px;
                padding: 0 10px;
                border: none;
            """)
            badge_layout.addWidget(badge)
            self.users_table.setCellWidget(idx, 4, badge_widget)

            last_login = str(u[5])[:16] if u[5] else "Never"
            self.users_table.setItem(
                idx, 5, QTableWidgetItem(last_login)
            )

            dots_btn = QPushButton("⋮")
            dots_btn.setFixedSize(32, 32)
            dots_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dots_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    font-size: 18px;
                    font-weight: bold;
                    padding-bottom: 4px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_tertiary']};
                }}
            """)
            dots_btn.clicked.connect(
                lambda _, user=u: self.show_user_menu(user)
            )

            cell = QWidget()
            cell.setStyleSheet("background: transparent;")
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cell_layout.addWidget(dots_btn)
            self.users_table.setCellWidget(idx, 6, cell)

    def load_settings(self):
        settings = get_all_settings()
        for key, inp in self.s_fields.items():
            inp.setText(settings.get(key, ""))

    def load_audit_logs(self):
        logs = get_audit_logs(limit=100)
        self.audit_table.setRowCount(0)
        self.audit_table.setRowCount(len(logs))

        for idx, log in enumerate(logs):
            self.audit_table.setRowHeight(idx, 44)

            time_item = QTableWidgetItem(str(log[5])[:16])
            time_item.setForeground(
                QColor(COLORS['text_muted'])
            )
            self.audit_table.setItem(idx, 0, time_item)

            user_item = QTableWidgetItem(log[1])
            user_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            user_item.setForeground(QColor(COLORS['accent']))
            self.audit_table.setItem(idx, 1, user_item)

            action_item = QTableWidgetItem(log[2])
            action_item.setForeground(
                QColor(COLORS['text_primary'])
            )
            self.audit_table.setItem(idx, 2, action_item)

            self.audit_table.setItem(
                idx, 3,
                QTableWidgetItem(log[3] or "—")
            )
            self.audit_table.setItem(
                idx, 4,
                QTableWidgetItem(
                    str(log[4]) if log[4] else "—"
                )
            )

    # ── Actions ───────────────────────────────────────────────
    def show_user_menu(self, user):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 6px;
                font-family: Segoe UI;
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 6px;
                color: {COLORS['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {COLORS['border']};
                margin: 4px 8px;
            }}
        """)

        edit_action   = menu.addAction("✏️   Edit User")
        reset_action  = menu.addAction("🔑  Reset Password")
        menu.addSeparator()
        toggle_label  = (
            "🔒  Lock Account" if user[4]
            else "🔓  Unlock Account"
        )
        toggle_action = menu.addAction(toggle_label)

        action = menu.exec(QCursor.pos())

        if action == edit_action:
            self.edit_user(user)
        elif action == reset_action:
            self.reset_password(user)
        elif action == toggle_action:
            self.toggle_user(user)

    def add_user(self):
        dialog = UserDialog(self, roles=self.roles)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = create_user(
                d['username'], d['full_name'],
                d['email'], d['password'], d['role_id']
            )
            if success:
                QMessageBox.information(
                    self, "Success",
                    f"User '{d['username']}' created successfully."
                )
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to create user. "
                    "Username may already exist."
                )

    def edit_user(self, user):
        dialog = UserDialog(
            self, user=user, roles=self.roles
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = update_user(
                user[0], d['full_name'],
                d['email'], d['role_id']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to update user."
                )

    def reset_password(self, user):
        dialog = ResetPasswordDialog(user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            success = reset_user_password(
                user[0], dialog.new_password
            )
            if success:
                QMessageBox.information(
                    self, "Success",
                    "Password reset successfully."
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to reset password."
                )

    def toggle_user(self, user):
        if user[0] == self.user['user_id']:
            QMessageBox.warning(
                self, "Cannot Lock",
                "You cannot lock your own account."
            )
            return
        success = toggle_user_status(user[0], user[4])
        if success:
            self.load_data()

    def save_settings(self):
        for key, inp in self.s_fields.items():
            save_setting(key, inp.text().strip())
        QMessageBox.information(
            self, "Saved",
            "All settings saved successfully.\n"
            "Some changes take effect on next login."
        )

    def preview_colour(self, color):
        if len(color) == 7 and color.startswith("#"):
            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    border: 1px solid {COLORS['border']};
                }}
            """)

    def select_preset(self, color):
        self.color_input.setText(color)
        self.preview_colour(color)

    def browse_logo(self):
        path = QFileDialog.getOpenFileName(
            self, "Select Logo Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.svg)"
        )[0]
        if path:
            self.logo_path_input.setText(path)
            # Show preview
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    200, 70,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.logo_preview.setPixmap(scaled)
                self.logo_preview.setText("")
            else:
                self.logo_preview.setText(
                    "Could not load image"
                )

    def do_backup(self):
        path = QFileDialog.getSaveFileName(
            self, "Save Backup",
            f"restaurant_backup_{__import__('datetime').date.today()}.bak",
            "Backup Files (*.bak)"
        )[0]
        if not path:
            return
        success = backup_database(path)
        if success:
            self.backup_status.setText(
                f"✅  Backup saved to: {path}"
            )
            self.backup_status.setStyleSheet(
                f"color: {COLORS['accent']};"
            )
        else:
            self.backup_status.setText(
                "❌  Backup failed. Check server permissions."
            )
            self.backup_status.setStyleSheet(
                f"color: {COLORS['danger']};"
            )

    def export_data(self):
        import csv
        path = QFileDialog.getSaveFileName(
            self, "Export Data",
            f"restaurant_data_{__import__('datetime').date.today()}.csv",
            "CSV Files (*.csv)"
        )[0]
        if not path:
            return
        try:
            from database.connection import create_connection
            conn   = create_connection()
            cursor = conn.cursor()
            with open(path, "w", newline="",
                      encoding="utf-8") as f:
                writer = csv.writer(f)
                for table in ["orders", "customers",
                              "menu_items", "ingredients"]:
                    writer.writerow([f"--- {table.upper()} ---"])
                    cursor.execute(f"SELECT * FROM {table}")
                    cols = [d[0] for d in cursor.description]
                    writer.writerow(cols)
                    for row in cursor.fetchall():
                        writer.writerow(row)
                    writer.writerow([])
            conn.close()
            QMessageBox.information(
                self, "Exported",
                f"Data exported to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", str(e)
            )