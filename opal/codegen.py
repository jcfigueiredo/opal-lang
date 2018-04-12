from hashlib import sha3_256

from lark import InlineTransformer
from lark.lexer import Token
from llvmlite import binding as llvm
from llvmlite import ir as ir
from llvmlite.llvmpy.core import Constant, Module, Function, Builder

from opal import operations as ops
from opal.ast import Program, BinaryOp, Integer, Block, Add, Sub, Mul, Div, Float, String, Print, Boolean, GreaterThan, \
    LessThan, Equals, Unequals, Comparison, Assign, Var, If

from opal.types import Int8, Any

PRIVATE_LINKAGE = 'private'


class CodeGenerator:
    def __init__(self):
        self.symtab = {}

        self.module = Module(name='opal-lang')
        self.blocks = []

        self._add_builtins()
        # self._add_externals()

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
        malloc_ty = ir.FunctionType(Int8.as_llvm().as_pointer(), [Integer.as_llvm()])
        ir.Function(self.module, malloc_ty, 'malloc')

        free_ty = ir.FunctionType(Any.as_llvm(), [Int8.as_llvm().as_pointer()])
        ir.Function(self.module, free_ty, 'free')

        puts_ty = ir.FunctionType(Integer.as_llvm(), [Int8.as_llvm().as_pointer()])
        ir.Function(self.module, puts_ty, 'puts')

        int_to_string_ty = ir.FunctionType(Int8.as_llvm().as_pointer(), [Integer.as_llvm(), Int8.as_llvm().as_pointer(),
                                                                         Integer.as_llvm()])
        ir.Function(self.module, int_to_string_ty, 'int_to_string')

        printf_ty = ir.FunctionType(Integer.as_llvm(), [Int8.as_llvm().as_pointer()],
                                    var_arg=True)
        ir.Function(self.module, printf_ty, 'printf')

    def generate_code(self, node):
        assert isinstance(node, Program)
        return self.visit(node)

    def alloc_and_store(self, val, typ, name=''):
        var_addr = self.builder.alloca(typ, name=name)
        self.builder.store(val, var_addr)
        return var_addr

    def load(self, name):
        return self.builder.load(name)

    def gep(self, ptr, indices, inbounds=False, name=''):
        return self.builder.gep(ptr, indices, inbounds, name)

    @staticmethod
    def generic_codegen(node):
        raise Exception('No visit_{} method'.format(type(node).__name__.lower()))

    def branch(self, block):
        self.builder.branch(block)

    def position_at_end(self, block):
        self.builder.position_at_end(block)

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

    def visit(self, node):
        """
        Dynamically invoke the code generator for each specific node
        :param node: ASTNode
        """

        if isinstance(node, Integer) or isinstance(node, Float) or isinstance(node, Boolean):
            return self.visit_value(node)

        method = 'visit_' + type(node).__name__.lower()

        if isinstance(node, BinaryOp):
            visit_specific_binop = getattr(self, method, None)
            if visit_specific_binop:
                return visit_specific_binop(node)
            return self.visit_binop(node)

        return getattr(self, method, self.generic_codegen)(node)

    @staticmethod
    def get_string_name(string):
        m = sha3_256()
        m.update(string.encode('utf-8'))

        return '_'.join(['str', str(m.hexdigest())])

    def call(self, name, args):
        if isinstance(name, str):
            func = self.module.get_global(name)
        else:
            func = self.module.get_global(name.name)
        if func is None:
            raise TypeError('Calling non existing function')
        return self.builder.call(func, args)

    def const(self, val):
        # has to come first because freaking `isinstance(True, int) == True`
        if isinstance(val, bool):
            return ir.Constant(Boolean.as_llvm(), val and 1 or 0)
        if isinstance(val, int):
            return ir.Constant(Integer.as_llvm(), val)
        if isinstance(val, float):
            return ir.Constant(Float.as_llvm(), val)

        raise NotImplementedError

    def visit_string(self, node):
        return self.insert_const_string(node.val)

    def visit_print(self, node):
        val = self.visit(node.val)

        typ = None

        if isinstance(val, Var):
            typ, name = self.symtab[val.val]
            val = self.load(name)
        elif isinstance(node.val, String):
            typ = String
        elif isinstance(node.val, Integer) or val.type is Integer.as_llvm():
            typ = Integer
        elif isinstance(node.val, Float) or val.type is Float.as_llvm():
            typ = Float
        elif isinstance(node.val, Boolean) or val.type is Boolean.as_llvm():
            typ = Boolean

        if typ is String:
            # Cast to a i8* pointer
            char_ty = val.type.pointee.element
            str_ptr = self.builder.bitcast(val, char_ty.as_pointer())

            self.call('puts', [str_ptr])
            return

        if typ is Integer:
            number = self.alloc_and_store(val, val.type)
            number_ptr = self.load(number)

            buffer = self.builder.alloca(ir.ArrayType(Int8.as_llvm(), 10))

            buffer_ptr = self.gep(buffer, [self.const(0), self.const(0)], inbounds=True)

            self.call('int_to_string', [number_ptr, buffer_ptr, (self.const(10))])

            self.call('puts', [buffer_ptr])
            return

        if typ is Float:
            percent_g = self.visit_string(String('%g\n'))
            percent_g = self.gep(percent_g, [self.const(0), self.const(0)])
            percent_g = self.builder.bitcast(percent_g, Int8.as_llvm().as_pointer())
            self.call('printf', [percent_g, val])
            return

        if typ is Boolean:
            true = self.insert_const_string('true')
            true = self.gep(true, [self.const(0), self.const(0)])
            false = self.insert_const_string('false')
            false = self.gep(false, [self.const(0), self.const(0)])

            if hasattr(val, 'constant'):
                if val.constant:
                    val = true
                else:
                    val = false
            else:
                val = self.builder.select(val, true, false)

            self.call('printf', [val])

            return

        raise NotImplementedError(f'can\'t print {node.val}')

    # noinspection PyMethodMayBeStatic
    def visit_var(self, node):
        return Var(node.val)

    def visit_assign(self, node):
        left = self.visit(node.lhs)
        right = self.visit(node.rhs)

        name = left.val

        if isinstance(node.rhs, String):
            var_address = self.alloc_and_store(right, right.type, name=name)
        else:
            var_address = self.alloc_and_store(right, node.rhs.as_llvm(), name=name)

        self.symtab[name] = (node.rhs.__class__, var_address)

        return var_address

    def visit_binop(self, node):

        left = self.visit(node.lhs)
        right = self.visit(node.rhs)

        op = node.op

        if isinstance(node, BinaryOp):
            if left.type == Integer.as_llvm() and right.type == Integer.as_llvm():
                return ops.int_ops(self.builder, left, right, node)
            return ops.float_ops(self.builder, left, right, node)

        raise NotImplementedError(f'The operation _{op}_ is nor support for Binary Operations.')

    # noinspection PyMethodMayBeStatic
    def visit_block(self, node):
        ret = None
        for stmt in node.statements:
            temp = self.visit(stmt)
            if temp:
                ret = temp
        return ret

    # noinspection PyPep8Naming
    def visit_program(self, node):
        self.visit(node.block)
        self.branch(self.exit_blocks[0])
        self.position_at_end(self.exit_blocks[0])
        self.builder.ret_void()

    # noinspection PyMethodMayBeStatic
    def visit_value(self, node):
        return self.const(node.val)


# noinspection PyMethodMayBeStatic
class ASTVisitor(InlineTransformer):
    def program(self, body):
        if isinstance(body, Block):
            program = Program(body)
        else:
            program = Program(Block([body]))

        return program

    def block(self, *args):
        statements_excluding_token = [arg for arg in args if arg and not isinstance(arg, Token)]
        return Block(statements_excluding_token)

    def assign(self, lhs, rhs):
        # if isinstance(rhs, Token):
        #     rhs = Var(rhs.value)
        return Assign(lhs, rhs)

    def name(self, id_):
        return Var(id_.value)

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

    def boolean(self, const):
        return Boolean(const.value == 'true')

    def if_(self, cond, then_, else_=None):
        return If(cond, then_, else_)

    def comp(self, lhs, op, rhs):
        node = Comparison.by(op.value)
        if not node:
            raise SyntaxError(f'The operation [{op}] is not supported.')
        return node(lhs, rhs)
