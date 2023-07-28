from errors import *

# Language
lang = 'en'

#########
# Lexer #
#########

# TOKENS
INTEGER, OPERATOR, EOF, SPACE = 'INTEGER', 'OPERATOR', 'EOF', 'SPACE'
BRACKET_LEFT, BRACKET_RIGHT = 'BRACKET_LEFT', 'BRACKET_RIGHT'

OPERATORS = ('+', '-', '*', '/')


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

##########
# Parser #
##########


class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def factor(self):
        """factor: INTEGER|BRACKET_LEFT expr BRACKET_RIGHT"""
        token = self.current_token
        if self.current_token.type == BRACKET_LEFT:
            self.eat(BRACKET_LEFT)
            node = self.expr()
            self.eat(BRACKET_RIGHT)
            return node
        else:
            self.eat(INTEGER)
            return Num(token)

    def term(self):
        """term: factor ((mult|div factor))*"""

        node = self.factor()
        while self.current_token.value in ('*', '/'):
            token = self.current_token
            self.eat(OPERATOR)
            node = BinOp(left=node, op=token, right=self.factor())

        return node

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

        node = self.term()

        while self.current_token.type != EOF:
            token = self.current_token
            if token.type == BRACKET_RIGHT:
                return node
            self.eat(OPERATOR)
            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()

###############
# Interpreter #
###############


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.default_visit)
        return visitor(node)

    def default_visit(self, node):
        raise Exception(f'visit_{type(node).__name__} is not defined')


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        match node.op.value:
            case '+':
                return self.visit(node.left) + self.visit(node.right)
            case '-':
                return self.visit(node.left) - self.visit(node.right)
            case '*':
                return self.visit(node.left) * self.visit(node.right)
            case '/':
                result = self.visit(node.left) / self.visit(node.right)
                if result == int(result):
                    result = int(result)
                return result

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


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
        parser = Parser(lexer)
        interpreter = Interpreter(parser)

        print(interpreter.interpret())

