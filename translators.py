from LPI import Lexer, Parser, NodeVisitor


##################
# RPN Translator #
##################


class RPNTranslator(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        right_value = self.visit(node.right)
        left_value = self.visit(node.left)

        return f'{left_value} {right_value} {node.op.value}'

    def visit_Num(self, node):
        return node.value

    def translate(self):
        tree = self.parser.parse()
        return self.visit(tree)


def translate_to_RPN(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    rpn = RPNTranslator(parser)
    return rpn.translate()

###################
# LISP Translator #
###################


class LISPTranslator(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)

        return f'({node.op.value} {left_value} {right_value})'

    def visit_Num(self, node):
        return node.value

    def translate(self):
        tree = self.parser.parse()
        return self.visit(tree)


def translate_to_LISP(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    lisp = LISPTranslator(parser)
    return lisp.translate()


def main():
    while True:
        try:
            text = input('translate> ')
        except EOFError:
            break
        if not text:
            continue

        print('RPN: ' + translate_to_RPN(text))
        print('LISP: ' + translate_to_LISP(text))
