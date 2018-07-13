from llvmlite import ir

from opal.ast import ASTNode, LogicError, Value
from opal.ast.types import String, List, Call, Integer
from opal.plugin import Plugin


class BinaryOp(ASTNode, metaclass=Plugin):
    op = None
    alias = None

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, o):
        if not isinstance(o, BinaryOp):
            raise LogicError(f'You can\'t compare a BinaryOp and {o.__class__.__name__}.'
                             f'\nTokens being compared:\n{self.dump()}\n{o.dump}')
        # noinspection PyUnresolvedReferences
        return self.lhs == o.lhs and self.rhs == o.rhs

    def dump(self):
        left = self.lhs.val if isinstance(self.lhs, Value) else self.lhs.dump()
        right = self.rhs.val if isinstance(self.rhs, Value) else self.rhs.dump()
        if isinstance(self.lhs, String):
            left = f'"{left}"'
        if isinstance(self.rhs, String):
            right = f'"{right}"'
        return f'({self.op} {left} {right})'

    def code(self, codegen):
        lhs = self.lhs
        rhs = self.rhs

        left = codegen.visit(lhs)
        right = codegen.visit(rhs)

        if left.type == Integer.as_llvm() and right.type == Integer.as_llvm():
            return int_ops(codegen.builder, left, right, self)
        return float_ops(codegen.builder, left, right, self)


class Assign(BinaryOp):
    op = '='

    def code(self, codegen):
        left = codegen.visit(self.lhs)
        rhs = self.rhs
        value = codegen.visit(rhs)

        name = left.val

        if isinstance(rhs, String):
            typ = value.type
        elif isinstance(rhs, List):
            typ = List.as_llvm().as_pointer()
        elif isinstance(rhs, Call):
            typ = codegen.get_klass_by_name(rhs.func)
            return codegen.assign(name, value, typ, is_class=True)
        elif not isinstance(rhs, Value):
            value = codegen.visit(rhs)
            typ = value.type
        else:
            typ = rhs.as_llvm()

        var_address = codegen.assign(name, value, typ)
        return var_address


class Comparison(BinaryOp):
    pass


class GreaterThan(Comparison):
    op = '>'
    alias = 'gt'


class GreaterThanEqual(Comparison):
    op = '>='
    alias = 'gte'


class LessThan(Comparison):
    op = '<'
    alias = 'lt'


class LessThanEqual(Comparison):
    op = '<='
    alias = 'lte'


class Equals(Comparison):
    op = '=='
    alias = 'eq'


class Unequals(Comparison):
    op = '!='
    alias = 'neq'


class Arithmetic(BinaryOp):
    pass


class Mul(Arithmetic):
    op = '*'
    alias = 'mul'


class Div(Arithmetic):
    op = '/'
    alias = 'div'


class Add(Arithmetic):
    op = '+'
    alias = 'add'


class Sub(Arithmetic):
    op = '-'
    alias = 'sub'


# temporary
def int_ops(builder, left, right, node):
    op = node.op

    if isinstance(node, Add):
        return builder.add(left, right, 'addtmp')
    elif isinstance(node, Sub):
        return builder.sub(left, right, 'subtmp')
    elif isinstance(node, Mul):
        return builder.mul(left, right, 'multmp')
    elif isinstance(node, Div):
        return builder.sdiv(left, right, 'divtmp')
    elif isinstance(node, Comparison):
        return builder.icmp_signed(op, left, right, 'booltmp')

    # it should never get to this point since grammar doesn't allow for it
    raise SyntaxError('Unknown operator', op)  # pragma: no cover


def float_ops(builder, left, right, node):
    op = node.op

    if isinstance(node, Add):
        return builder.fadd(left, right, 'faddtmp')
    elif isinstance(node, Sub):
        return builder.fsub(left, right, 'fsubtmp')
    elif isinstance(node, Mul):
        return builder.fmul(left, right, 'fmultmp')
    elif isinstance(node, Div):
        return builder.udiv(builder.fptosi(left, ir.IntType(64)),
                            builder.fptosi(right, ir.IntType(64)), 'ffloordivtmp')
    elif isinstance(node, Comparison):
        return builder.fcmp_ordered(op, left, right, 'booltmp')

    # it should never get to this point since grammar doesn't allow for it
    raise SyntaxError('Unknown operator', op)  # pragma: no cover

