from collections import OrderedDict
from hashlib import sha3_256

# noinspection PyPackageRequirements
from llvmlite import ir as ir
from llvmlite.ir import PointerType
from llvmlite.llvmpy.core import Constant, Module, Function, Builder

from opal import operations as ops
from opal.ast import ASTNode, Value
from opal.ast.core import BinaryOp, Integer, Float, String, Print, Assign, Var, VarValue, List, \
    IndexOf, While, For, Klass, Funktion, Return, Call, ASTVisitor, MethodCall, get_param_type
from opal.ast.program import Program
from opal.parser import parser
from opal.ast.types import Int8, Any, Bool
from resources.llvmex import CodegenError

INDICES = [ir.Constant(Integer.as_llvm(), 0), ir.Constant(Integer.as_llvm(), 0)]

PRIVATE_LINKAGE = 'private'


class CodeGenerator:
    def __init__(self):
        # TODO: come up with a less naive way of handling the symtab and types
        self.classes = None
        self.symtab = {}
        self.typetab = {}
        self.is_break = False
        self.current_class = None

        self.loop_end_blocks = []
        self.loop_cond_blocks = []
        context = ir.Context()
        self.module = Module(name='opal-lang', context=context)
        self.blocks = []
        self.scope = {}

        self._add_builtins()

        func_ty = ir.FunctionType(ir.VoidType(), [])
        func = Function(self.module, func_ty, 'main')

        self.current_function = func
        entry_block = self.add_block('entry')
        exit_block = self.add_block('exit')

        self.function_stack = [func]
        self.builder = Builder(entry_block)
        self.exit_blocks = [exit_block]
        self.block_stack = [entry_block]

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

        vector_append_ty = ir.FunctionType(Any.as_llvm(), [List.as_llvm().as_pointer(), Int8.as_llvm().as_pointer()])
        ir.Function(self.module, vector_append_ty, 'vector_append')

        vector_get_ty = ir.FunctionType(Int8.as_llvm().as_pointer(), [List.as_llvm().as_pointer(), Integer.as_llvm()])
        ir.Function(self.module, vector_get_ty, 'vector_get')

        vector_size_ty = ir.FunctionType(Integer.as_llvm(), [List.as_llvm().as_pointer()])
        ir.Function(self.module, vector_size_ty, 'vector_size')

    def alloc(self, typ, name=''):
        return self.builder.alloca(typ, name=name)

    def alloc_and_store(self, val, typ, name=''):
        var_addr = self.alloc(typ, name)
        self.builder.store(val, var_addr)
        return var_addr

    def add_block(self, name):
        return self.current_function.append_basic_block(name)

    def assign(self, name, value, typ, is_class=False):
        if is_class:
            self.symtab[name] = value
            self.typetab[name] = typ
            return value

        old_val = self.symtab.get(name)
        if old_val:
            new_val = self.builder.store(value, old_val)
            self.symtab[name] = new_val.operands[1]
            return new_val

        var_address = self.alloc_and_store(value, typ, name=name)

        self.symtab[name] = var_address
        self.typetab[name] = typ
        return var_address

    def get_var(self, name):
        return self.symtab[name]

    def get_var_type(self, name):
        return self.typetab[name]

    # noinspection SpellCheckingInspection
    def bitcast(self, value, type_):
        return self.builder.bitcast(value, type_)

    def branch(self, block):
        return self.builder.branch(block)

    # noinspection SpellCheckingInspection
    def cbranch(self, cond, true_block, false_block):
        return self.builder.cbranch(cond, true_block, false_block)

    def gep(self, ptr, indices, inbounds=False, name=''):
        return self.builder.gep(ptr, indices, inbounds, name)

    def generate_code(self, code):
        visitor = ASTVisitor()
        ast = visitor.transform(parser.parse(f"{code}\n"))
        self.classes = visitor.classes

        for klass in self.classes:
            self.generate_classes_metadata(klass)

        assert isinstance(ast, Program)
        return ast.accept(self)

    def load(self, ptr, name=''):
        return self.builder.load(ptr, name)

    def position_at_end(self, block):
        return self.builder.position_at_end(block)

    def select(self, val, true, false):
        return self.builder.select(val, true, false)

    @staticmethod
    def insert_const_string(module, string):
        text = Constant.stringz(string)
        name = CodeGenerator.get_string_name(string)
        gv = module.globals.get(name)
        if gv is None:
            gv = module.add_global_variable(text.type, name=name)
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
        func = self.module.get_global(name)

        if func is None:
            raise TypeError('Calling non existing function')

        return self.builder.call(func, args)

    def const(self, val):
        # has to come first because freaking `isinstance(True, int) == True`
        if isinstance(val, bool):
            return ir.Constant(Bool.as_llvm(), val and 1 or 0)
        if isinstance(val, int):
            return ir.Constant(Integer.as_llvm(), val)
        if isinstance(val, float):
            return ir.Constant(Float.as_llvm(), val)

        raise NotImplementedError

    @staticmethod
    def generic_codegen(node):
        raise NotImplementedError('No visit_{} method'.format(type(node).__name__.lower()))

    def visit(self, node: ASTNode):
        """
        Dynamically invoke the code generator for each specific node
        :param node: ASTNode
        """

        can_code_gen = hasattr(node, 'code')
        if can_code_gen:
            # noinspection PyUnresolvedReferences
            return node.code(codegen=self)

        if self.is_break:
            return

        if isinstance(node, Integer) or isinstance(node, Float) or isinstance(node, Bool):
            return self.visit_value(node)

        method = 'visit_' + type(node).__name__.lower()

        if isinstance(node, BinaryOp):
            visit_specific_binop = getattr(self, method, None)
            if visit_specific_binop:
                return visit_specific_binop(node)
            return self.visit_binop(node)

        return getattr(self, method, self.generic_codegen)(node)

    def visit_string(self, node):
        return self.insert_const_string(self.module, node.val)

    # noinspection PyMethodMayBeStatic
    # TODO: review this to codegen instead of returning an ASTNode
    def visit_var(self, node):
        return Var(node.val)

    # noinspection SpellCheckingInspection
    def visit_varvalue(self, node):
        name = self.symtab[node.val]
        return self.load(name)

    # TODO: refactor to create smaller, specific functions
    def generate_classes_metadata(self, klass: Klass):
        name = klass.name
        parent = klass.parent

        if name != 'Object' and parent not in [c.name for c in self.classes]:
            raise CodegenError(f'Parent class {parent} not defined')
        vtable_typ_name = f"{name}_vtable_type"
        vtable_typ = self.module.context.get_identified_type(vtable_typ_name)
        type_ = self.module.context.get_identified_type(name)

        funk_types = OrderedDict()
        funktions = OrderedDict()

        object_type = self.module.context.get_identified_type('Object')

        for func in klass.functions:
            funk_name = f'{name}::{func.name}'

            signature = [get_param_type(param.type, object_type) for param in func.params]
            if func.ret_type:
                ret = get_param_type(func.ret_type, object_type)
            else:
                ret = ir.VoidType()

            func_ty = ir.FunctionType(ret, [type_.as_pointer()] + signature)
            funk_types[funk_name] = func_ty
            funk = Function(self.module, func_ty, funk_name)
            funktions[funk_name] = funk

        vtable_name = f"{name}_vtable"

        vtable_elements = [el.type for el in funktions.values()]

        vtable_type_name = f"{parent}_vtable_type"

        parent_type = \
            parent and self.module.context.get_identified_type(vtable_type_name) or vtable_typ

        vtable_elements.insert(0, parent_type.as_pointer())
        vtable_elements.insert(1, ir.IntType(8).as_pointer())
        vtable_typ.set_body(*vtable_elements)

        # --
        class_string = CodeGenerator.insert_const_string(self.module, name)
        if klass.parent:
            parent_table_typ = self.module.context.get_identified_type(f"{parent}_vtable_type")
            vtable_constant = ir.Constant(parent_table_typ.as_pointer(),
                                          self.module.get_global(f'{parent}_vtable').get_reference())
        else:
            vtable_constant = ir.Constant(vtable_typ.as_pointer(), None)

        fields = [
            vtable_constant,
            class_string.gep(INDICES)
        ]

        fields += [ir.Constant(item.type, item.get_reference()) for item in funktions.values()]

        vtable = self.module.add_global_variable(vtable_typ, name=vtable_name)
        vtable.linkage = PRIVATE_LINKAGE
        vtable.unnamed_addr = False
        vtable.global_constant = True
        vtable.initializer = vtable_typ(
            fields
        )

        type_ = self.module.context.get_identified_type(name)

        elements = []
        elements.insert(0, vtable_typ.as_pointer())
        type_.set_body(*elements)

    def visit_klass(self, node: Klass):
        self.current_class = node
        body = self.visit(node.body)

        self.current_class = None
        return body

    def get_function_names(self):
        return [f.name for f in self.module.functions]

    def visit_funktion(self, node: Funktion):
        klass = self.current_class

        method_name = f'{klass.name}::{node.name}'

        func = list(filter(lambda f: f.name == method_name, self.module.functions))[0]

        self.function_stack.append(func)

        old_func = self.current_function
        old_builder = self.builder
        self.current_function = func
        entry_block = self.add_block('entry')
        exit_block = self.add_block('exit')
        self.exit_blocks.append(exit_block)
        self.builder = Builder(entry_block)

        if node.is_constructor:
            this = self.gep(func.args[0], INDICES)
            self.builder.store(self.module.get_global(f'{klass.name}_vtable'), this)

        body = node.body
        if body:
            ret = self.visit(body)
        else:
            ret = None

        self.branch(exit_block)

        if not ret:
            self.position_at_end(exit_block)
            self.builder.ret_void()

        self.current_function = old_func
        self.builder = old_builder
        self.exit_blocks.pop()
        self.function_stack.pop()

        return func

    def visit_return(self, node: Return):
        previous_block = self.builder.block
        self.position_at_end(self.exit_blocks[-1])
        ret = self.builder.ret(self.visit(node.val))
        self.position_at_end(previous_block)
        return ret

    def visit_call(self, node: Call):
        func = node.func

        klass = self.get_klass_by_name(name=func)

        klass_name = klass.name
        klass_type = self.module.context.get_identified_type(klass_name)

        instance = self.alloc(klass_type, name=klass_name.lower())

        name = f'{func}::init'
        self.call(name, [instance])
        return instance

    def visit_methodcall(self, node: MethodCall):
        var = node.instance

        instance = self.get_var(var)
        typ = self.get_var_type(var)

        func = f'{typ.name}::{node.method}'

        return self.call(func, [instance])

    def visit_print(self, node: Print):
        val = self.visit(node.val)
        typ = None
        if isinstance(node.val, VarValue):
            typ = self.typetab[node.val.val]

        if isinstance(node.val, String) or isinstance(typ, PointerType):
            typ = String
        elif isinstance(node.val, Integer) or val.type is Integer.as_llvm():
            typ = Integer
        elif isinstance(node.val, Float) or val.type is Float.as_llvm():
            typ = Float
        elif isinstance(node.val, Bool) or val.type is Bool.as_llvm():
            typ = Bool

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

            buffer_ptr = self.gep(buffer, INDICES, inbounds=True)

            self.call('int_to_string', [number_ptr, buffer_ptr, (self.const(10))])

            self.call('puts', [buffer_ptr])
            return

        if typ is Float:
            percent_g = self.visit_string(String('%g\n'))
            percent_g = self.gep(percent_g, INDICES)

            value = percent_g
            type_ = Int8.as_llvm().as_pointer()
            percent_g = self.bitcast(value, type_)
            self.call('printf', [percent_g, val])
            return

        if typ is Bool:
            mod = self.module
            true = self.insert_const_string(mod, 'true')
            true = self.gep(true, INDICES)
            false = self.insert_const_string(mod, 'false')
            false = self.gep(false, INDICES)

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

    def visit_while(self, node: While):

        cond_block = self.add_block('while.cond')
        body_block = self.add_block('while.body')

        self.loop_cond_blocks.append(cond_block)
        end_block = self.add_block('while.end')
        self.loop_end_blocks.append(end_block)

        self.branch(cond_block)
        self.position_at_end(cond_block)

        cond = self.visit(node.cond)
        self.cbranch(cond, body_block, end_block)
        self.position_at_end(body_block)

        self.visit(node.body)

        if not self.is_break:
            self.branch(cond_block)
        else:
            self.is_break = False

        self.position_at_end(end_block)
        self.loop_end_blocks.pop()
        self.loop_cond_blocks.pop()

    def visit_for(self, node: For):
        init_block = self.add_block('for.init')
        cond_block = self.add_block('for.cond')
        self.loop_cond_blocks.append(cond_block)

        body_block = self.add_block('for.body')
        end_block = self.add_block('for.end')
        self.loop_end_blocks.append(end_block)

        self.branch(init_block)
        self.position_at_end(init_block)
        vector = self.visit(node.iterable)

        size = self.call('vector_size', [vector])

        size = self.alloc_and_store(size, Integer.as_llvm(), name='size')
        index = self.alloc_and_store(self.const(0), Integer.as_llvm(), 'index')

        self.branch(cond_block)
        self.position_at_end(cond_block)

        should_go_on = self.builder.icmp_signed('<', self.load(index), self.load(size))

        self.cbranch(should_go_on, body_block, end_block)

        self.position_at_end(body_block)

        pos = self.load(index)

        val = self.visit_vector(vector, pos)

        self.assign(node.var.val, val, Integer.as_llvm())

        self.visit(node.body)

        if not self.is_break:
            self.builder.store(self.builder.add(self.const(1), pos), index)
            self.branch(cond_block)
        else:
            self.is_break = False

        self.position_at_end(end_block)
        self.loop_end_blocks.pop()
        self.loop_cond_blocks.pop()

    def visit_break(self, _):
        self.is_break = True
        return self.branch(self.loop_end_blocks[-1])

    def visit_assign(self, node: Assign):
        left = self.visit(node.lhs)
        rhs = node.rhs
        value = self.visit(rhs)

        name = left.val

        if isinstance(rhs, String):
            typ = value.type
        elif isinstance(rhs, List):
            typ = List.as_llvm().as_pointer()
        elif isinstance(rhs, Call):
            typ = self.get_klass_by_name(rhs.func)
            return self.assign(name, value, typ, is_class=True)
        elif not isinstance(rhs, Value):
            value = self.visit(rhs)
            typ = value.type
        else:
            typ = rhs.as_llvm()

        var_address = self.assign(name, value, typ)
        return var_address

    def visit_list(self, node: List):
        vector = self.alloc(List.as_llvm())
        self.call('vector_init', [vector])
        for item in node.items:
            val = self.visit(item)
            self.call('vector_append', [vector, self.builder.inttoptr(val, Int8.as_llvm().as_pointer())])
        return vector

    def visit_indexof(self, node: IndexOf):
        index = self.visit(node.index)
        vector = self.visit(node.lst)
        val = self.visit_vector(vector, index)
        return val

    def visit_vector(self, vector, index):
        val = self.call('vector_get', [vector, index])
        val = self.builder.ptrtoint(val, Integer.as_llvm())
        return val

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
    def visit_value(self, node):
        return self.const(node.val)

    def cast(self, from_, to):
        if from_.type == Integer.as_llvm() and to is Bool:
            result = self.alloc_and_store(from_, Integer.as_llvm())
            result = self.load(result)
            return self.builder.icmp_signed('!=', result, self.const(0))
        if from_.type == Float.as_llvm() and to is Bool:
            result = self.alloc_and_store(from_, Float.as_llvm())
            result = self.load(result)
            return self.builder.fcmp_ordered('!=', result, self.const(0.0))

        raise NotImplementedError('Unsupported cast')

    def get_klass_by_name(self, name):
        for klass in self.classes:
            if klass.name == name:
                return klass
