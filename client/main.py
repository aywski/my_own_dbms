from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QLabel, QListWidget, QHBoxLayout, QInputDialog, QMessageBox,
    QDialog, QFormLayout, QComboBox
)
from rest_client import RestClient
import sys

class RecordDialog(QDialog):
    def __init__(self, table_name, fields, records, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Записи для {table_name}")
        self.layout = QVBoxLayout(self)

        self.records_list = QListWidget(self)
        self.layout.addWidget(self.records_list)
        self.update_records(records)

        # Кнопка для добавления записи
        self.add_record_button = QPushButton("Добавить запись")
        self.add_record_button.clicked.connect(lambda: self.add_record(fields))
        self.layout.addWidget(self.add_record_button)

        # Кнопка для удаления записи
        self.remove_record_button = QPushButton("Удалить запись")
        self.remove_record_button.clicked.connect(self.remove_record)
        self.layout.addWidget(self.remove_record_button)

        # Кнопка для обновления записей
        self.refresh_records_button = QPushButton("Обновить записи")
        self.refresh_records_button.clicked.connect(self.refresh_records)
        self.layout.addWidget(self.refresh_records_button)

    def update_records(self, records):
        """Обновить список записей."""
        self.records_list.clear()
        for record in records:
            # Форматируем запись для более читабельного отображения
            record_display = ", ".join(f"{key}: {value}" for key, value in record.items())
            self.records_list.addItem(record_display)

    def add_record(self, fields):
        """Добавить новую запись через диалог."""
        record_data = {}
        for field in fields:
            value, ok = QInputDialog.getText(self, f"Введите значение для {field[0]}:", field[0])
            if ok:
                record_data[field[0]] = value
            else:
                return  # Если пользователь нажал Cancel, не добавляем запись

        # Отправка запроса на добавление записи на сервер
        self.parent().client.add_record(self.parent().table_list.currentItem().text(), record_data)

        # Обновление списка записей после добавления
        self.update_records(self.parent().client.get_records(self.parent().table_list.currentItem().text()))

    def remove_record(self):
        """Удалить выбранную запись из списка."""
        selected_item = self.records_list.currentItem()
        if selected_item:
            row = self.records_list.row(selected_item)
            # Получаем текст записи для удаления
            record_text = selected_item.text()
            record = {key: value for key, value in (item.split(": ") for item in record_text.split(", "))}

            # Логика для удаления записи на сервере
            self.parent().client.delete_record(self.parent().table_list.currentItem().text(), record)
            self.update_records(self.parent().client.get_records(self.parent().table_list.currentItem().text()))  # Обновляем записи

    def refresh_records(self):
        """Обновить записи с сервера."""
        table_name = self.parent().table_list.currentItem().text()
        records = self.parent().client.get_records(table_name)
        self.update_records(records)


class FieldDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить поле")
        self.layout = QVBoxLayout(self)

        self.fields_list = QListWidget(self)
        self.layout.addWidget(QLabel("Список полей:"))
        self.layout.addWidget(self.fields_list)

        form_layout = QFormLayout()
        self.name_input = QLineEdit(self)
        form_layout.addRow("Имя поля:", self.name_input)

        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["INTEGER", "TEXT", "REAL", "CHAR"])
        form_layout.addRow("Тип данных:", self.type_combo)

        self.layout.addLayout(form_layout)

        # Кнопки для добавления и удаления поля
        buttons_layout = QHBoxLayout()
        self.add_field_button = QPushButton("Добавить поле")
        self.add_field_button.clicked.connect(self.add_field)
        buttons_layout.addWidget(self.add_field_button)

        self.remove_field_button = QPushButton("Удалить поле")
        self.remove_field_button.clicked.connect(self.remove_field)
        buttons_layout.addWidget(self.remove_field_button)

        self.layout.addLayout(buttons_layout)

        # Кнопки OK и Отмена
        action_buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.clicked.connect(self.reject)
        action_buttons_layout.addWidget(self.ok_button)
        action_buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(action_buttons_layout)

        self.fields = []

    def add_field(self):
        """Добавить поле в список."""
        field_name = self.name_input.text()
        field_type = self.type_combo.currentText()

        if field_name:
            self.fields.append((field_name, field_type))
            self.fields_list.addItem(f"{field_name} ({field_type})")

            # Очищаем поля ввода для нового поля
            self.name_input.clear()
            self.type_combo.setCurrentIndex(0)

    def remove_field(self):
        """Удалить выбранное поле из списка."""
        selected_item = self.fields_list.currentItem()
        if selected_item:
            row = self.fields_list.row(selected_item)
            self.fields_list.takeItem(row)
            del self.fields[row]

    def get_fields(self):
        return self.fields

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

        # Обработчик двойного клика для добавления записи
        self.table_list.itemDoubleClicked.connect(self.add_record)

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

    def add_record(self):
        """Открыть диалог для отображения записей и управления ими."""
        selected_item = self.table_list.currentItem()
        if selected_item:
            table_name = selected_item.text()
            fields = self.client.get_table_fields(table_name)  # Получаем поля
            records = self.client.get_records(table_name)  # Получаем записи для таблицы

            dialog = RecordDialog(table_name, fields, records, self)
            dialog.exec()  # Открыть диалог


    def add_table(self):
        """Добавить новую таблицу."""
        table_name, ok = QInputDialog.getText(self, "Добавить таблицу", "Введите имя таблицы:")
        if ok and table_name:
            dialog = FieldDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                fields = dialog.get_fields()
                
                if fields:
                    response = self.client.create_table(table_name, fields)
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
