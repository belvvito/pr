from PyQt6.QtWidgets import QPushButton, QDialog, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, \
    QTableWidget
from PyQt6.QtCore import Qt
from windows.base_window import BaseWindow


class ManagerWindow(BaseWindow):
    def __init__(self, user=None):
        super().__init__(user)
        self.setWindowTitle("Аквилон - Менеджер")
        self.sort_desc = False

        self.button_orders.show()
        self.button_orders.setText("Просмотр заказов")
        self.line_search.show()
        self.combo_category.show()
        self.combo_supplier.show()
        self.button_sort.show()

        self.load_suppliers()

        self.button_orders.clicked.connect(self.view_orders)
        self.line_search.textChanged.connect(self.filter_menu)
        self.combo_category.currentTextChanged.connect(self.filter_menu)
        self.combo_supplier.currentTextChanged.connect(self.filter_menu)
        self.button_sort.clicked.connect(self.toggle_sort)

    def load_suppliers(self):
        suppliers = self.db.get_suppliers()
        self.combo_supplier.addItem("Все поставщики")
        for s in suppliers:
            self.combo_supplier.addItem(s)

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

    def view_orders(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Просмотр заказов")
        dialog.resize(900, 500)
        layout = QVBoxLayout(dialog)

        top = QHBoxLayout()
        top.addWidget(QLabel("Статус:"))
        status_combo = QComboBox()
        status_combo.addItems(["Все", "Ожидает приготовления", "Готово", "Доставляется", "Выполнен"])
        top.addWidget(status_combo)
        btn_refresh = QPushButton("Обновить")
        top.addWidget(btn_refresh)
        layout.addLayout(top)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ID", "Клиент", "Дата", "Сумма", "Статус", "Адрес"])
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)

        def refresh():
            data = self.db.get_all_orders(status_combo.currentText())
            table.setRowCount(len(data))
            for i, row in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(str(row['id_order'])))
                table.setItem(i, 1, QTableWidgetItem(row['username']))
                table.setItem(i, 2, QTableWidgetItem(str(row['order_date'])[:19]))
                table.setItem(i, 3, QTableWidgetItem(str(row['total_amount'])))

                status_item = QTableWidgetItem(row['status'])
                if row['status'] == 'Выполнен':
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif row['status'] == 'Ожидает приготовления':
                    status_item.setForeground(Qt.GlobalColor.darkYellow)
                elif row['status'] == 'Готово':
                    status_item.setForeground(Qt.GlobalColor.darkBlue)
                table.setItem(i, 4, status_item)

                table.setItem(i, 5, QTableWidgetItem(row['address'] or '-'))

        status_combo.currentTextChanged.connect(refresh)
        btn_refresh.clicked.connect(refresh)
        refresh()

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)

        dialog.exec()