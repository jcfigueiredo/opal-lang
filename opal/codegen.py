from collections import OrderedDict
from hashlib import sha3_256

# noinspection PyPackageRequirements
from llvmlite import ir as ir
from llvmlite.llvmpy.core import Constant, Module, Function, Builder

from opal import operations as ops
from opal.ast import ASTNode
from opal.ast.binop import BinaryOp
from opal.ast.core import ASTVisitor, get_param_type
from opal.ast.program import Program
from opal.ast.types import Int8, Any, Bool, Integer, List, Float, Klass
from opal.parser import parser
from resources.llvmex import CodegenError

INDICES = [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]

PRIVATE_LINKAGE = 'private'


class Printable(object):
    pass


class CodeGenerator(Printable):
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

        if self.is_break:
            return

        can_code_gen = hasattr(node, 'code')
        if can_code_gen:
            # noinspection PyUnresolvedReferences
            return node.code(codegen=self)

        method = 'visit_' + type(node).__name__.lower()

        return getattr(self, method, self.generic_codegen)(node)

    # TODO: refactor to create smaller, specific functions
    def generate_classes_metadata(self, klass: Klass):
        name = klass.name
        parent = klass.parent

        undefined_parent_class = name != 'Object' and parent not in [c.name for c in self.classes]

        if undefined_parent_class:
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

    def visit_vector(self, vector, index):
        val = self.call('vector_get', [vector, index])
        val = self.builder.ptrtoint(val, Integer.as_llvm())
        return val

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
