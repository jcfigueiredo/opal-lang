from llvmlite import ir

from opal.ast import Add, Sub, Mul, Div, GreaterThan, LessThan, Equals

PLUS = '+'
MINUS = '-'
MUL = '*'
DIV = '/'  # TODO: Change it to floordiv
GREATER_THAN = '>'
LESS_THAN = '<'
EQUALS = '=='


def int_ops(builder, left, right, node):
    op = node.op
    if op == Add.op:
        return builder.add(left, right, 'addtmp')
    elif op == Sub.op:
        return builder.sub(left, right, 'subtmp')
    elif op == Mul.op:
        return builder.mul(left, right, 'multmp')
    elif op == Div.op:
        return builder.sdiv(left, right, 'divtmp')
    elif op in [GreaterThan.op, LessThan.op, Equals.op]:
        return builder.icmp_signed(op, left, right, 'booltmp')

    raise SyntaxError('Unknown binary operator', op)


def float_ops(builder, left, right, node):
    op = node.op
    if op == Add.op:
        return builder.fadd(left, right, 'faddtmp')
    elif op == Sub.op:
        return builder.fsub(left, right, 'fsubtmp')
    elif op == Mul.op:
        return builder.fmul(left, right, 'fmultmp')
    elif op == Div.op:
        return builder.udiv(builder.fptosi(left, ir.IntType(64)),
                            builder.fptosi(right, ir.IntType(64)), 'ffloordivtmp')
    elif op in [GreaterThan.op, LessThan.op, Equals.op]:
        return builder.fcmp_ordered(op, left, right, 'booltmp')

    raise SyntaxError('Unknown binary operator', op)
