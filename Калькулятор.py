#Создание своей ошибки, специально для калькулятора (будем выводить в некоторых моментах)
class CalcError(Exception):
    pass

#Лексер (разбиваем выражение на токены)
def tokenize(expression):
    tokens = []
    i = 0
    n = len(expression)

    #Старт перебора. Каждый символ строки перебираем
    while i < n:
        ch = expression[i]

        #Скип пробелов
        if ch.isspace():
            i += 1
            continue

        #Распознаем числа (целые и дробные)
        if ch.isdigit() or (ch == '.' and i + 1 < n and expression[i + 1].isdigit()):
            start = i
            has_dot = False

            #Проверка на то, что число дробное (меняем флаг has_dot, если да, чтоб больше точек не было)
            while i < n and (expression[i].isdigit() or (expression[i] == '.' and not has_dot)):
                if expression[i] == '.':
                    has_dot = True
                i += 1

            text = expression[start:i]

            #Вводим токен, что мы получили на входе число (или выводим ошибку, если на входе подана фигня)
            try:
                tokens.append(('NUMBER', float(text)))
            except ValueError:
                raise CalcError(f"Некорректное число: {text}")

            continue

        #Вариант 31: Функция abs()
        if ch.isalpha(): #Проверяем, является ли символ буквой
            start = i

            while i < n and expression[i].isalpha():
                i += 1

            name = expression[start:i].lower()

            if name == 'abs':
                tokens.append(('ABS', 'abs'))
            else:
                raise CalcError(
                    f"Неизвестная функция: {name}. "
                    f"Программа поддерживает лишь функцию abs()."
                )

            continue

        #Обычные операторы и скобки
        if ch in '+-*/()':
            tokens.append((ch, ch))
            i += 1
            continue

        #Вариант 1: Оператор ==
        if ch == '=':
            if i + 1 < n and expression[i + 1] == '=':
                tokens.append(('NEQ', '=='))
                i += 2
                continue

            raise CalcError("После '=' ожидается '=' для оператора '=='")

        raise CalcError(f"Недопустимый символ: '{ch}'")

    #Конец заданной строки
    tokens.append(('EOF', None))
    return tokens


class Parser:
    #Приоритеты:
    #1: Скобки и функция abs()
    #2: Унарный + и унарный -
    #3: * и /
    #4: + и -
    #5: !=
    #В коде начинаем с самого низкого приоритета

    #Возвращаем все токены и устанавливаем позицию на первую (начало)
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    #Возвращаем текущую позицию (текущий токен)
    @property #делаем функцию свойством, чтоб не писать лишние скобочки. Крч, для удобства сделано, не более.
    def current(self):
        return self.tokens[self.pos]

    #Проверка, чтобы исключить неправильно введенные функции/ошибки ввода.фиы
    def eat(self, expected_type):
        token = self.current

        if token[0] != expected_type:
            got = token[0]
            raise CalcError(f"Ожидалось '{expected_type}', получено: {got}")

        self.pos += 1
        return token

    def parse(self):
        result = self.expression()
        self.eat('EOF')
        return float(result)

    def expression(self):
        return self.comparison()

    #Оператор !=
    def comparison(self):
        left = self.additive()

        while self.current[0] == 'NEQ':
            self.eat('NEQ')
            right = self.additive()
            left = 1.0 if left == right else 0.0

        return left

    #Сложение и вычитание
    def additive(self):
        left = self.term()

        while self.current[0] in ('+', '-'):
            op = self.eat(self.current[0])[0]
            right = self.term()

            if op == '+':
                left += right
            else:
                left -= right

        return left

    #Умножение и деление
    def term(self):
        left = self.factor()

        while self.current[0] in ('*', '/'):
            op = self.eat(self.current[0])[0]
            right = self.factor()

            if op == '*':
                left *= right
            else:
                if right == 0:
                    raise CalcError("Деление на ноль недопустимо")
                left /= right
        return left

    def factor(self):
        return self.unary()

    #Унарные плюс и минус
    def unary(self):
        if self.current[0] == '-':
            self.eat('-')
            return -self.unary()

        if self.current[0] == '+':
            self.eat('+')
            return self.unary()

        return self.primary()

    #Числа, скобки и abs()
    def primary(self):
        token = self.current
        match token[0]:
            case 'NUMBER':
                self.eat('NUMBER')
                return float(token[1])
            case 'ABS':
                self.eat('ABS')
                self.eat('(')
                value = self.expression()
                self.eat(')')
                return value if value >= 0 else -value
            case '(':
                self.eat('(')
                value = self.expression()
                self.eat(')')
                return value
            case 'EOF':
                raise CalcError("Пустая строка или неожиданный конец выражения")
            case _:
                raise CalcError(f"Неожиданный токен: {token[0]}")

#Собственно, вычисляет
def calculate(expression) -> float:
    tokens = tokenize(expression)
    parser = Parser(tokens)
    return parser.parse()

#Собственно, форматирует
def format_result(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

#Собственно, начало (но в конце xD)
def main():
    print("Консольный калькулятор")
    print("Доступна поддержка функции abs() и оператора ==")
    print("Для выхода введите quit")

    while True:
        try:
            expression = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if expression.lower() in {'quit'}:
            break

        try:
            result = calculate(expression)
            print(format_result(result))
        except CalcError as error:
            print(f"Ошибка: {error}")

#Сам запуск программы
if __name__ == "__main__":
    main()