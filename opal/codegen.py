from lark import InlineTransformer
from lark.lexer import Token
from llvmlite import binding as llvm
from llvmlite import ir as ir

from opal import operations
from opal.ast import Program, Value, BinaryOp, Integer, Block, Add, Sub, Mul, Div, Float, String


class CodeGenerator:
    def __init__(self):
        self.module = ir.Module()
        self.blocks = []

        func_ty = ir.FunctionType(ir.VoidType(), [])
        func = ir.Function(self.module, func_ty, 'main')
        entry_block = func.append_basic_block('entry')
        exit_block = func.append_basic_block('exit')

        self.current_function = func
        self.function_stack = [func]
        self.builder = ir.IRBuilder(entry_block)
        self.exit_blocks = [exit_block]
        self.block_stack = [entry_block]

        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

    def generate_code(self, node):
        assert isinstance(node, Program)
        return self._codegen(node)

    @staticmethod
    def generic_codegen(node):
        raise Exception('No _codegen_{} method'.format(type(node).__name__.lower()))

    def branch(self, block):
        self.builder.branch(block)

    def position_at_end(self, block):
        self.builder.position_at_end(block)

    def _codegen(self, node):
        """
        Dynamically invoke the code generator for each specific node
        :param node: ASTNode
        """

        if isinstance(node, Value):
            return self._codegen_value(node)

        if isinstance(node, BinaryOp):
            return self._codegen_binop(node)

        method = '_codegen_' + type(node).__name__.lower()

        return getattr(self, method, self.generic_codegen)(node)

    def _codegen_binop(self, node):
        left = self._codegen(node.lhs)
        right = self._codegen(node.rhs)

        ops = {'+': 'addtmp', '-': 'subtmp', '*': 'multmp', '/': 'sdivtmp', }

        op = node.op
        if op not in ops:
            raise NotImplementedError(f'The operation _{op}_ is nor support for Binary Operations.')

        if left.type == Integer.as_llvm and right.type == Integer.as_llvm:
            return operations.int_ops(self.builder, left, right, node)

        return operations.float_ops(self.builder, left, right, node)

    # noinspection PyMethodMayBeStatic
    def _codegen_block(self, node):
        ret = None
        for stmt in node.statements:
            temp = self._codegen(stmt)
            if temp:
                ret = temp
        return ret

    # noinspection PyPep8Naming
    def _codegen_program(self, node):
        self._codegen(node.block)
        self.branch(self.exit_blocks[0])
        self.position_at_end(self.exit_blocks[0])
        self.builder.ret_void()

    # noinspection PyMethodMayBeStatic
    def _codegen_value(self, node):
        return ir.Constant(node.__class__.as_llvm, node.val)


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
