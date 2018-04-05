from llvmlite import ir

from opal.ast import Boolean

PLUS = '+'
MINUS = '-'
MUL = '*'
DIV = '/'  # TODO: Change it to floordiv
GREATER_THAN = '>'
LESS_THAN = '<'


def int_ops(builder, left, right, node):
    op = node.op
    if op == PLUS:
        return builder.add(left, right, 'addtmp')
    elif op == MINUS:
        return builder.sub(left, right, 'subtmp')
    elif op == MUL:
        return builder.mul(left, right, 'multmp')
    elif op == DIV:
        return builder.sdiv(left, right, 'divtmp')
    elif op in [GREATER_THAN, LESS_THAN]:
        return builder.icmp_signed(op, left, right, 'booltmp')

    raise SyntaxError('Unknown binary operator', op)


def float_ops(builder, left, right, node):
    op = node.op
    if op == PLUS:
        return builder.fadd(left, right, 'faddtmp')
    elif op == MINUS:
        return builder.fsub(left, right, 'fsubtmp')
    elif op == MUL:
        return builder.fmul(left, right, 'fmultmp')
    elif op == DIV:
        return builder.udiv(builder.fptosi(left, ir.IntType(64)),
                            builder.fptosi(right, ir.IntType(64)), 'ffloordivtmp')
    elif op in [GREATER_THAN, LESS_THAN]:
        return builder.fcmp_ordered(op, left, right, 'booltmp')

    raise SyntaxError('Unknown binary operator', op)
