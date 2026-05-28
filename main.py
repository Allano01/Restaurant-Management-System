import sys
from PyQt6.QtWidgets import QApplication
from database.connection import create_connection
from services.auth_service import setup_admin_password
from ui.login_window import LoginWindow


def main():
    # Test database connection
    conn = create_connection()
    if not conn:
        print("Could not connect to database. Exiting.")
        sys.exit(1)
    conn.close()

    # Hash admin password on first run
    setup_admin_password()

    # Launch the app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()