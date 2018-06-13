from llvmlite import ir
from llvmlite.ir import PointerType

from opal.ast import Value
from opal.ast.types import Int8, Any, Bool, Integer, Float, String
from opal.ast.vars import VarValue

INDICES = [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]


class Print(Value, Any):

    def __init__(self, expr):
        self.val = expr

    def __eq__(self, o):
        return self.val == o.val

    def dump(self):
        return f'({self.__class__.__name__} {self.val.dump()})'
    
    def code(self, codegen):
        val = codegen.visit(self.val)
        typ = None
        if isinstance(self.val, VarValue):
            typ = codegen.typetab[self.val.val]

        if isinstance(self.val, String) or isinstance(typ, PointerType):
            typ = String
        elif isinstance(self.val, Integer) or val.type is Integer.as_llvm():
            typ = Integer
        elif isinstance(self.val, Float) or val.type is Float.as_llvm():
            typ = Float
        elif isinstance(self.val, Bool) or val.type is Bool.as_llvm():
            typ = Bool

        if typ is String:
            # Cast to a i8* pointer
            char_ty = val.type.pointee.element
            str_ptr = codegen.bitcast(val, char_ty.as_pointer())

            codegen.call('puts', [str_ptr])
            return

        if typ is Integer:
            number = codegen.alloc_and_store(val, val.type)
            number_ptr = codegen.load(number)

            buffer = codegen.alloc(ir.ArrayType(Int8.as_llvm(), 10))

            buffer_ptr = codegen.gep(buffer, INDICES, inbounds=True)

            codegen.call('int_to_string', [number_ptr, buffer_ptr, (codegen.const(10))])

            codegen.call('puts', [buffer_ptr])
            return

        if typ is Float:
            percent_g = String('%g\n').code(codegen)
            percent_g = codegen.gep(percent_g, INDICES)

            value = percent_g
            type_ = Int8.as_llvm().as_pointer()
            percent_g = codegen.bitcast(value, type_)
            codegen.call('printf', [percent_g, val])
            return

        if typ is Bool:
            mod = codegen.module
            true = codegen.insert_const_string(mod, 'true')
            true = codegen.gep(true, INDICES)
            false = codegen.insert_const_string(mod, 'false')
            false = codegen.gep(false, INDICES)

            if hasattr(val, 'constant'):
                if val.constant:
                    val = true
                else:
                    val = false
            else:
                val = codegen.select(val, true, false)

            codegen.call('printf', [val])

            return

        raise NotImplementedError(f'can\'t print {self.val}')