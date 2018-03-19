# AST hierarchy


# noinspection PyAbstractClass
from operator import eq
from opal import types


class LogicError(Exception):
    pass


class ASTNode:
    def dump(self):
        raise NotImplementedError


# noinspection PyAbstractClass
class Program(ASTNode):

    def __init__(self, block=None):
        self.block = block and block or Block()

    def __eq__(self, o):
        return self.block.__eq__(o.block)

    def dump(self):
        s = f"({self.__class__.__name__}\n  {self.block.dump()})"
        return s


class Block(ASTNode):

    def __init__(self, body=None):
        if isinstance(body, list):
            self._statements = body
            return

        self._statements = []
        if body:
            self._statements.append(body)

    def __eq__(self, o):
        return any(map(eq, self.statements, o.statements))

    def add_statement(self, statement):
        self._statements.insert(0, statement)

    @property
    def statements(self):
        return self._statements

    def dump(self):
        stmts = '\n'.join([stmt.dump() for stmt in self._statements])

        s = f"({self.__class__.__name__}\n  {stmts})"
        return s


# # noinspection PyAbstractClass
# class Function(ASTNode):
#     def __init__(self, proto, body):
#         self.proto = proto
#         self.body = body
#
#     _anonymous_function_counter = 0
#
#     @classmethod
#     def create_anonymous(cls, expr):
#         """Create an anonymous function to hold an expression."""
#         cls._anonymous_function_counter += 1
#         return cls(Prototype(f'_anon{cls._anonymous_function_counter}'), expr)
#
#     def is_anonymous(self):
#         return self.proto.name.startswith('_anon')
#
#
# class Prototype(ASTNode):
#
#     def __init__(self, name):
#         self.name = name
#
#     @property
#     def dump(self):
#         return f'({self.__class__.__name__} {self.name})'


# noinspection PyAbstractClass
class ExprAST(ASTNode):
    pass


class BinaryOp(ASTNode):
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
        return f'({self.op} {left} {right})'


class Mul(BinaryOp):
    op = '*'


class Div(BinaryOp):
    op = '/'


class Add(BinaryOp):
    op = '+'


class Sub(BinaryOp):
    op = '-'


# noinspection PyAbstractClass
class Value(ExprAST):
    val = None

    def __eq__(self, o):
        other_val = o.val if isinstance(o, Value) else o
        if not isinstance(o, Value):
            raise LogicError(f'You can\'t compare a Value and {o.__class__.__name__}.'
                             f'\nTokens being compared:\n{self.dump()}\n{other_val}')
        # noinspection PyUnresolvedReferences
        return self.val == o.val

    def dump(self):
        return f'({self.__class__.__name__} {self.val})'


class Void(types.Any):
    pass


class Integer(Value, types.Int):
    def __init__(self, val):
        self.val = int(val)


class Int8(Value, types.Int8):
    def __init__(self, val):
        self.val = int(val)


class Float(Value, types.Float):
    def __init__(self, val):
        self.val = float(val)


class String(Value, types.String):
    def __init__(self, val):
        self.val = val
