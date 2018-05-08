from __future__ import print_function, absolute_import

from contextlib import contextmanager

from llvmlite import binding as llvm
from llvmlite import ir
from llvmlite.ir import Function
from llvmlite.llvmpy.core import Builder
from llvmlite.tests.test_binding import BaseTest

from opal.ast import Integer


class Class:
    def __init__(self, module, name, elements):
        self._module = module
        self._name = name
        self._elements = elements
        self._typ = None
        self.functions = {}

    def _pointer(self):
        return self._typ.as_pointer()

    def create(self):
        self._typ = self._module.context.get_identified_type(self._name)
        self._typ.set_body(*self._elements)
        return self._typ

    def add_function(self, name, signature=None, ret=None):
        if not signature:
            signature = []
        if not ret:
            ret = ir.VoidType()

        func_ty = ir.FunctionType(ret, [self._pointer()] + signature)
        func = Function(self._module, func_ty, name)
        self.functions[name] = func
        return func

    @property
    def type(self):
        return self._typ


class TestTypeParsing(BaseTest):
    @contextmanager
    def check_parsing(self):
        mod = ir.Module()
        # Yield to caller and provide the module for adding
        # new GV.
        yield mod
        # Caller yield back and continue with testing
        asm = str(mod)
        llvm.parse_assembly(asm)

    def test_literal_struct(self):
        # Natural layout
        with self.check_parsing() as mod:

            type_name = "Type::Integer"

            integer = Class(mod, type_name, [Integer.as_llvm()])
            integer.create()
            typ_pointer = integer.type.as_pointer()

            intgr_create = f'{type_name}_Create'
            func = integer.add_function(intgr_create, [Integer.as_llvm()])

            entry_block = func.append_basic_block('entry')
            args = func.args
            constant = ir.Constant(typ_pointer, args[0].get_reference())
            indices = [ir.Constant(Integer.as_llvm(), 0), ir.Constant(Integer.as_llvm(), 0)]

            builder = Builder(entry_block)
            value = builder.gep(constant, indices)
            builder.store(args[1], value)

            builder.ret_void()

            intgr_getvalue = f'{type_name}_GetValue'
            func = integer.add_function(intgr_getvalue, ret=Integer.as_llvm())
            entry_block = func.append_basic_block('entry')

            builder = Builder(entry_block)
            value = builder.gep(constant, indices)
            address = builder.load(value)

            builder.ret(address)

            Builder(entry_block)

            main_ty = ir.FunctionType(Integer.as_llvm(), [])
            func = Function(mod, main_ty, 'main')
            entry_block = func.append_basic_block('entry')
            builder = Builder(entry_block)
            intgr = builder.alloca(integer.type, name="Int")
            builder.call(mod.get_global(intgr_create), [intgr, ir.Constant(Integer.as_llvm(), 234)])
            val = builder.call(mod.get_global(intgr_getvalue), [intgr])

            builder.ret(val)

            print(mod)


# class TestCustomTypes:
#     def test_works(self):
#         foo = LiteralStructType([Integer.as_llvm()])
#
#         str(foo).should.be.equal("%Foo = type { i32 }")