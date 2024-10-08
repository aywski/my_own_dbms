from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QLabel, QListWidget, QHBoxLayout, QInputDialog, QMessageBox,
    QDialog, QFormLayout, QComboBox
)
from rest_client import RestClient
import sys
import re

class RecordDialog(QDialog):
    def __init__(self, table_name, fields, records, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Records for {table_name}")
        self.layout = QVBoxLayout(self)

        self.records_list = QListWidget(self)
        self.layout.addWidget(self.records_list)
        self.update_records(records)

        # Кнопка для добавления записи
        self.add_record_button = QPushButton("Add record")
        self.add_record_button.clicked.connect(lambda: self.add_record(fields))
        self.layout.addWidget(self.add_record_button)

        # Кнопка для удаления записи
        self.remove_record_button = QPushButton("Remove record")
        self.remove_record_button.clicked.connect(self.remove_record)
        self.layout.addWidget(self.remove_record_button)

        # Кнопка для удаления дубликатов
        self.remove_duplicates_button = QPushButton("Remove duplicates")
        self.remove_duplicates_button.clicked.connect(self.remove_duplicates)
        self.layout.addWidget(self.remove_duplicates_button)

        # Кнопка для обновления записей
        self.refresh_records_button = QPushButton("Refresh")
        self.refresh_records_button.clicked.connect(self.refresh_records)
        self.layout.addWidget(self.refresh_records_button)

    def remove_duplicates(self):
        table_name = self.parent().table_list.currentItem().text()
        response = self.parent().client.remove_duplicates(table_name)
        if response and "success" in response:
            QMessageBox.information(self, "Succsess", f"{response['removed_count']} duplicates was removed.")
            self.refresh_records()
        else:
            QMessageBox.warning(self, "Error", "Cann't remove duplicates.")

    def update_records(self, records):
        self.records_list.clear()
        for record in records:
            record_display = f"ID: {record['id']}, " + ", ".join(f"{key}: {value}" for key, value in record.items() if key != 'id')
            self.records_list.addItem(record_display)

    def add_record(self, fields):
        record_data = {}
        for field in fields:
            field_name, field_type = field[0], field[1]

            if field_type == "CHARINVL" or field_type == "string(CHARINVL)":
                # Для этих типов данных отображаем два поля для ввода диапазона
                start_value, ok1 = QInputDialog.getText(self, f"Enter start of interval {field_name}:", field_name)
                if not ok1:
                    return

                end_value, ok2 = QInputDialog.getText(self, f"Enter end of interval {field_name}:", field_name)
                if not ok2:
                    return

                if field_type == "CHARINVL":
                    # Формат для CHARINVL: (B - D)
                    record_data[field_name] = f"({start_value} - {end_value})"
                elif field_type == "string(CHARINVL)":
                    # Формат для string(CHARINVL): (B, C, D)
                    record_data[field_name] = f"({', '.join(chr(c) for c in range(ord(start_value), ord(end_value) + 1))})"
            else:
                value, ok = QInputDialog.getText(self, f"Enter value for {field_name}:", field_name)
                if ok:
                    record_data[field_name] = value
                else:
                    return  # Если пользователь нажал Cancel, не добавляем запись

        # Отправка запроса на добавление записи на сервер
        self.parent().client.add_record(self.parent().table_list.currentItem().text(), record_data)

        # Обновление списка записей после добавления
        self.update_records(self.parent().client.get_records(self.parent().table_list.currentItem().text()))

    def remove_record(self):
        selected_item = self.records_list.currentItem()
        if selected_item:
            record_text = selected_item.text()

            # Извлекаем ID записи
            pattern = r"ID: (\d+)"
            match = re.search(pattern, record_text)
            if match:
                record_id = int(match.group(1))

                # Логика для удаления записи на сервере
                self.parent().client.delete_record(self.parent().table_list.currentItem().text(), record_id)
                self.update_records(self.parent().client.get_records(self.parent().table_list.currentItem().text()))  # Обновляем записи
            else:
                QMessageBox.warning(self, "Error", "Cann't get ID's.")

    def refresh_records(self):
        table_name = self.parent().table_list.currentItem().text()
        records = self.parent().client.get_records(table_name)
        self.update_records(records)

class FieldDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add field")
        self.layout = QVBoxLayout(self)

        self.fields_list = QListWidget(self)
        self.layout.addWidget(QLabel("List of fields:"))
        self.layout.addWidget(self.fields_list)

        form_layout = QFormLayout()
        self.name_input = QLineEdit(self)
        form_layout.addRow("Field name:", self.name_input)

        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["INTEGER", "TEXT", "REAL", "CHAR", "CHARINVL", "string(CHARINVL)"])
        form_layout.addRow("Data type:", self.type_combo)

        self.layout.addLayout(form_layout)

        # Кнопки для добавления и удаления поля
        buttons_layout = QHBoxLayout()
        self.add_field_button = QPushButton("Add field")
        self.add_field_button.clicked.connect(self.add_field)
        buttons_layout.addWidget(self.add_field_button)

        self.remove_field_button = QPushButton("Remove field")
        self.remove_field_button.clicked.connect(self.remove_field)
        buttons_layout.addWidget(self.remove_field_button)

        self.layout.addLayout(buttons_layout)

        # Кнопки OK и Отмена
        action_buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        action_buttons_layout.addWidget(self.ok_button)
        action_buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(action_buttons_layout)

        self.fields = []

    def add_field(self):
        field_name = self.name_input.text()
        field_type = self.type_combo.currentText()

        if field_name:
            self.fields.append((field_name, field_type))
            self.fields_list.addItem(f"{field_name} ({field_type})")

            # Очищаем поля ввода для нового поля
            self.name_input.clear()
            self.type_combo.setCurrentIndex(0)

    def remove_field(self):
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
        self.layout.addWidget(QLabel("Tables:"))
        self.layout.addWidget(self.table_list)
        self.load_tables()

        # Обработчик двойного клика для добавления записи
        self.table_list.itemDoubleClicked.connect(self.add_record)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Добавление таблицы
        self.add_table_button = QPushButton("Add Table")
        self.add_table_button.clicked.connect(self.add_table)
        buttons_layout.addWidget(self.add_table_button)

        # Удаление таблицы
        self.delete_table_button = QPushButton("Remove Table")
        self.delete_table_button.clicked.connect(self.delete_table)
        buttons_layout.addWidget(self.delete_table_button)

        # Обновить список
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_tables)
        buttons_layout.addWidget(self.refresh_button)

        self.layout.addLayout(buttons_layout)

        # Основной виджет
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def load_tables(self):
        self.table_list.clear()
        tables = self.client.get_tables()
        if tables:
            for table in tables:
                self.table_list.addItem(table)
        else:
            self.table_list.addItem("Empty.")

    def add_record(self):
        selected_item = self.table_list.currentItem()
        try:
            if selected_item:
                table_name = selected_item.text()
                fields = self.client.get_table_fields(table_name)  # Получаем поля
                records = self.client.get_records(table_name)  # Получаем записи для таблицы

                dialog = RecordDialog(table_name, fields, records, self)
                dialog.exec()  # Открыть диалог
        except Exception as e:
            QMessageBox.information(self, ":c", f"Error: {str(e)}")

    def add_table(self):
        table_name, ok = QInputDialog.getText(self, "Add Table", "Enter the table name:")
        if ok and table_name:
            dialog = FieldDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                fields = dialog.get_fields()
                
                if fields:
                    response = self.client.create_table(table_name, fields)
                    if response:
                        QMessageBox.information(self, "Succsess", f"Table {table_name} is created.")
                    else:
                        QMessageBox.warning(self, "Error", "Cann't create table")
                    self.load_tables()

    def delete_table(self):
        selected_item = self.table_list.currentItem()
        if selected_item:
            table_name = selected_item.text()
            if table_name != "Empty.":
                response = self.client.delete_table(table_name)
                if response:
                    QMessageBox.information(self, "Succsess", f"Table {table_name} is created.")
                else:
                    QMessageBox.warning(self, "Error", "Cann't create table")
                self.load_tables()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
