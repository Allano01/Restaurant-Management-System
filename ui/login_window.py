from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from services.auth_service import authenticate_user, log_action


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restaurant Management System")
        self.setFixedSize(420, 500)
        self.setStyleSheet("background-color: #1e1e2e;")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(16)

        # ── Logo / title area ─────────────────────────────────
        title_label = QLabel("🍽")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 52px;")

        app_name = QLabel("Restaurant Manager")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #ffffff;")

        subtitle = QLabel("Sign in to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #888888; margin-bottom: 10px;")

        # ── Card frame ────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b3b;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Username
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 10))
        username_label.setStyleSheet("color: #cccccc;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                border: 1px solid #444466;
                border-radius: 6px;
                padding: 0 12px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #c0392b;
            }
        """)

        # Password
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 10))
        password_label.setStyleSheet("color: #cccccc;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                border: 1px solid #444466;
                border-radius: 6px;
                padding: 0 12px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #c0392b;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")

        # Login button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(42)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a93226;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_btn)

        # Footer
        footer = QLabel("Restaurant Management System v1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #555555; font-size: 10px;")

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