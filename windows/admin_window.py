import os
import shutil
import time
from PyQt6.QtWidgets import (
    QPushButton, QInputDialog, QMessageBox, QFileDialog, QDialog,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QTableWidget, QFormLayout, QLineEdit, QSpinBox
)
from PyQt6.QtCore import Qt
from windows.base_window import BaseWindow


class AdminWindow(BaseWindow):
    def __init__(self, user=None):
        super().__init__(user)
        self.setWindowTitle("Аквилон - Администратор")
        self.sort_desc = False

        self.button_add.show()
        self.button_orders.show()
        self.button_orders.setText("Управление заказами")
        self.line_search.show()
        self.combo_category.show()
        self.combo_supplier.show()
        self.button_sort.show()

        self.load_suppliers()

        self.button_add.clicked.connect(self.add_item)
        self.button_orders.clicked.connect(self.manage_orders)
        self.line_search.textChanged.connect(self.filter_menu)
        self.combo_category.currentTextChanged.connect(self.filter_menu)
        self.combo_supplier.currentTextChanged.connect(self.filter_menu)
        self.button_sort.clicked.connect(self.toggle_sort)

    def load_suppliers(self):
        suppliers = self.db.get_suppliers()
        self.combo_supplier.addItem("Все поставщики")
        for s in suppliers:
            self.combo_supplier.addItem(s)

    def add_card_buttons(self, layout, item):
        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda _, it=item: self.edit_item(it))
        btn_del = QPushButton("Удалить")
        btn_del.clicked.connect(lambda _, id_=item.id_menu: self.delete_item(id_))
        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)

    def filter_menu(self):
        search = self.line_search.text().lower()
        category = self.combo_category.currentText()
        supplier = self.combo_supplier.currentText()

        filtered = []
        for item in self.all_items:
            if category != "Все" and item.category != category:
                continue
            if supplier != "Все поставщики" and item.supplier != supplier:
                continue
            if search and search not in f"{item.name_item} {item.description}".lower():
                continue
            filtered.append(item)

        if self.sort_desc:
            filtered.sort(key=lambda x: x.price, reverse=True)

        self.display_items(filtered)
        self.label_status.setText(f"Найдено: {len(filtered)}")

    def toggle_sort(self):
        self.sort_desc = not self.sort_desc
        self.button_sort.setText(f"Сортировка {'↓' if self.sort_desc else '↑'}")
        self.filter_menu()

    def add_item(self):
        name, ok = QInputDialog.getText(self, "Новое блюдо", "Название:")
        if not ok or not name.strip():
            return

        price, ok = QInputDialog.getInt(self, "Новое блюдо", "Цена (₽):", 500, 10, 10000)
        if not ok:
            return

        cats = ["Пицца", "Салаты", "Десерты", "Напитки"]
        category, ok = QInputDialog.getItem(self, "Новое блюдо", "Категория:", cats, 0, False)
        if not ok:
            return

        quantity, ok = QInputDialog.getInt(self, "Новое блюдо", "Количество на складе:", 10, 0, 1000)
        if not ok:
            quantity = 10

        discount, ok = QInputDialog.getInt(self, "Новое блюдо", "Скидка (%):", 0, 0, 100)
        if not ok:
            discount = 0

        desc, ok = QInputDialog.getText(self, "Новое блюдо", "Описание:")
        if not ok:
            desc = f"Вкусное {name}"

        photo_name = "menu.png"
        reply = QMessageBox.question(self, "Фото", "Добавить фото?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "data/", "Images (*.png *.jpg *.jpeg)")
            if file_path and os.path.exists(file_path):
                os.makedirs("data", exist_ok=True)
                photo_name = os.path.basename(file_path)
                dest_path = os.path.join("data", photo_name)
                try:
                    shutil.copy2(file_path, dest_path)
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось скопировать фото:\n{e}")

        try:
            self.db.add_item(name, desc, price, category, quantity, discount, photo_name)
            self.load_menu()
            QMessageBox.information(self, "Успех", f"Блюдо '{name}' добавлено!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить блюдо:\n{e}")

    def edit_item(self, item):
        try:
            name, ok = QInputDialog.getText(self, "Изменить", "Название:", text=item.name_item)
            if not ok:
                return

            price, ok = QInputDialog.getInt(self, "Изменить", "Цена:", value=int(item.price), min=10, max=10000)
            if not ok:
                return

            quantity, ok = QInputDialog.getInt(self, "Изменить", "Количество:", value=item.quantity, min=0, max=1000)
            if not ok:
                quantity = item.quantity

            discount, ok = QInputDialog.getInt(self, "Изменить", "Скидка (%):", value=item.discount, min=0, max=100)
            if not ok:
                discount = item.discount

            desc, ok = QInputDialog.getText(self, "Изменить", "Описание:", text=item.description)
            if not ok:
                desc = item.description

            photo_name = item.photo_path
            reply = QMessageBox.question(self, "Фото", "Изменить фото?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "data/",
                                                           "Images (*.png *.jpg *.jpeg)")
                if file_path and os.path.exists(file_path):
                    os.makedirs("data", exist_ok=True)
                    new_photo_name = os.path.basename(file_path)
                    dest_path = os.path.join("data", new_photo_name)
                    try:
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                            time.sleep(0.1)
                        shutil.copy2(file_path, dest_path)
                        photo_name = new_photo_name
                    except Exception as e:
                        QMessageBox.warning(self, "Ошибка", f"Не удалось скопировать фото:\n{e}")

            self.db.update_item(item.id_menu, name, price, desc, quantity, discount, photo_name)
            self.load_menu()
            QMessageBox.information(self, "Успех", "Блюдо обновлено!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить блюдо:\n{e}")

    def delete_item(self, id_menu):
        reply = QMessageBox.question(self, "Удалить", "Удалить блюдо?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = self.db.delete_item(id_menu)
            if ok:
                self.load_menu()
                QMessageBox.information(self, "Успех", "Блюдо удалено!")
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    # ==================== УПРАВЛЕНИЕ ЗАКАЗАМИ ====================
    def manage_orders(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление заказами")
        dialog.resize(1000, 600)
        layout = QVBoxLayout(dialog)

        top = QHBoxLayout()
        top.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Все", "Ожидает приготовления", "Готово", "Доставляется", "Выполнен"])
        top.addWidget(self.status_combo)

        btn_refresh = QPushButton("Обновить")
        top.addWidget(btn_refresh)
        top.addStretch()

        btn_create = QPushButton("Создать заказ")
        top.addWidget(btn_create)

        layout.addLayout(top)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Клиент", "Телефон", "Дата", "Сумма", "Статус", "Адрес"])
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.orders_table)

        btn_layout = QHBoxLayout()

        btn_edit = QPushButton("Редактировать")
        btn_delete = QPushButton("Удалить")
        btn_view = QPushButton("Состав заказа")

        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_view)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Изменить статус:"))

        btn_ready = QPushButton("Готово")
        btn_delivery = QPushButton("Доставляется")
        btn_done = QPushButton("Выполнен")

        status_layout.addWidget(btn_ready)
        status_layout.addWidget(btn_delivery)
        status_layout.addWidget(btn_done)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        self.status_combo.currentTextChanged.connect(self.refresh_orders_table)
        btn_refresh.clicked.connect(self.refresh_orders_table)
        btn_create.clicked.connect(lambda: self.create_order_dialog(dialog))
        btn_edit.clicked.connect(lambda: self.edit_order_dialog(dialog))
        btn_delete.clicked.connect(lambda: self.delete_order_dialog(dialog))
        btn_view.clicked.connect(self.view_order_items)
        btn_ready.clicked.connect(lambda: self.change_order_status("Готово"))
        btn_delivery.clicked.connect(lambda: self.change_order_status("Доставляется"))
        btn_done.clicked.connect(lambda: self.change_order_status("Выполнен"))

        self.refresh_orders_table()
        dialog.exec()

    def refresh_orders_table(self):
        data = self.db.get_all_orders(self.status_combo.currentText())
        self.orders_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.orders_table.setItem(i, 0, QTableWidgetItem(str(row['id_order'])))
            self.orders_table.setItem(i, 1, QTableWidgetItem(row['username']))
            self.orders_table.setItem(i, 2, QTableWidgetItem(row.get('contact_info', '-')))
            self.orders_table.setItem(i, 3, QTableWidgetItem(str(row['order_date'])[:19]))
            self.orders_table.setItem(i, 4, QTableWidgetItem(f"{row['total_amount']:.0f} ₽"))

            status_item = QTableWidgetItem(row['status'])
            if row['status'] == 'Выполнен':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif row['status'] == 'Ожидает приготовления':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif row['status'] == 'Готово':
                status_item.setForeground(Qt.GlobalColor.darkBlue)
            self.orders_table.setItem(i, 5, status_item)

            self.orders_table.setItem(i, 6, QTableWidgetItem(row['address'] or '-'))

    def get_selected_order_id(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")
            return None
        return int(self.orders_table.item(row, 0).text())

    def change_order_status(self, new_status):
        order_id = self.get_selected_order_id()
        if order_id:
            self.db.update_order_status(order_id, new_status)
            self.refresh_orders_table()
            QMessageBox.information(self, "Успех", f"Заказ #{order_id} → {new_status}")

    def create_order_dialog(self, parent_dialog):
        dialog = QDialog(parent_dialog)
        dialog.setWindowTitle("Создание заказа")
        dialog.resize(400, 350)
        layout = QVBoxLayout(dialog)

        form = QFormLayout()

        self.user_combo = QComboBox()
        users = self.db.get_all_users()
        for u in users:
            self.user_combo.addItem(f"{u['username']} ({u['contact_info']})", u['id_user'])
        form.addRow("Клиент:", self.user_combo)

        self.item_combo = QComboBox()
        self.load_menu_items()
        form.addRow("Блюдо:", self.item_combo)

        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(99)
        self.qty_spin.valueChanged.connect(self.update_price)
        form.addRow("Количество:", self.qty_spin)

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Адрес доставки")
        form.addRow("Адрес:", self.address_edit)

        self.price_label = QLabel()
        form.addRow("Цена за шт:", self.price_label)

        self.total_label = QLabel()
        form.addRow("Итого:", self.total_label)

        layout.addLayout(form)

        btn_create = QPushButton("Оформить заказ")
        btn_create.clicked.connect(lambda: self.save_new_order(dialog))
        layout.addWidget(btn_create)

        self.update_price()
        dialog.exec()

    def load_menu_items(self):
        self.item_combo.clear()
        items = self.db.get_menu()
        for item in items:
            if item.quantity > 0:
                self.item_combo.addItem(f"{item.name_item} - {item.final_price:.0f} ₽", item.id_menu)

    def update_price(self):
        idx = self.item_combo.currentIndex()
        if idx >= 0:
            item_id = self.item_combo.itemData(idx)
            items = self.db.get_menu()
            for item in items:
                if item.id_menu == item_id:
                    self.price_label.setText(f"{item.final_price:.0f} ₽")
                    total = item.final_price * self.qty_spin.value()
                    self.total_label.setText(f"{total:.0f} ₽")
                    break

    def save_new_order(self, dialog):
        user_idx = self.user_combo.currentIndex()
        if user_idx < 0:
            QMessageBox.warning(dialog, "Ошибка", "Выберите клиента")
            return

        item_idx = self.item_combo.currentIndex()
        if item_idx < 0:
            QMessageBox.warning(dialog, "Ошибка", "Выберите блюдо")
            return

        user_id = self.user_combo.itemData(user_idx)
        item_id = self.item_combo.itemData(item_idx)
        qty = self.qty_spin.value()
        address = self.address_edit.text().strip()

        items = self.db.get_menu()
        price = 0
        for item in items:
            if item.id_menu == item_id:
                price = item.final_price
                break

        try:
            order_id = self.db.create_order(user_id, item_id, qty, price, address)
            QMessageBox.information(dialog, "Успех", f"Заказ #{order_id} создан!")
            self.refresh_orders_table()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось создать заказ:\n{e}")

    def edit_order_dialog(self, parent_dialog):
        order_id = self.get_selected_order_id()
        if not order_id:
            return

        orders = self.db.get_all_orders()
        order_data = None
        for o in orders:
            if o['id_order'] == order_id:
                order_data = o
                break

        if not order_data:
            QMessageBox.warning(self, "Ошибка", "Заказ не найден")
            return

        dialog = QDialog(parent_dialog)
        dialog.setWindowTitle(f"Редактирование заказа #{order_id}")
        dialog.resize(400, 250)
        layout = QVBoxLayout(dialog)

        form = QFormLayout()

        address_edit = QLineEdit(order_data['address'] or '')
        status_combo = QComboBox()
        status_combo.addItems(["Ожидает приготовления", "Готово", "Доставляется", "Выполнен"])
        status_combo.setCurrentText(order_data['status'])

        form.addRow("Адрес:", address_edit)
        form.addRow("Статус:", status_combo)
        layout.addLayout(form)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(
            lambda: self.save_order_changes(order_id, address_edit.text(), status_combo.currentText(), dialog))
        layout.addWidget(btn_save)

        dialog.exec()

    def save_order_changes(self, order_id, address, status, dialog):
        self.db.update_order(order_id, address, status)
        self.refresh_orders_table()
        QMessageBox.information(dialog, "Успех", f"Заказ #{order_id} обновлён")
        dialog.accept()

    def delete_order_dialog(self, parent_dialog):
        order_id = self.get_selected_order_id()
        if not order_id:
            return

        reply = QMessageBox.question(parent_dialog, "Удаление",
                                     f"Удалить заказ #{order_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = self.db.delete_order(order_id)
            if ok:
                self.refresh_orders_table()
                QMessageBox.information(parent_dialog, "Успех", msg)
            else:
                QMessageBox.warning(parent_dialog, "Ошибка", msg)

    def view_order_items(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            return

        items = self.db.get_order_items(order_id)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Состав заказа #{order_id}")
        dialog.resize(500, 300)
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setRowCount(len(items))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Блюдо", "Количество", "Цена"])

        total = 0
        for i, item in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(item['name_item']))
            table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            table.setItem(i, 2, QTableWidgetItem(f"{item['price']:.0f} ₽"))
            total += item['price'] * item['quantity']

        layout.addWidget(table)
        layout.addWidget(QLabel(f"Итого: {total:.0f} ₽"))

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)

        dialog.exec()