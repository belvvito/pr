from windows.base_window import BaseWindow

class CustomerWindow(BaseWindow):
    def __init__(self, user=None):
        super().__init__(user)
        self.setWindowTitle("Клиент")