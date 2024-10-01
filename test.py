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

# Пример использования
lowercase = CharInvl('a', 'z')
print(lowercase)  # Выведет: [a-z]
print('m' in lowercase)  # Выведет: True
print('A' in lowercase)  # Выведет: False

digits = CharInvl('0', '9')
print(digits)  # Выведет: [0-9]
print('5' in digits)  # Выведет: True
print('x' in digits)  # Выведет: False