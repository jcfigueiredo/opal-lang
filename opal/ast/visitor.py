# AST hierarchy


from lark import InlineTransformer
from lark.lexer import Token

from opal.ast.binop import Assign, Comparison, Mul, Div, Add, Sub
from opal.ast.conditionals import If
from opal.ast.iterators import IndexOf, While, For
from opal.ast.program import Program, Block
from opal.ast.statements import Print
from opal.ast.terminals import Continue, Break, Return
from opal.ast.types import Bool, Integer, List, Float, String, Klass, Funktion, Param, Call, MethodCall
from opal.ast.vars import Var, VarValue


# noinspection PyMethodMayBeStatic
class ASTVisitor(InlineTransformer):
    def __init__(self):
        self.classes = []
        self.functions = []
        self.ret_val = None
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
        funktion.ret_type = funktion.ret_type or self.ret_val
        self.functions.append(funktion)
        self.ret_val = None

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
        return Bool(const.value == 'true')

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
        ret_val = Return(val)
        self.ret_val = ret_val
        return ret_val

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


