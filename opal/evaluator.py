# noinspection PyPackageRequirements
from ctypes import CFUNCTYPE, c_void_p

from lark import InlineTransformer
# noinspection PyPackageRequirements
from lark.lexer import Token
from llvmlite import binding as llvm

from opal.ast import Program, Block, Add, Sub, Mul, Div, Integer, Float, String
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

    def string(self, const):
        return String(const.value[1:][:-1])

    def term(self, nl):
        # newlines handler
        return None


class OpalEvaluator:

    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.codegen = LLVMCodeGenerator()

        # self.target = llvm.Target.from_triple("x86_64-apple-macosx10.12.0")

    def evaluate(self, code, print_ir=False):
        ast = ASTVisitor().transform(parser.parse(f'{code}'))

        self.codegen.generate_code(ast)

        module = self.codegen.module

        llvm_ir = str(module)

        llvm_mod = llvm.parse_assembly(llvm_ir)

        if print_ir:
            print(llvm_ir)

        llvm_mod.verify()

        target_machine = llvm.Target.from_default_triple().create_target_machine()
        with llvm.create_mcjit_compiler(llvm_mod, target_machine) as ee:
            ee.finalize_object()
            fptr = CFUNCTYPE(c_void_p)(ee.get_function_address('main'))

            fptr()

