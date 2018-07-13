from typing import Iterable

import llvmlite.ir as ir
from llvmlite.llvmpy.core import Builder

from opal.ast import Value, ASTNode
from opal.ast.program import Block
from opal.ast.terminals import Return

INDICES = [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]


class Any:
    _llvm_type = ir.VoidType()

    @classmethod
    def as_llvm(cls):
        return cls._llvm_type


# noinspection PyMethodMayBeStatic
class Integer(Any, Value):
    _llvm_type = ir.IntType(32)

    def __init__(self, val):
        self.val = int(val)

    def code(self, codegen):
        return codegen.const(self.val)


class Int8(Any, Value):
    _llvm_type = ir.IntType(8)

    def __init__(self, val):
        self.val = int(val)


class Bool(Any, Value):
    _llvm_type = ir.IntType(1)

    def __init__(self, val):
        self.val = bool(val)

    def dump(self):
        return f'({self.__class__.__name__} {str(self.val).lower()})'

    def code(self, codegen):
        return codegen.const(self.val)


# TODO: make it decimal? https://docs.python.org/3/library/decimal.html
class Float(Any, Value):
    _llvm_type = ir.DoubleType()

    def __init__(self, val):
        self.val = float(val)

    def code(self, codegen):
        return codegen.const(self.val)


class List(Any, ASTNode):
    _llvm_type = ir.LiteralStructType([Integer.as_llvm(), Integer.as_llvm(), Int8.as_llvm().as_pointer().as_pointer()])

    def __init__(self, items: Iterable[Value]):
        self._items = items

    @property
    def items(self):
        return self._items

    def dump(self):
        return "[{0}]".format(', '.join([item.dump() for item in self._items]))

    def code(self, codegen):
        vector = codegen.alloc(List.as_llvm())
        codegen.call('vector_init', [vector])
        for item in self.items:
            val = codegen.visit(item)
            codegen.call('vector_append', [vector, codegen.builder.inttoptr(val, Int8.as_llvm().as_pointer())])
        return vector


# type_map = {
# 	ANY: ir.VoidType(),
# 	BOOL: ir.IntType(1),
# 	INT: ir.IntType(64),
# 	INT8: ir.IntType(8),
# 	INT32: ir.IntType(32),
# 	INT64: ir.IntType(64),
# 	INT128: ir.IntType(128),
# 	DEC: ir.DoubleType(),
# 	FLOAT: ir.FloatType(),
# 	FUNC: ir.FunctionType,
# 	VOID: ir.VoidType(),
# 	STR: ir.IntType(8).as_pointer,
# }


class String(Any, Value):
    _llvm_type = ir.IntType(8).as_pointer

    def __init__(self, val):
        self.val = val

    def code(self, codegen):
        return codegen.insert_const_string(codegen.module, self.val)


class Funktion(ASTNode):
    def __init__(self, name, params, body, ret_type=None, is_constructor=False):
        self.name = name
        self.params = params
        self.body = body
        self.ret_type = ret_type
        self.is_constructor = is_constructor

    def dump(self):
        args = ','.join([arg.dump() for arg in self.params])
        ret_type = self.ret_type and f'{self.ret_type} ' or ''
        # ret_type = self.ret_type and self.ret_type.val.__class__.__name__
        # ret_type = ret_type and f'{ret_type} ' or ''
        name = '{0}{1}'.format(self.is_constructor and ':' or '', self.name)
        return f'({ret_type}{name}({args}) {self.body.dump()})'

    def code(self, codegen):
        klass = codegen.current_class

        method_name = f'{klass.name}::{self.name}'

        func = list(filter(lambda f: f.name == method_name, codegen.module.functions))[0]

        codegen.function_stack.append(func)

        old_func = codegen.current_function
        old_builder = codegen.builder
        codegen.current_function = func
        entry_block = codegen.add_block('entry')
        exit_block = codegen.add_block('exit')
        codegen.exit_blocks.append(exit_block)
        codegen.builder = Builder(entry_block)

        if self.is_constructor:
            this = codegen.gep(func.args[0], INDICES)
            codegen.builder.store(codegen.module.get_global(f'{klass.name}_vtable'), this)

        body = self.body
        if body:
            ret = codegen.visit(body)
        else:
            ret = None

        codegen.branch(exit_block)

        if not ret:
            codegen.position_at_end(exit_block)
            codegen.builder.ret_void()

        codegen.current_function = old_func
        codegen.builder = old_builder
        codegen.exit_blocks.pop()
        codegen.function_stack.pop()

        return func


class Klass(ASTNode):
    def __init__(self, name, body: Block, parent=None):
        self.name = name
        self.body = body
        self.parent = parent
        if name != 'Object' and not parent:
            self.parent = 'Object'
        self.functions = []

    def dump(self):
        return f'(class {self.name}{self.body.dump()})'

    def add_function(self, funktion: Funktion):
        self.functions.append(funktion)

    def code(self, codegen):
        codegen.current_class = self
        body = codegen.visit(self.body)

        codegen.current_class = None
        return body


class Param(ASTNode):
    def __init__(self, name, type_):
        self._name = name
        self._type = type_

    def dump(self):
        type_ = self.type and f'::{self.type}' or ''
        return f'{self.name}{type_}'

    @property
    def name(self):
        return self._name.val

    @property
    def type(self):
        return self._type


class Call(ASTNode):
    def __init__(self, func, args):
        self.func = func

        if args is None:
            args = []

        self.args = args

    def dump(self):
        args = ', '.join([arg.dump() for arg in self.args])
        return f'{self.func}({args})'

    def code(self, codegen):
        func = self.func

        klass = codegen.get_klass_by_name(name=func)

        klass_name = klass.name
        klass_type = codegen.module.context.get_identified_type(klass_name)

        instance = codegen.alloc(klass_type, name=klass_name.lower())

        name = f'{func}::init'
        codegen.call(name, [instance])
        return instance


class MethodCall(ASTNode):
    def __init__(self, instance, method, args):
        self.instance = instance
        self.method = method

        if args is None:
            args = []

        self.args = args

    def dump(self):
        args = ', '.join([arg.dump() for arg in self.args])
        return f'({self.instance}.{self.method} {args})'

    def code(self, codegen):
        var = self.instance

        instance = codegen.get_var(var)
        typ = codegen.get_var_type(var)

        func = f'{typ.name}::{self.method}'

        return codegen.call(func, [instance])


type_map = {
    'Cint32': Integer.as_llvm(),
    Integer: Integer.as_llvm(),
}


def get_param_type(typ, default=None):
    if isinstance(typ, Return):
        typ = typ.val.__class__
    if typ in type_map:
        return type_map[typ]

    return default