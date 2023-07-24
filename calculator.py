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
        self.current_token = self.lexer.get_next_token()

    def factor(self):
        """factor: INTEGER|BRACKET_LEFT expr BRACKET_RIGHT"""
        if self.current_token.type == BRACKET_LEFT:
            self.eat(BRACKET_LEFT)
            result = self.expr()
            self.eat(BRACKET_RIGHT)
        else:
            result = self.current_token.value
            self.eat(INTEGER)

        return result

    def term(self):
        """term: factor ((mult|div factor))*"""

        result = self.factor()
        while self.current_token.value in ('*', '/'):
            match self.current_token:
                case '*':
                    self.eat(OPERATOR)
                    result *= self.factor()
                case '/':
                    self.eat(OPERATOR)
                    result /= self.factor()
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
           term: factor ((mult|div) factor)*
           factor: INTEGER|BRACKET_LEFT expr BRACKET_RIGHT
           plus: OPERATOR
           minus: OPERATOR
           mult: OPERATOR
           div: OPERATOR"""

        result = self.term()

        while self.current_token.type != EOF:
            match self.current_token.value:
                case ')':
                    return result
                case '+':
                    self.eat(OPERATOR)
                    result += self.term()
                case '-':
                    self.eat(OPERATOR)
                    result -= self.term()
                case _:
                    error(INVALID_SYNTAX[lang])

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
