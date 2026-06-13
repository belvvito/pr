from windows.base_window import BaseWindow

class GuestWindow(BaseWindow):
    def __init__(self, user=None):
        super().__init__(user)
        self.setWindowTitle("Гость")