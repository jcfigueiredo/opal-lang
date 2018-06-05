import llvmlite.ir as ir

from opal.ast import Value

INT = 'Int'


class Any:
    _llvm_type = ir.VoidType()

    @classmethod
    def as_llvm(cls):
        return cls._llvm_type


class Int8(Any):
    _llvm_type = ir.IntType(8)


class Int(Any):
    _llvm_type = ir.IntType(32)


# TODO: make it decimal? https://docs.python.org/3/library/decimal.html
class Float(Any):
    _llvm_type = ir.DoubleType()


class String(Any):
    _llvm_type = ir.IntType(8).as_pointer


class Vector(Any):
    _llvm_type = ir.LiteralStructType([Int.as_llvm(), Int.as_llvm(), Int8.as_llvm().as_pointer().as_pointer()])


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

class Bool(Any, Value):
    _llvm_type = ir.IntType(1)

    def __init__(self, val):
        self.val = bool(val)

    def dump(self):
        return f'({self.__class__.__name__} {str(self.val).lower()})'
