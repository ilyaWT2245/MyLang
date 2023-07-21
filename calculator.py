from errors import *

# TOKENS
INTEGER, OPERATOR, EOF, SPACE = 'INTEGER', 'OPERATOR', 'EOF', 'SPACE'

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
        self.current_token = None
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self, error):
        raise Exception(error)

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def ignore_spaces(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.ignore_spaces()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char in '+-*/':
                char = self.current_char
                self.advance()
                return Token(OPERATOR, char)

            self.error(PARSING_ERROR[lang])

        return Token(EOF, None)

    def term(self):
        result = self.current_token
        self.eat(INTEGER)
        return result.value

    def eat(self, token_type):
        if self.current_token.type != token_type:
            self.error(PARSING_ERROR[lang])
        self.current_token = self.get_next_token()

    def expr(self):
        """expr -> INTEGER OPERATOR INTEGER"""

        self.current_token = self.get_next_token()

        result = self.term()

        while self.current_token.type != EOF:
            op = self.current_token
            self.eat(OPERATOR)

            right = self.term()
            match op.value:
                case '+':
                    result += right
                case '-':
                    result -= right
                case '*':
                    result *= right
                case '/':
                    if right == 0:
                        self.error(DIVIDING_BY_ZERO[lang])
                    result /= right

        return result


def main():
    while True:
        try:
            text = input('calc>')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)

