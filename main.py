from errors import *

# TOKEN TYPES
INTEGER, OPERATOR, EOF, SPACE = "INTEGER", "OPERATOR", "EOF", "SPACE"

# Language
lang = 'en'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()


class Interpreter(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None
        self.current_char = self.text[self.pos]

    def error(self, case):
        match case:
            case 'p': raise Exception(PARSING_ERROR[lang])
            case 'd0': raise Exception(DIVIDING_BY_ZERO[lang])
            case _: raise Exception('ERROR')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.ignore_spaces()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char in '+-*/':
                op = Token(OPERATOR, self.current_char)
                self.advance()
                return op

            self.error('p')

        return Token(EOF, None)

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def ignore_spaces(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error('p')

    def term(self):
        result = self.current_token
        self.eat(INTEGER)
        return result.value

    def expr(self):
        """expr -> INTEGER OPERATOR INTEGER"""

        self.current_token = self.get_next_token()

        left = self.term()

        while self.current_token.type != EOF:
            op = self.current_token
            self.eat(OPERATOR)

            right = self.term()

            match op.value:
                case '+':
                    left += right
                case '-':
                    left -= right
                case '*':
                    left *= right
                case '/':
                    if right == 0:
                        self.error('d0')
                    left /= right
                    if left == int(left):
                        left = int(left)

        return left


def main():
    while True:
        try:
            text = input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)


if __name__ == '__main__':
    main()
