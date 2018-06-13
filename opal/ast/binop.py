from opal.ast import ASTNode, LogicError, Value
from opal.ast.types import String, List, Call
from opal.plugin import Plugin


class BinaryOp(ASTNode, metaclass=Plugin):
    op = None

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


class Arithmetic(BinaryOp):
    pass


class Mul(Arithmetic):
    op = '*'


class Div(Arithmetic):
    op = '/'


class Add(Arithmetic):
    op = '+'


class Sub(Arithmetic):
    op = '-'


class Comparison(BinaryOp):
    pass


class GreaterThan(Comparison):
    op = '>'


class GreaterThanEqual(Comparison):
    op = '>='


class LessThan(Comparison):
    op = '<'


class LessThanEqual(Comparison):
    op = '<='


class Equals(Comparison):
    op = '=='


class Unequals(Comparison):
    op = '!='