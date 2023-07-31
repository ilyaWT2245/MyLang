from errors import *

# Language
lang = 'en'

#########
# Lexer #
#########

# Tokens
INTEGER, OPERATOR, EOF, SPACE = 'INTEGER', 'OPERATOR', 'EOF', 'SPACE'
BRACKET_LEFT, BRACKET_RIGHT = 'BRACKET_LEFT', 'BRACKET_RIGHT'
BEGIN, END, SEMI, ID, DOT, ASSIGN = 'BEGIN', 'END', 'SEMI', 'ID', 'DOT', 'ASSIGN'

OPERATORS = ('+', '-', '*', '/')


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.RESERVED_KEYWORDS = {
            'BEGIN': Token(BEGIN, 'BEGIN'),
            'END': Token(END, 'END')
        }

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

    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        return self.RESERVED_KEYWORDS.get(result, Token(ID, result))

    def see_next_char(self):
        pos = self.pos + 1
        if pos > len(self.text) + 1:
            return None
        else:
            return self.text[pos]

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

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == ':' and self.see_next_char() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

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


class UnOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Compound(AST):
    def __init__(self):
        self.children = []


class AssignOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


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
        """factor: (plus|minus) factor
                 | INTEGER
                 | BRACKET_LEFT expr BRACKET_RIGHT
                 | variable
        """

        token = self.current_token
        if token.type == BRACKET_LEFT:
            self.eat(BRACKET_LEFT)
            node = self.expr()
            self.eat(BRACKET_RIGHT)
            return node

        elif token.value in ('+', '-'):
            self.eat(OPERATOR)
            return UnOp(token, self.factor())

        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        else:
            return self.variable()

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
           factor: (plus|minus) factor
                 | INTEGER
                 | BRACKET_LEFT expr BRACKET_RIGHT
                 | variable
           plus: OPERATOR
           minus: OPERATOR
           mult: OPERATOR
           div: OPERATOR"""

        node = self.term()

        while self.current_token.value in ('+', '-'):
            token = self.current_token
            self.eat(OPERATOR)
            node = BinOp(left=node, op=token, right=self.term())

        if self.current_token.type == INTEGER:
            error(INVALID_SYNTAX[lang])

        return node

    def variable(self):
        """variable: ID"""

        token = self.current_token
        self.eat(ID)
        return Var(token)

    def empty(self):
        return NoOp()

    def assignment_statement(self):
        """assignment_statement: variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        return AssignOp(left=left, op=token, right=right)

    def statement(self):
        """statement: compound_statement
                    | assignment_statement
                    | empty
        """

        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()

        return node

    def statements_list(self):
        """statements_list: statement (SEMI statement)*"""

        node = self.statement()
        nodes = [node]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            nodes.append(self.statement())

        return nodes

    def compound_statement(self):
        """compound_statement: BEGIN statements_list END"""

        self.eat(BEGIN)
        nodes = self.statements_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def program(self):
        """program: compound_statement DOT
           compound_statement: BEGIN statements_list END
           statements_list: statement (SEMI statement)*
           statement: compound_statement
                    | assignment_statement
                    | empty
           assignment_statement: variable ASSIGN expr
           variable: ID
           empty:
        """

        node = self.compound_statement()
        self.eat(DOT)
        return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            error(INVALID_SYNTAX[lang])
        return node

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
        self.GLOBAL_SCOPE = {}

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

    def visit_UnOp(self, node):
        if node.op.value == '+':
            return +self.visit(node.expr)
        elif node.op.value == '-':
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for n in node.children:
            self.visit(n)

    def visit_AssignOp(self, node):
        var = node.left.value
        value = self.visit(node.right)
        self.GLOBAL_SCOPE[var] = value

    def visit_Var(self, node):
        name = node.value
        value = self.GLOBAL_SCOPE.get(name, None)
        if value is None:
            raise NameError(repr(name))
        else:
            return value

    def visit_NoOp(self, node):
        return None

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

