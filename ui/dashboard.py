from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Restaurant Management System — Dashboard")
        self.setMinimumSize(1024, 680)
        self.setStyleSheet("background-color: #1e1e2e;")
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome = QLabel(f"Welcome, {self.user['full_name']} 👋")
        welcome.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        welcome.setStyleSheet("color: #ffffff;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        role = QLabel(f"Role: {self.user['role']}")
        role.setFont(QFont("Segoe UI", 12))
        role.setStyleSheet("color: #888888;")
        role.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QLabel("Dashboard coming in next phase...")
        info.setFont(QFont("Segoe UI", 11))
        info.setStyleSheet("color: #555555; margin-top: 20px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(welcome)
        layout.addWidget(role)
        layout.addWidget(info)