from PyQt6.QtWidgets import QWidget, QMessageBox
from ui.auth_ui import Ui_AuthWindow
from services.db_service import DBService


class AuthWindow(QWidget, Ui_AuthWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db = DBService()
        self.button_login.clicked.connect(self.login)
        self.button_guest.clicked.connect(lambda: self.open_menu(None))

    def login(self):
        user = self.db.get_user(self.line_login.text().strip(), self.line_password.text().strip())
        if user:
            self.open_menu(user)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def open_menu(self, user):
        if not user:
            from windows.guest_window import GuestWindow
            self.window = GuestWindow(None)
        else:
            role = user.name_role.lower()
            if role == "customer":
                from windows.customer_window import CustomerWindow
                self.window = CustomerWindow(user)
            elif role == "staff":
                from windows.manager_window import ManagerWindow
                self.window = ManagerWindow(user)
            elif role == "admin":
                from windows.admin_window import AdminWindow
                self.window = AdminWindow(user)
            else:
                from windows.guest_window import GuestWindow
                self.window = GuestWindow(None)

        self.window.show()
        self.close()