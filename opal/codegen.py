from hashlib import sha3_256

# noinspection PyPackageRequirements
from llvmlite import binding as llvm
from llvmlite import ir as ir
from llvmlite.llvmpy.core import Constant, Module, Function, Builder

from opal import operations as ops
from opal.ast import Program, BinaryOp, Integer, Float, String, Print, Boolean, Assign, Var, VarValue, List, IndexOf, \
    While, If
from opal.types import Int8, Any

PRIVATE_LINKAGE = 'private'


class CodeGenerator:
    def __init__(self):
        # TODO: come up with a less naive way of handling the symtab and types
        self.symtab = {}
        self.typetab = {}

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

        vector_init_ty = ir.FunctionType(Any.as_llvm(), [List.as_llvm().as_pointer()])
        ir.Function(self.module, vector_init_ty, 'vector_init')

        vector_append_ty = ir.FunctionType(Any.as_llvm(), [List.as_llvm().as_pointer(), Integer.as_llvm()])
        ir.Function(self.module, vector_append_ty, 'vector_append')

        vector_get_ty = ir.FunctionType(Integer.as_llvm(), [List.as_llvm().as_pointer(), Integer.as_llvm()])
        ir.Function(self.module, vector_get_ty, 'vector_get')

    def alloc(self, typ, name=''):
        return self.builder.alloca(typ, name=name)

    def alloc_and_store(self, val, typ, name=''):
        var_addr = self.alloc(typ, name)
        self.builder.store(val, var_addr)
        return var_addr

    def add_block(self, name):
        return self.current_function.append_basic_block(name)

    def bitcast(self, value, type_):
        return self.builder.bitcast(value, type_)

    def branch(self, block):
        self.builder.branch(block)

    # noinspection SpellCheckingInspection
    def cbranch(self, cond, true_block, false_block):
        self.builder.cbranch(cond, true_block, false_block)

    def gep(self, ptr, indices, inbounds=False, name=''):
        return self.builder.gep(ptr, indices, inbounds, name)

    def generate_code(self, node):
        assert isinstance(node, Program)
        return self.visit(node)

    def load(self, name):
        return self.builder.load(name)

    def position_at_end(self, block):
        self.builder.position_at_end(block)

    def select(self, val, true, false):
        return self.builder.select(val, true, false)

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

    @staticmethod
    def generic_codegen(node):
        raise NotImplementedError('No visit_{} method'.format(type(node).__name__.lower()))

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

    def visit_string(self, node):
        return self.insert_const_string(node.val)

    # TODO: review this to codegen instead of returning an ASTNode
    # noinspection PyMethodMayBeStatic
    def visit_var(self, node):
        return Var(node.val)

    # noinspection SpellCheckingInspection
    def visit_varvalue(self, node):
        name = self.symtab[node.val]
        return self.load(name)

    def visit_print(self, node: Print):
        val = self.visit(node.val)
        typ = None

        if isinstance(node.val, VarValue):
            typ = self.typetab[node.val.val]

        if isinstance(node.val, String):
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
            str_ptr = self.bitcast(val, char_ty.as_pointer())

            self.call('puts', [str_ptr])
            return

        if typ is Integer:
            number = self.alloc_and_store(val, val.type)
            number_ptr = self.load(number)

            buffer = self.alloc(ir.ArrayType(Int8.as_llvm(), 10))

            buffer_ptr = self.gep(buffer, [self.const(0), self.const(0)], inbounds=True)

            self.call('int_to_string', [number_ptr, buffer_ptr, (self.const(10))])

            self.call('puts', [buffer_ptr])
            return

        if typ is Float:
            percent_g = self.visit_string(String('%g\n'))
            percent_g = self.gep(percent_g, [self.const(0), self.const(0)])

            value = percent_g
            type_ = Int8.as_llvm().as_pointer()
            percent_g = self.bitcast(value, type_)
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
                val = self.select(val, true, false)

            self.call('printf', [val])

            return

        raise NotImplementedError(f'can\'t print {node.val}')

    def visit_if(self, node: If):
        start_block = self.add_block('if.start')
        end_block = self.add_block('if.end')
        self.branch(start_block)
        self.position_at_end(start_block)

        if_true_block = self.add_block('if.true')

        if isinstance(node.cond, VarValue):
            cond = self.visit(node.cond)
        else:
            cond = self.visit(node.cond)

        if cond.type != Boolean.as_llvm():
            cond = self.cast(cond, Boolean)

        if_false_block = end_block

        if node.else_:
            if_false_block = self.add_block('if.false')

        self.cbranch(cond, if_true_block, if_false_block)

        self.position_at_end(if_true_block)
        self.visit(node.then_)
        self.branch(end_block)

        if node.else_:
            self.position_at_end(if_false_block)
            self.visit(node.else_)
            self.branch(end_block)

        self.position_at_end(end_block)

    def visit_while(self, node: While):

        cond_block = self.add_block('while.cond')
        body_block = self.add_block('while.body')
        end_block = self.add_block('while.end')

        self.branch(cond_block)
        self.position_at_end(cond_block)
        cond = self.visit(node.cond)
        self.cbranch(cond, body_block, end_block)
        self.position_at_end(body_block)
        self.visit(node.body)
        self.branch(cond_block)

        self.position_at_end(end_block)

    def visit_assign(self, node: Assign):
        left = self.visit(node.lhs)
        right = self.visit(node.rhs)

        name = left.val

        old_val = self.symtab.get(name)
        if old_val:
            new_val = self.builder.store(right, old_val)
            self.symtab[name] = new_val.operands[1]

            return new_val

        if isinstance(node.rhs, String):
            var_address = self.alloc_and_store(right, right.type, name=name)
        elif isinstance(node.rhs, List):
            var_address = self.alloc_and_store(right, List.as_llvm().as_pointer())
        else:
            var_address = self.alloc_and_store(right, node.rhs.as_llvm(), name=name)

        self.symtab[name] = var_address
        self.typetab[name] = node.rhs.__class__

        return var_address

    def visit_list(self, node: List):
        vector = self.alloc(List.as_llvm())
        self.call('vector_init', [vector])
        for item in node.items:
            val = self.visit(item)
            self.call('vector_append', [vector, val])
        return vector

    def visit_indexof(self, node: IndexOf):
        index = self.visit(node.index)
        vector = self.visit(node.lst)
        return self.call('vector_get', [vector, index])

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

    def cast(self, from_, to):
        if from_.type == Integer.as_llvm() and to is Boolean:
            result = self.alloc_and_store(from_, Integer.as_llvm())
            result = self.load(result)
            return self.builder.icmp_signed('!=', result, self.const(0))
        if from_.type == Float.as_llvm() and to is Boolean:
            result = self.alloc_and_store(from_, Float.as_llvm())
            result = self.load(result)
            return self.builder.fcmp_ordered('!=', result, self.const(0.0))

        raise NotImplementedError('Unsupported cast')
