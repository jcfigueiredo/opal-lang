from lark import InlineTransformer
from lark.lexer import Token
from llvmlite import binding as llvm
from llvmlite import ir as ir
from llvmlite.llvmpy.core import Constant, LINKAGE_INTERNAL, Module, Function, Builder

from opal import operations
from opal.ast import Program, BinaryOp, Integer, Block, Add, Sub, Mul, Div, Float, String, Print
from opal.types import Int8, Any

PRIVATE_LINKAGE = 'private'


class CodeGenerator:
    def __init__(self):
        self.module = Module(name='opal-lang')
        self.blocks = []

        self._add_builtins()

        func_ty = ir.FunctionType(ir.VoidType(), [])
        func = Function(self.module, func_ty, 'main')
        entry_block = func.append_basic_block('entry')
        exit_block = func.append_basic_block('exit')

        self.current_function = func
        self.function_stack = [func]
        self.builder = Builder(entry_block)
        self.exit_blocks = [exit_block]
        self.block_stack = [entry_block]

        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

    def __str__(self):
        return str(self.module)

    def _add_builtins(self):
        malloc_ty = ir.FunctionType(Int8.as_llvm.as_pointer(), [Integer.as_llvm])
        ir.Function(self.module, malloc_ty, 'malloc')

        free_ty = ir.FunctionType(Any.as_llvm, [Int8.as_llvm.as_pointer()])
        ir.Function(self.module, free_ty, 'free')

        puts_ty = ir.FunctionType(Integer.as_llvm, [Int8.as_llvm.as_pointer()])
        ir.Function(self.module, puts_ty, 'puts')

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

        if isinstance(node, Integer) or isinstance(node, Float):
            return self._codegen_value(node)

        if isinstance(node, BinaryOp):
            return self._codegen_binop(node)

        method = '_codegen_' + type(node).__name__.lower()

        return getattr(self, method, self.generic_codegen)(node)

    def insert_const_string(self, string):
        text = Constant.stringz(string)
        name = self.get_string_name(string)
        # Try to reuse existing global
        gv = self.module.globals.get(name)
        if gv is None:
            # Not defined yet
            gv = self.builder.module.add_global_variable(text.type, name=name)
            gv.linkage = PRIVATE_LINKAGE
            gv.unnamed_addr = True
            gv.global_constant = True
            gv.initializer = text

        return gv

    @staticmethod
    def get_string_name(string):
        return '_'.join(['str', str(id(string))])

    def _codegen_string(self, node):
        return self.insert_const_string(node.val)

    def _codegen_print(self, node):
        if isinstance(node.val, String):

            stringz = self.insert_const_string(node.val.val)
            # Cast to a i8* pointer
            char_ty = stringz.type.pointee.element
            str_ptr = self.builder.bitcast(stringz, char_ty.as_pointer())

            self.call('puts', [str_ptr])
            return

        raise NotImplementedError(f'can\'t print {node.val}')

    def call(self, name, args):
        if isinstance(name, str):
            func = self.module.get_global(name)
        else:
            func = self.module.get_global(name.name)
        if func is None:
            raise TypeError('Calling non existant function')
        return self.builder.call(func, args)

    # def alloc_and_store(self, val, typ, name=''):
    #     var_addr = self.builder.alloca(typ, name=name)
    #     self.builder.store(val, var_addr)
    #     return var_addr

    def gep(self, ptr, indices, inbounds=False, name=''):
        return self.builder.gep(ptr, indices, inbounds, name)

    def const(self, val):
        if isinstance(val, int):
            return ir.Constant(Integer.as_llvm, val)
        raise NotImplementedError

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

    def print(self, expr):
        return Print(expr)

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
