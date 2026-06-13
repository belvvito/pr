import os
from PyQt6.QtWidgets import QMainWindow, QLabel, QFrame, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ui.menu_ui import Ui_MenuWindow
from services.db_service import DBService
from models.menu_item import MenuItem


class BaseWindow(QMainWindow, Ui_MenuWindow):
    COLOR_HIGH_DISCOUNT = "#2E8B57"
    COLOR_OUT_OF_STOCK = "#ADD8E6"

    def __init__(self, user=None):
        super().__init__()
        self.setupUi(self)

        self.user = user
        self.db = DBService()
        self.all_items = []

        # Скрываем все дополнительные элементы по умолчанию
        self.button_add.hide()
        self.button_orders.hide()
        self.line_search.hide()
        self.combo_category.hide()
        self.combo_supplier.hide()
        self.button_sort.hide()

        if user:
            self.label_user.setText(f"👤 {user.contact_info}")
        else:
            self.label_user.setText("Гость")

        self.combo_category.addItems(["Все", "Пицца", "Салаты", "Десерты", "Напитки"])
        self.button_exit.clicked.connect(self.logout)

        self.load_menu()

    def load_menu(self):
        try:
            self.all_items = self.db.get_menu()
            self.display_items(self.all_items)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить меню:\n{e}")

    def display_items(self, items):
        for i in reversed(range(self.menu_layout.count())):
            widget = self.menu_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for item in items:
            self.menu_layout.addWidget(self.create_card(item))
        self.menu_layout.addStretch()

    def create_card(self, item):
        card = QFrame()
        card_style = self._get_card_style(item)
        card.setStyleSheet(card_style)
        layout = QHBoxLayout(card)

        # Фото
        img = QLabel()
        img.setFixedSize(80, 80)
        img.setScaledContents(True)

        if item.photo and not item.photo.isNull():
            pix = item.photo.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
            img.setPixmap(pix)
        else:
            default_path = os.path.join("data", "menu.png")
            if os.path.exists(default_path):
                pix = QPixmap(default_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                img.setPixmap(pix)
            else:
                # Текст вместо смайлика
                img.setText("Нет фото")
                img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img.setStyleSheet("background: #f0f0f0; font-size: 12px;")

        layout.addWidget(img)

        price_text = self._get_price_html(item)

        stock_text = ""
        if item.quantity <= 0:
            stock_text = "<br><span style='color: #cc0000; font-weight: bold;'>Нет в наличии</span>"
        elif item.quantity < 10:
            stock_text = f"<br><span style='color: #e67e22;'>Осталось: {item.quantity} шт.</span>"

        info = QLabel(f"<b>{item.name_item}</b><br>{item.description}<br>{price_text}{stock_text}")
        info.setWordWrap(True)
        layout.addWidget(info, 1)

        self.add_card_buttons(layout, item)
        return card

    def _get_card_style(self, item):
        if item.quantity <= 0:
            return f"background-color: {self.COLOR_OUT_OF_STOCK}; border: 1px solid #87CEEB; border-radius: 8px; padding: 5px; margin: 5px;"
        if item.discount > 15:
            return f"background-color: {self.COLOR_HIGH_DISCOUNT}; color: white; border: 1px solid #1a6b3a; border-radius: 8px; padding: 5px; margin: 5px;"
        return "background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 5px; margin: 5px;"

    def _get_price_html(self, item):
        if item.discount > 0:
            return f'<span style="color: red; text-decoration: line-through;">{item.price:.0f} ₽</span> <b style="color: black;">{item.final_price:.0f} ₽</b> <span style="color: #27ae60;">(-{item.discount}%)</span>'
        return f'<b style="color: green;">{item.price:.0f} ₽</b>'

    def add_card_buttons(self, layout, item):
        pass

    def logout(self):
        from windows.auth_window import AuthWindow
        self.auth = AuthWindow()
        self.auth.show()
        self.close()