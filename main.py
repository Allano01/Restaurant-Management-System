import sys
from PyQt6.QtWidgets import QApplication
from database.connection import create_connection
from services.auth_service import setup_admin_password

def main():
    try:
        conn = create_connection()
        if not conn:
            print("Could not connect to database. Exiting.")
            sys.exit(1)
        conn.close()

        setup_admin_password()

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        from assets.styles import app_stylesheet
        app.setStyleSheet(app_stylesheet())

        from ui.login_window import LoginWindow
        window = LoginWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()