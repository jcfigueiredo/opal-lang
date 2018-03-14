from llvmlite import ir as ir

from opal import types
from opal.ast import Program, Value, BinaryOp


# noinspection PyPep8Naming
class LLVMCodeGenerator:
    def __init__(self):
        self.module = ir.Module()
        self.blocks = []
        # Current IR builder.
        self.builder = ir.IRBuilder()

        # self.func_symtab = {}

    def generate_code(self, node):
        assert isinstance(node, Program)
        return self._codegen(node)

    def _codegen(self, node):
        """
        Dynamically invoke the code generator for each specific node
        :param node: ASTNode
        """

        if isinstance(node, Value):
            return self._codegen_Value(node)

        if isinstance(node, BinaryOp):
            return self._codegen_Binop(node)

        method = '_codegen_' + node.__class__.__name__

        return getattr(self, method)(node)

    def _codegen_Binop(self, node):
        left = self._codegen(node.lhs)
        right = self._codegen(node.rhs)

        ops = {
            '+': 'addtmp',
            '-': 'subtmp',
            '*': 'multmp',
            '/': 'sdivtmp',
        }

        op = node.op
        op_alias = ops.get(op)

        if op not in ops:
            raise NotImplementedError(f'The operation _{op}_ is nor support for Binary Operations.')
        return self.builder.add(left, right, op_alias)

    # noinspection PyMethodMayBeStatic
    def _codegen_Block(self, node):
        ret = None
        for stmt in node.statements:
            temp = self._codegen(stmt)
            if temp:
                ret = temp
        return ret

    def _codegen_Program(self, node):
        func_type = ir.FunctionType(types.Int.as_llvm, [])

        func = ir.Function(self.module, func_type, name='main')

        bb_entry = func.append_basic_block('entry')

        self.builder.position_at_end(bb_entry)
        self.blocks.append(bb_entry)

        self._codegen(node.block)

        result_alloc = self.builder.alloca(types.Int.as_llvm, name='result')
        self.builder.store(ir.Constant(result_alloc.type.pointee, 0), result_alloc)
        result = self.builder.load(result_alloc, 'result')

        self.builder.ret(result)

    # noinspection PyMethodMayBeStatic
    def _codegen_Value(self, node):
        return ir.Constant(node.__class__.as_llvm, node.val)
