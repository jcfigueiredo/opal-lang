# AST hierarchy


from operator import eq
from typing import Iterable

from lark import InlineTransformer
from lark.lexer import Token

from opal import types
from opal.plugin import Plugin


# noinspection PyAbstractClass
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

    @property
    def statements(self):
        return self._statements

    def dump(self):
        stmts = '\n'.join([stmt.dump() for stmt in self._statements])

        s = f"({self.__class__.__name__}\n  {stmts})"
        return s


# noinspection PyAbstractClass
class ExprAST(ASTNode):
    pass


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


class If(ASTNode):

    def __init__(self, cond, then_, else_=None):
        self.cond = cond
        self.then_ = then_
        self.else_ = else_

    def dump(self):
        else_ = self.else_ and f' Else({self.else_.dump()})' or ''
        s = f'If({self.cond.dump()}) Then({self.then_.dump()})){else_}'
        return s


class While(ASTNode):

    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def dump(self):
        return f'While({self.cond.dump()}) {self.body.dump()}'


class For(ASTNode):

    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body

    def dump(self):
        return f'For({self.var.dump()} in {self.iterable.dump()}) {self.body.dump()}'


class Break(ASTNode):
    def dump(self):
        return 'Break'


class Continue(ASTNode):
    def dump(self):
        return 'Continue'


class Assign(BinaryOp):
    op = '='


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


# noinspection PyAbstractClass
class Value(ExprAST):
    val = None

    def __eq__(self, o):
        other_val = o.val if isinstance(o, Value) else o
        if not isinstance(o, Value):
            raise LogicError(f'You can\'t compare a Value and {o.__class__.__name__}.'
                             f'\nTokens being compared:\n{self.dump()}\n{other_val}')
        # noinspection PyUnresolvedReferences
        if self.__class__ != o.__class__:
            return False

        return self.val == o.val

    def dump(self):
        return f'({self.__class__.__name__} {self.val})'


class Print(Value, types.Any):

    def __init__(self, expr):
        self.val = expr

    def __eq__(self, o):
        return self.val == o.val

    def dump(self):
        return f'({self.__class__.__name__} {self.val.dump()})'


class Void(types.Any):
    pass


class Boolean(Value, types.Boolean):
    def __init__(self, val):
        self.val = bool(val)

    def dump(self):
        return f'({self.__class__.__name__} {str(self.val).lower()})'


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


class Var(Value):
    def __init__(self, val):
        self.val = val


class VarValue(Value):
    def __init__(self, val):
        self.val = val


class List(ASTNode, types.Vector):

    def __init__(self, items: Iterable[Value]):
        self._items = items

    @property
    def items(self):
        return self._items

    def dump(self):
        return "[{0}]".format(', '.join([item.dump() for item in self._items]))


class IndexOf(ASTNode):

    def dump(self):
        return f'(position {self.index.val} {self.lst.dump()})'

    def __init__(self, lst: List, index: Integer):
        self.lst = lst
        self.index = index


class Funktion(ASTNode):
    def __init__(self, name, params, body, ret_type=None, is_constructor=False):
        self.name = name
        self.params = params
        self.body = body
        self.ret_type = ret_type
        self.is_constructor = is_constructor

    def dump(self):
        args = ','.join([arg.dump() for arg in self.params])
        ret_type = self.ret_type and f'{self.ret_type} ' or ''
        name = '{0}{1}'.format(self.is_constructor and ':' or '', self.name)
        return f'({ret_type}{name}({args}) {self.body.dump()})'


class Klass(ASTNode):
    def __init__(self, name, body: Block, parent=None):
        self.name = name
        self.body = body
        self.parent = parent
        if name != 'Object' and not parent:
            self.parent = 'Object'
        self.functions = []

    def dump(self):
        return f'(class {self.name}{self.body.dump()})'

    def add_function(self, funktion: Funktion):
        self.functions.append(funktion)


class Param(ASTNode):
    def __init__(self, name, type_):
        self._name = name
        self._type = type_

    def dump(self):
        type_ = self.type and f'::{self.type}' or ''
        return f'{self.name}{type_}'

    @property
    def name(self):
        return self._name.val

    @property
    def type(self):
        return self._type


class Return(ASTNode):
    def __init__(self, val):
        self.val = val

    def dump(self):
        return f'(Return {self.val.dump()})'


class Call(ASTNode):

    def __init__(self, func, args):
        self.func = func

        if args is None:
            args = []

        self.args = args

    def dump(self):
        args = ', '.join([arg.dump() for arg in self.args])
        return f'{self.func}({args})'


class MethodCall(ASTNode):

    def __init__(self, instance, method, args):
        self.instance = instance
        self.method = method

        if args is None:
            args = []

        self.args = args

    def dump(self):
        args = ', '.join([arg.dump() for arg in self.args])
        return f'({self.instance}.{self.method} {args})'


# noinspection PyMethodMayBeStatic
class ASTVisitor(InlineTransformer):

    def __init__(self):
        self.classes = []
        self.functions = []
        super().__init__()

    def add_klass(self, klass):
        has_constructor = False

        for funktion in self.functions:
            has_constructor |= funktion.is_constructor
            klass.add_function(funktion)

        if not has_constructor:
            default_constructor = Funktion('init', params=[], body=Block(), is_constructor=True)
            klass.body.statements.append(default_constructor)
            klass.add_function(default_constructor)

        self.classes.append(klass)
        self.functions = []
        return klass

    def add_funktion(self, funktion):
        self.functions.append(funktion)

    def program(self, body: Block):
        program = Program(body)
        return program

    def block(self, *args):
        statements_excluding_token = [arg for arg in args if arg and not isinstance(arg, Token)]
        return Block(statements_excluding_token)

    def assign(self, lhs, rhs):
        return Assign(lhs, rhs)

    def break_(self):
        return Break()

    def continue_(self):
        return Continue()

    def name(self, id_):
        return Var(id_.value)

    def var(self, id_):
        return VarValue(id_.value)

    def print(self, expr):
        return Print(expr)

    def add(self, lhs, rhs):
        return Add(lhs, rhs)

    def sub(self, lhs, rhs):
        return Sub(lhs, rhs)

    def mul(self, lhs, rhs):
        return Mul(lhs, rhs)

    def div(self, lhs, rhs):
        return Div(lhs, rhs)

    def int(self, const):
        return Integer(const.value)

    def index(self, const):
        return const

    def float(self, const):
        return Float(const.value)

    def string(self, const):
        return String(const.value[1:-1])

    def list(self, *items):
        return List(items)

    def list_access(self, list_, index):
        return IndexOf(lst=list_, index=index)

    def boolean(self, const):
        return Boolean(const.value == 'true')

    def if_(self, cond, then_, else_=None):
        return If(cond, then_, else_)

    def while_(self, cond, body):
        return While(cond, body)

    def for_(self, var, iterable, body):
        return For(var, iterable, body)

    def class_(self, name, body):
        klass = Klass(name.val, body)
        klass = self.add_klass(klass)
        return klass

    def inherits(self, name, parent, body):
        klass = Klass(name.val, body, parent=parent.val)
        klass = self.add_klass(klass)
        return klass

    def def_(self, name, params, body=None):
        if isinstance(params, Block):
            body = params
            params = []
        funktion = Funktion(name.val, params, body)
        self.add_funktion(funktion)
        return funktion

    def ctor_(self, name, params, body=None):
        if isinstance(params, Block):
            body = params
            params = []
        funktion = Funktion(name.val, params, body, is_constructor=True)
        self.add_funktion(funktion)
        return funktion

    def typed_def(self, type_, name, params, body=None):
        funktion = Funktion(name.val, params, body, ret_type=type_.value)
        self.add_funktion(funktion)
        return funktion

    def params(self, *nodes):
        return [node for node in nodes if isinstance(node, Param)]

    def param(self, name, type_=None):
        return Param(name, type_ and type_.value)

    def ret_(self, val):
        return Return(val)

    def instance(self, func, args=None):
        return Call(func.val, args)

    def method_call(self, instance, method, args=None):
        return MethodCall(instance.val, method.val, args)

    def args(self, *args):
        args_without_tokens = [arg for arg in args if not isinstance(arg, Token)]
        return args_without_tokens

    def arg(self, arg):
        return arg

    def comp(self, lhs, op, rhs):
        node = Comparison.by(op.value)

        if not node:  # pragma: no cover
            raise SyntaxError(f'The operation [{op}] is not supported.')  # pragma: no cover
        return node(lhs, rhs)
