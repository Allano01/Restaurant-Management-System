from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from services.auth_service import authenticate_user, log_action
from assets.styles import COLORS, primary_button


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restaurant Management System")
        self.setFixedSize(420, 500)
        self.setStyleSheet("background-color: #1e1e2e;")
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(16)

        title_label = QLabel("🍽")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 52px; background: transparent;")

        app_name = QLabel("Restaurant Manager")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        app_name.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")

        subtitle = QLabel("Sign in to your account")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; margin-bottom: 10px;")

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 14px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(24, 24, 24, 24)

        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['accent']};
            }}
        """

        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        username_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(42)
        self.username_input.setStyleSheet(input_style)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        password_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.setStyleSheet(input_style)
        self.password_input.returnPressed.connect(self.handle_login)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 12px; background: transparent;")

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(44)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(primary_button())
        self.login_btn.clicked.connect(self.handle_login)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_btn)

        footer = QLabel("Restaurant Management System  •  v1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")

        main_layout.addWidget(title_label)
        main_layout.addWidget(app_name)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(card)
        main_layout.addStretch()
        main_layout.addWidget(footer)
        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Please enter username and password.")
            return

        self.login_btn.setText("Signing in...")
        self.login_btn.setEnabled(False)

        user = authenticate_user(username, password)

        if user:
            log_action(user["user_id"], "LOGIN", "users", user["user_id"])
            self.error_label.setText("")
            self.open_dashboard(user)
        else:
            self.error_label.setText("Invalid username or password.")
            self.login_btn.setText("Sign In")
            self.login_btn.setEnabled(True)

    def open_dashboard(self, user):
        from ui.dashboard import DashboardWindow
        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()