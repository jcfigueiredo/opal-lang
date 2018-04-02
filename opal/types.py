import llvmlite.ir as ir

INT = 'Int'


class MetaType(type):
    _llvm_type = None
    #
    # @property
    # def name(self):
    #     return self.__class__.__name__

    @property
    def as_llvm(self):
        return self._llvm_type


class Any(metaclass=MetaType):
    _llvm_type = ir.VoidType()


class Int8(Any):
    _llvm_type = ir.IntType(8)


class Int(Any):
    _llvm_type = ir.IntType(32)


class Float(Any):
    _llvm_type = ir.DoubleType()


class String(Any):
    _llvm_type = ir.IntType(8).as_pointer

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
