from errors import *

# TOKENS
INTEGER, OPERATOR, EOF, SPACE = 'INTEGER', 'OPERATOR', 'EOF', 'SPACE'
BRACKET_LEFT, BRACKET_RIGHT = 'BRACKET_LEFT', 'BRACKET_RIGHT'

OPERATORS = ('+', '-', '*', '/')

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


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

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

            if self.current_char in OPERATORS:
                char = self.current_char
                self.advance()
                return Token(OPERATOR, char)

            if self.current_char == '(':
                self.advance()
                return Token(BRACKET_LEFT, '(')

            if self.current_char == ')':
                self.advance()
                return Token(BRACKET_RIGHT, ')')

            error(INVALID_CHAR[lang])

        return Token(EOF, None)


class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def factor(self):
        result = self.current_token
        self.eat(INTEGER)
        return result.value

    def staple(self):
        """staple: factor|expr"""

        if self.current_token.type == BRACKET_LEFT:
            result = self.expr()
        else:
            result = self.factor()

        return result

    def term(self):
        """term: factor ((mult|div factor))*"""

        result = self.staple()
        while self.current_token.value in ('*', '/'):
            op = self.current_token
            self.eat(OPERATOR)

            right = self.staple()
            match op.value:
                case '*':
                    result *= right
                case '/':
                    result /= right
                    if result == int(result):
                        result = int(result)
        return result

    def eat(self, token_type):
        if self.current_token.type != token_type:
            error(INVALID_SYNTAX[lang])
        self.current_token = self.lexer.get_next_token()

    def expr(self):
        """Arithmetic expressions parser

           expr: term ((plus|minus) term)*
           term: staple ((mult|div) staple)*
           staple: factor|expr
           factor: INTEGER
           plus: OPERATOR
           minus: OPERATOR
           mult: OPERATOR
           div: OPERATOR"""

        self.current_token = self.lexer.get_next_token()

        result = self.term()

        while self.current_token.type != EOF:
            if self.current_token.type not in (OPERATOR, BRACKET_RIGHT):
                error(INVALID_SYNTAX[lang])

            match self.current_token.value:
                case ')':
                    self.eat(BRACKET_RIGHT)
                    break
                case '+':
                    self.eat(OPERATOR)
                    result += self.term()
                case '-':
                    self.eat(OPERATOR)
                    result -= self.term()

        return result


def error(e):
    raise Exception(e)


def main():
    while True:
        try:
            text = input('calc>')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.expr()
        print(result)
