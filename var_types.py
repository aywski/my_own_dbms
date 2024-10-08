class DataType:
    def __init__(self, data, selected_type):
        self.data = data
        self.selected_type = selected_type
        self.type_checkers = {
            "INTEGER": self._check_integer,
            "TEXT": self._check_text,
            "REAL": self._check_real,
            "CHAR": self._check_char,
            "CHARINVL": self._check_charInvl,
            "string(CHARINVL)": self._check_string_charInvl
        }

    def check_field_type(self):
        checker = self.type_checkers.get(self.selected_type)
        if checker:
            return checker()
        return False

    def _check_integer(self):
        try:
            self.data = int(self.data)
            return True
        except ValueError:
            return False

    def _check_text(self):
        return isinstance(self.data, str)

    def _check_real(self):
        try:
            self.data = float(self.data)
            return True
        except ValueError:
            return False

    def _check_char(self):
        return isinstance(self.data, str) and len(self.data) == 1

    def _check_charInvl(self):
        """Проверка диапазона символов, например '(B - D)'."""
        try:
            # Убираем пробелы, скобки и разделяем по символу '-'
            cleaned_data = self.data.replace(" ", "").replace("(", "").replace(")", "")
            parts = cleaned_data.split("-")
            if len(parts) != 2:
                return False

            start_char, end_char = parts[0], parts[1]
            # Проверяем, что это одиночные символы
            if len(start_char) == 1 and len(end_char) == 1:
                # Проверяем, что первый символ не больше второго по порядку
                return ord(start_char) <= ord(end_char)
            return False
        except:
            return False

    def _check_string_charInvl(self):
        """Проверка списка символов, например '(B, C, D)'."""
        try:
            # Убираем пробелы, скобки и разбиваем по запятым
            cleaned_data = self.data.replace(" ", "").replace("(", "").replace(")", "")
            chars = [char.strip() for char in cleaned_data.split(",")]

            # Проверяем, что все элементы одиночные символы
            if all(len(char) == 1 for char in chars):
                # Проверяем, что символы идут по порядку
                return all(ord(chars[i]) < ord(chars[i + 1]) for i in range(len(chars) - 1))
            return False
        except:
            return False


# using new type
# lowercase = CharInvl('a', 'z')
# print(DataType(123, "INTEGER").check_field_type())  # True
# print(DataType("Hello", "TEXT").check_field_type())  # True
# print(DataType(3.14, "REAL").check_field_type())  # True
# print(DataType("A", "CHAR").check_field_type())  # True
# print(DataType(lowercase, "CHARINVL").check_field_type())  # True
# print(DataType(("hello", lowercase), "string(CHARINVL)").check_field_type())  # True
# print(DataType(("HELLO", lowercase), "string(CHARINVL)").check_field_type())  # False