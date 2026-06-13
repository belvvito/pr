import sys
from PyQt6.QtWidgets import QApplication
from windows.auth_window import AuthWindow

def main():
    app = QApplication(sys.argv)
    win = AuthWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()