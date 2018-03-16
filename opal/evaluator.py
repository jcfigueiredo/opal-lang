from lark import InlineTransformer
from lark.lexer import Token
from llvmlite import binding as llvm

from opal.ast import Program, Block, Add, Sub, Mul, Div, Integer, Float
from opal.codegen import LLVMCodeGenerator
from opal.parser import parser


# noinspection PyMethodMayBeStatic

# noinspection PyMethodMayBeStatic
class ASTVisitor(InlineTransformer):
    def program(self, body):
        if isinstance(body, Block):
            program = Program(body)
        else:
            program = Program(Block([body]))

        return program

    def block(self, *args):
        return Block([arg for arg in args if arg])

    # noinspection PyUnusedLocal
    def instruction(self, a, b=None):
        if isinstance(a, Token):
            return None
        return a

    def number(self, number):
        return number

    def add(self, lhs, rhs):
        return Add(lhs, rhs)

    def sub(self, lhs, rhs):
        return Sub(lhs, rhs)

    def mul(self, lhs, rhs):
        return Mul(lhs, rhs)

    def div(self, lhs, rhs):
        return Div(lhs, rhs)

    def int(self, const):
        return Integer(const.value)

    def float(self, const):
        return Float(const.value)

    def term(self, nl):
        # newlines hanler
        return None


class OpalEvaluator:

    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.codegen = LLVMCodeGenerator()

        self.target = llvm.Target.from_default_triple()

    def execute(self, code):
        ast = ASTVisitor().transform(parser.parse(f'{code}'))

        self.codegen.generate_code(ast)

        mod_ir = str(self.codegen.module)
        mod_ir = mod_ir.replace("unknown-unknown-unknown", "x86_64-apple-macosx10.12.0")

        return mod_ir
