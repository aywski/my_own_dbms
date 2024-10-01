class CharInvl:
    def __init__(self, start, end):
        if not (isinstance(start, str) and isinstance(end, str) and
                len(start) == 1 and len(end) == 1):
            raise ValueError("Start and end must be single characters")
        if ord(start) > ord(end):
            raise ValueError("Start character must come before end character in ASCII order")
        self.start = start
        self.end = end

    def __contains__(self, char):
        return ord(self.start) <= ord(char) <= ord(self.end)

    def __str__(self):
        return f"[{self.start}-{self.end}]"

    def __repr__(self):
        return f"CharInvl('{self.start}', '{self.end}')"

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
        return isinstance(self.data, CharInvl)

    def _check_string_charInvl(self):
        if not isinstance(self.data, tuple) or len(self.data) != 2:
            return False
        string, char_invl = self.data
        if not isinstance(string, str) or not isinstance(char_invl, CharInvl):
            return False
        return all(char in char_invl for char in string)

# using new type
lowercase = CharInvl('a', 'z')
print(DataType(123, "INTEGER").check_field_type())  # True
print(DataType("Hello", "TEXT").check_field_type())  # True
print(DataType(3.14, "REAL").check_field_type())  # True
print(DataType("A", "CHAR").check_field_type())  # True
print(DataType(lowercase, "CHARINVL").check_field_type())  # True
print(DataType(("hello", lowercase), "string(CHARINVL)").check_field_type())  # True
print(DataType(("HELLO", lowercase), "string(CHARINVL)").check_field_type())  # False