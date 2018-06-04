from llvmlite import ir

from opal.ast.core import Add, Sub, Mul, Div, Comparison


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
