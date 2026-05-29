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
        self.setFixedSize(440, 520)
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(48, 48, 48, 48)
        main_layout.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedSize(56, 56)
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent_light']};
                border-radius: 14px;
                border: none;
            }}
        """)
        logo_inner = QVBoxLayout(logo_frame)
        logo_inner.setContentsMargins(0, 0, 0, 0)
        logo_icon = QLabel("🍽")
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setFont(QFont("Segoe UI", 26))
        logo_icon.setStyleSheet("background: transparent; border: none;")
        logo_inner.addWidget(logo_icon)

        logo_row = QHBoxLayout()
        logo_row.addWidget(logo_frame)
        logo_row.addStretch()

        app_name = QLabel("RestaurantPro")
        app_name.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        app_name.setStyleSheet(f"color: {COLORS['text_primary']}; margin-top: 16px;")

        subtitle = QLabel("Sign in to your account to continue")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: 28px;")

        # Card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(24, 24, 24, 24)

        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {COLORS['accent']};
                background-color: white;
            }}
        """

        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        username_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; border: none;"
        )

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet(input_style)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        password_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; border: none;"
        )

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet(input_style)
        self.password_input.returnPressed.connect(self.handle_login)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet(
            f"color: {COLORS['danger']}; font-size: 12px; "
            f"background: transparent; border: none;"
        )

        self.login_btn = QPushButton("Sign In →")
        self.login_btn.setFixedHeight(46)
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
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet(
            f"color: {COLORS['text_muted']}; margin-top: 16px; background: transparent;"
        )

        main_layout.addLayout(logo_row)
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
            self.error_label.setText("Please enter your username and password.")
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
            self.login_btn.setText("Sign In →")
            self.login_btn.setEnabled(True)

    def open_dashboard(self, user):
        from ui.dashboard import DashboardWindow
        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()