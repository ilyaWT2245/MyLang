from errors import *
from tokens import *
from collections import OrderedDict

# Language
lang = 'en'

#########
# Lexer #
#########

OPERATORS = ('+', '-', '*', '/')


class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type


class BuiltInSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return f'name={self.name}'

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.__str__()})>'


class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return f'name={self.name}, type={self.type}'

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.__str__()})>'


class SymbolTable(object):
    def __init__(self):
        self._symbols = OrderedDict()
        self.init_builtins()

    def init_builtins(self):
        self.define(BuiltInSymbol(INTEGER))
        self.define(BuiltInSymbol(REAL))

    def __str__(self):
        return f'Symbols: {[value for value in self._symbols.values()]}'

    __repr__ = __str__

    def define(self, symbol):
        print('Define: %s' % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print('Lookup: %s' % name)
        return self._symbols.get(name)


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.RESERVED_KEYWORDS = {
            'begin': Token(BEGIN, 'BEGIN'),
            'end': Token(END, 'END'),
            'div': Token(OPERATOR, 'DIV'),
            'program': Token(PROGRAM, 'PROGRAM'),
            'var': Token(VAR, 'VAR'),
            'integer': Token(INTEGER, 'INTEGER'),
            'real': Token(REAL, 'REAL'),
            'procedure': Token(PROCEDURE, 'PROCEDURE')
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

    def ignore_comment(self):
        while self.current_char is not None and self.current_char != '}':
            self.advance()
        if self.current_char is None:
            error(COMMENT_CLOSING[lang])

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            token = Token(REAL_CONST, float(result))
        else:
            token = Token(INTEGER_CONST, int(result))
        return token

    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum() or self.current_char == '_':
            result += self.current_char
            self.advance()

        result = result.lower()
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

            if self.current_char == '{':
                self.ignore_comment()
                self.advance()
                continue

            if self.current_char.isdigit():
                return self.number()

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

            if self.current_char.isalpha() or self.current_char == '_':
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

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':')

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


class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block


class Block(AST):
    def __init__(self, var_decl, compound_statement):
        self.declarations = var_decl
        self.compound_statement = compound_statement


class ProcedureDecl(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block


class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node


class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Token(object):
    def __init__(self, _type, value):
        self.type = _type
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
                 | INTEGER_CONST
                 | REAL_CONST
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

        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)

        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)

        else:
            return self.variable()

    def term(self):
        """term: factor ((mult|div|DIV factor))*"""

        node = self.factor()
        while self.current_token.value in ('*', 'DIV', '/'):
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
                 | INTEGER_CONST
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

        if self.current_token.type == INTEGER_CONST:
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

    def type(self):
        """type: INTEGER | REAL"""
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
        elif self.current_token.type == REAL:
            self.eat(REAL)
        return Type(token)

    def variable_declaration(self):
        """variable_declaration: ID (COMMA ID)* COLON type"""
        var_nodes = [Var(self.current_token)]
        self.eat(ID)

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)

        self.eat(COLON)
        var_type = self.type()

        var_declarations = [VarDecl(var_node, var_type) for var_node in var_nodes]
        return var_declarations

    def declarations(self):
        """declarations: VAR (variable_declaration SEMI)+
                       | (PROCEDURE ID SEMI block SEMI)*
                       | empty"""

        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                declarations.extend(self.variable_declaration())
                self.eat(SEMI)

        while self.current_token.type == PROCEDURE:
            self.eat(PROCEDURE)
            procedure_name = self.current_token.value
            self.eat(ID)
            self.eat(SEMI)
            block_node = self.block()
            declarations.append(ProcedureDecl(procedure_name, block_node))
            self.eat(SEMI)

        return declarations

    def block(self):
        """block: declarations compound_statement"""

        declarations_node = self.declarations()
        compound_statement_node = self.compound_statement()
        return Block(declarations_node, compound_statement_node)

    def program(self):
        """program: PROGRAM variable SEMI block DOT

           block: declarations compound_statement

           declarations: VAR (variable_declaration SEMI)+
                       | (PROCEDURE ID SEMI block SEMI)*
                       | empty

           variable_declaration: ID (COMMA ID)* COLON type

           type: INTEGER | REAL

           compound_statement: BEGIN statements_list END

           statements_list: statement (SEMI statement)*

           statement: compound_statement
                    | assignment_statement
                    | empty

           assignment_statement: variable ASSIGN expr

           variable: ID

           empty:

           expr: term ((plus|minus) term)*
           term: factor ((mult|div) factor)*
           factor: (plus|minus) factor
                 | INTEGER_CONST
                 | BRACKET_LEFT expr BRACKET_RIGHT
                 | variable
           plus: OPERATOR
           minus: OPERATOR
           mult: OPERATOR
           div: OPERATOR
        """

        self.eat(PROGRAM)
        name = self.variable().value
        self.eat(SEMI)
        block = self.block()
        self.eat(DOT)
        node = Program(name, block)
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
                return self.visit(node.left) / self.visit(node.right)
            case 'DIV':
                return self.visit(node.left) // self.visit(node.right)

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

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for decl_node in node.declarations:
            self.visit(decl_node)
        self.visit(node.compound_statement)

    def visit_ProcedureDecl(self, node):
        pass

    def visit_VarDecl(self, node):
        return None

    def visit_Type(self, node):
        return None

    def visit_NoOp(self, node):
        return None

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node):
        pass

    def visit_UnOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for n in node.children:
            self.visit(n)

    def visit_AssignOp(self, node):
        var_name = node.left.value
        if self.symbol_table.lookup(var_name) is None:
            raise NameError(repr(var_name))
        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        if self.symbol_table.lookup(var_name) is None:
            raise NameError(repr(var_name))

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for decl_node in node.declarations:
            self.visit(decl_node)
        self.visit(node.compound_statement)

    def visit_ProcedureDecl(self, node):
        pass

    def visit_VarDecl(self, node):
        name = node.var_node.value
        type = self.symbol_table.lookup(node.type_node.value)
        if self.symbol_table.lookup(name) is not None:
            error(DUPLICATE_DECLARATION[lang])
        self.symbol_table.define(VarSymbol(name, type))

    def visit_Type(self, node):
        return None

    def visit_NoOp(self, node):
        return None


def error(e):
    raise Exception(e)


def main():
    while True:
        try:
            text = input('input>')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        symtab = SymbolTableBuilder()
        tree = parser.parse()
        symtab.visit(tree)
        print()
        print(symtab.symbol_table)
        print()
        interpreter.visit(tree)
        print('GLOBAL_SCOPE: ')
        for k, v in sorted(interpreter.GLOBAL_SCOPE.items()):
            print(f'{k} = {v}')
