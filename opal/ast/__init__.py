class ASTNode:

    def dump(self):
        raise NotImplementedError

    def accept(self, visitor):
        visitor.visit(self)


# noinspection PyAbstractClass
class ExprAST(ASTNode):
    pass


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


class LogicError(Exception):
    pass
