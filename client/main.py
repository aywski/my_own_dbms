from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
    QLineEdit, QLabel, QListWidget, QHBoxLayout, QInputDialog, QMessageBox
)
from rest_client import RestClient
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Manager")
        self.setGeometry(100, 100, 400, 300)

        self.client = RestClient()

        self.layout = QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        # Виджет для отображения таблиц
        self.table_list = QListWidget()
        self.layout.addWidget(QLabel("Таблицы:"))
        self.layout.addWidget(self.table_list)
        self.load_tables()

        # Кнопки
        buttons_layout = QHBoxLayout()

        # Добавление таблицы
        self.add_table_button = QPushButton("Добавить таблицу")
        self.add_table_button.clicked.connect(self.add_table)
        buttons_layout.addWidget(self.add_table_button)

        # Удаление таблицы
        self.delete_table_button = QPushButton("Удалить таблицу")
        self.delete_table_button.clicked.connect(self.delete_table)
        buttons_layout.addWidget(self.delete_table_button)

        # Обновить список
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_tables)
        buttons_layout.addWidget(self.refresh_button)

        self.layout.addLayout(buttons_layout)

        # Основной виджет
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def load_tables(self):
        """Загрузить список таблиц с сервера."""
        self.table_list.clear()
        tables = self.client.get_tables()
        if tables:
            for table in tables:
                self.table_list.addItem(table)
        else:
            self.table_list.addItem("Нет таблиц.")

    def add_table(self):
        """Добавить новую таблицу."""
        table_name, ok = QInputDialog.getText(self, "Добавить таблицу", "Введите имя таблицы:")
        if ok and table_name:
            fields, ok = QInputDialog.getText(self, "Добавить поля", "Введите поля через запятую:")
            if ok and fields:
                fields_list = [field.strip() for field in fields.split(",")]
                response = self.client.create_table(table_name, fields_list)
                if response:
                    QMessageBox.information(self, "Успех", f"Таблица {table_name} создана.")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось создать таблицу.")
                self.load_tables()

    def delete_table(self):
        """Удалить выбранную таблицу."""
        selected_item = self.table_list.currentItem()
        if selected_item:
            table_name = selected_item.text()
            if table_name != "Нет таблиц.":
                response = self.client.delete_table(table_name)
                if response:
                    QMessageBox.information(self, "Успех", f"Таблица {table_name} удалена.")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить таблицу.")
                self.load_tables()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
